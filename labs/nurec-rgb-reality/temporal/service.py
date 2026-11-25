"""Optional loopback GPU enhancer with matched baseline and accelerated profiles."""
from __future__ import annotations
import argparse,base64,hashlib,collections,concurrent.futures,io,json,math,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import numpy as np
from PIL import Image,UnidentifiedImageError
import torch
from context import reset_reasons
from fast import CurrentFrame,set_layout
from wire import encode_preview
from adaptive import plan,bootstrap_slots,validate_input_size

class Engine:
    def __init__(self,checkpoint,components,record_root=None):
        import pix2pix_turbo_harmonizer as upstream
        from standalone import prepare,patch_config,verify_parameters
        paths,self.provenance=prepare(checkpoint,components);patch_config(upstream,paths)
        torch.manual_seed(42);torch.set_num_threads(8)
        self.model=upstream.Pix2Pix_Turbo(pretrained_path=str(checkpoint),timestep=250,train_full_unet=True,freeze_vae=False,vae_skip_connection=False,use_sched=False,device='cuda',dtype=torch.bfloat16)
        self.provenance.update(verify_parameters(self.model,checkpoint));self.model.set_eval();self.model.to(device='cuda',dtype=torch.bfloat16)
        self.fast=CurrentFrame(self.model);self.tuned=False
        self.lock=threading.Lock();self.sessions=collections.OrderedDict();self.record_root=record_root;self.sequence=0
        self.writer=concurrent.futures.ThreadPoolExecutor(max_workers=1,thread_name_prefix='preview-record') if record_root else None
        self.record_slots=threading.BoundedSemaphore(3)
        if record_root:
            record_root.mkdir(parents=True,exist_ok=True)
            self.sequence=max([int(p.name.split('.')[0]) for p in record_root.iterdir() if p.is_file() and p.name.split('.')[0].isascii() and p.name.split('.')[0].isdecimal()]+[0])
    @staticmethod
    def image_tensor(image,size=(1024,576)):
        return torch.from_numpy(np.array(image.resize(size,Image.Resampling.BILINEAR),copy=True)).permute(2,0,1)[None].to(device='cuda',dtype=torch.bfloat16)/127.5-1
    def warmup(self):
        with torch.inference_mode():
            x=torch.zeros((1,3,1,576,1024),device='cuda',dtype=torch.bfloat16)
            self.model(x);self.fast(x.expand(-1,-1,5,-1,-1).contiguous());
            small=torch.zeros((1,3,5,288,512),device='cuda',dtype=torch.bfloat16);self.fast(small);self.fast(small[:,:,:1]);torch.cuda.synchronize()
    def save_record(self,prefix,image,result,receipt,level):
        image.save(prefix.with_suffix('.input.png'),compress_level=level);result.save(prefix.with_suffix('.output.png'),compress_level=level);prefix.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
    def deferred_record(self,*args):
        try:self.save_record(*args)
        except Exception:print('LOCAL_RECORDING_WRITE_FAILED',flush=True)
        finally:self.record_slots.release()
    def infer(self,request):
        begin=time.perf_counter()
        if not isinstance(request,dict):raise ValueError('JSON object required')
        session=request.get('session','');mode=request.get('mode','temporal');profile=request.get('execution','exact');info=request.get('view',{})
        if not isinstance(info,dict):raise ValueError('View metadata object required')
        if not isinstance(session,str) or not session or len(session)>64 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in session):raise ValueError('Invalid local session identifier')
        if mode not in ['independent','temporal'] or profile not in ['baseline','exact','tuned','adaptive']:raise ValueError('Unsupported preview profile')
        try:raw=base64.b64decode(request['image'],validate=True)
        except Exception:raise ValueError('Expected base64 PNG or JPEG image') from None
        if len(raw)>2500000:raise ValueError('Image exceeds local preview limit')
        image=Image.open(io.BytesIO(raw));w,h=image.size
        if w*h>2100000 or w<256 or h<144 or w*9!=h*16:raise ValueError('Use a16:9 image of at most2.1megapixels')
        image=image.convert('RGB')
        for name in ['camera','forward']:
            vector=info.get(name)
            if not isinstance(vector,list) or len(vector)!=3 or not all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in vector):raise ValueError('Supply finite camera and forward three-vectors')
        if np.linalg.norm(info['forward'])<1e-6 or type(info.get('frame')) is not int:raise ValueError('Invalid view direction or frame index')
        phase=request.get('phase');bank,size=plan(profile,phase);width,height=size
        validate_input_size(profile,phase,image.size)
        decoded=time.perf_counter()
        with self.lock:
            acquired=time.perf_counter();banks=self.sessions.pop(session,{})
            if request.get('reset'):banks={}
            previous=banks.get(bank,{'history':[],'tensors':[],'view':None,'mode':mode,'execution':profile})
            history=previous['history'];cached=previous['tensors'];reset=bool(request.get('reset')) or previous['mode']!=mode or previous['execution']!=profile
            reasons=reset_reasons(previous['view'],info);reset|=bool(reasons)
            if reset:history=[];cached=[]
            if self.tuned!=(profile=='tuned'):
                set_layout(self.model,'tuned' if profile=='tuned' else 'exact');self.tuned=profile=='tuned'
            refs=[]
            if mode=='temporal' and len(history)>=4:
                refs=[self.image_tensor(p,size) for p in history[-1:-5:-1]] if profile=='baseline' else cached[-1:-5:-1]
            current=self.image_tensor(image,size);slots=bootstrap_slots(len(history),mode,phase);bootstrap_ms=0.0
            if slots:
                torch.cuda.synchronize();warm=time.perf_counter()
                with torch.inference_mode():first=self.fast(current[:,:,None])
                torch.cuda.synchronize();bootstrap_ms=(time.perf_counter()-warm)*1000
                if tuple(first.shape)!=(1,3,1,height,width) or not torch.isfinite(first).all():raise RuntimeError('Invalid stationary warm start')
                warm_rgb=((first[0,:,0].float().permute(1,2,0).cpu().numpy()+1)*127.5).clip(0,255).astype(np.uint8)
                warm_image=Image.fromarray(warm_rgb);warm_tensor=self.image_tensor(warm_image,size)
                history=[warm_image]*slots;cached=[warm_tensor]*slots;refs=cached[::-1]
            x=torch.stack([current,*refs],dim=2)
            torch.cuda.synchronize();prepared=time.perf_counter()
            with torch.inference_mode():y=self.model(x) if profile=='baseline' else self.fast(x)
            torch.cuda.synchronize();finished=time.perf_counter();seconds=finished-prepared
            expected=(1,3,len(refs)+1 if profile=='baseline' else 1,height,width)
            if tuple(y.shape)!=expected or not torch.isfinite(y).all():raise RuntimeError('Invalid enhanced output')
            rgb=((y[0,:,0].float().permute(1,2,0).cpu().numpy()+1)*127.5).clip(0,255).astype(np.uint8)
            result=Image.fromarray(rgb);level=6 if profile=='baseline' else 1;mime,payload=encode_preview(result,profile);encoded=base64.b64encode(payload).decode();encoded_at=time.perf_counter()
            tensors=[*cached,self.image_tensor(result,size)][-4:] if profile!='baseline' else []
            banks[bank]={'history':[*history,result][-4:],'tensors':tensors,'view':info,'mode':mode,'execution':profile}
            self.sessions[session]=banks
            while len(self.sessions)>2:self.sessions.popitem(last=False)
            self.sequence+=1
            receipt={'sequence':self.sequence,'mode':mode,'execution':profile,'history_frames':len(refs),'history_reset':bool(reset),'reset_reasons':reasons,'model_ms':seconds*1000+bootstrap_ms,'final_forward_ms':seconds*1000,'bootstrap_ms':bootstrap_ms,'model_calls':2 if slots else 1,'reused_reference_slots':slots,'history_bank':bank,'phase':phase or 'continuous','hq_uses_preview_history':False,'view':info,'resolution':[width,height],'rgb_sha256':hashlib.sha256(rgb.tobytes()).hexdigest(),'image_mime':mime,'image_bytes':len(payload),'checkpoint_sha256':self.provenance['checkpoint_sha256'],'timings':{'request_decode_ms':(decoded-begin)*1000,'queue_ms':(acquired-decoded)*1000,'prepare_ms':(prepared-acquired)*1000-bootstrap_ms,'output_encode_ms':(encoded_at-finished)*1000},'scope':'Generated enhancement of a captured offline3D reconstruction; no driving control or unseen-view ground truth'}
            if self.record_root:
                prefix=self.record_root/f'{self.sequence:06d}'
                if profile=='baseline':self.save_record(prefix,image,result,receipt,level);receipt['recording']='inline'
                elif self.record_slots.acquire(blocking=False):
                    receipt['recording']='deferred';self.writer.submit(self.deferred_record,prefix,image,result,dict(receipt),level)
                else:receipt['recording']='skipped_busy'
            receipt['server_total_ms']=(time.perf_counter()-begin)*1000
            return {'image':encoded,**receipt}

def handler(engine):
    class Handler(BaseHTTPRequestHandler):
        def reply(self,status,value):
            raw=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if self.path!='/health':self.reply(404,{'error':'Unknown endpoint'});return
            self.reply(200,{'ready':True,'model':'nvidia/Harmonizer','learned_parameters_verified':self.engine.provenance['all_learned_parameters_equal_released_tensors'],'modes':['independent','temporal'],'execution':['baseline','exact','tuned','adaptive'],'adaptive_preview_size':[512,288],'adaptive_hq_size':[1024,576]})
        def do_POST(self):
            if self.path!='/infer':self.reply(404,{'error':'Unknown endpoint'});return
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':self.reply(415,{'error':'JSON required'});return
            if self.headers.get('Origin'):self.reply(403,{'error':'Use the same-origin local viewer proxy'});return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=3500000:raise ValueError('Request size limit exceeded')
                value=json.loads(self.rfile.read(length));result=self.engine.infer(value)
            except (ValueError,KeyError,TypeError,UnidentifiedImageError,Image.DecompressionBombError):self.reply(400,{'error':'Invalid preview request'});return
            except Exception:self.reply(500,{'error':'GPU enhancement failed; inspect the private service log'});raise
            self.reply(200,result)
        def log_message(self,*args):pass
    Handler.engine=engine;return Handler

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--components',type=Path,required=True);p.add_argument('--port',type=int,default=8765);p.add_argument('--record-root',type=Path);a=p.parse_args()
    engine=Engine(a.checkpoint,a.components,a.record_root);engine.warmup();print('LOCAL_ENHANCER_READY',a.port,flush=True);ThreadingHTTPServer(('127.0.0.1',a.port),handler(engine)).serve_forever()
if __name__=='__main__':main()
