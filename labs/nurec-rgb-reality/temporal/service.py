"""Optional loopback GPU image enhancer; no workspace or model downloads API."""
from __future__ import annotations
import argparse,base64,collections,io,json,math,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import numpy as np
from PIL import Image,UnidentifiedImageError
import torch
from context import reset_reasons

class Engine:
    def __init__(self,checkpoint,components,record_root=None):
        import pix2pix_turbo_harmonizer as upstream
        from standalone import prepare,patch_config,verify_parameters
        paths,self.provenance=prepare(checkpoint,components);patch_config(upstream,paths)
        torch.manual_seed(42);torch.set_num_threads(8)
        self.model=upstream.Pix2Pix_Turbo(pretrained_path=str(checkpoint),timestep=250,train_full_unet=True,freeze_vae=False,vae_skip_connection=False,use_sched=False,device='cuda',dtype=torch.bfloat16)
        self.provenance.update(verify_parameters(self.model,checkpoint));self.model.set_eval();self.model.to(device='cuda',dtype=torch.bfloat16)
        self.lock=threading.Lock();self.sessions=collections.OrderedDict();self.record_root=record_root;self.sequence=0
        if record_root:record_root.mkdir(parents=True,exist_ok=True)
    @staticmethod
    def image_tensor(image):
        return torch.from_numpy(np.array(image.resize((1024,576),Image.Resampling.BILINEAR),copy=True)).permute(2,0,1)[None].to(device='cuda',dtype=torch.bfloat16)/127.5-1
    def infer(self,request):
        if not isinstance(request,dict):raise ValueError('JSON object required')
        session=request.get('session','');mode=request.get('mode','temporal');info=request.get('view',{})
        if not isinstance(info,dict):raise ValueError('View metadata object required')
        if not session or len(session)>64 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in session):raise ValueError('Invalid local session identifier')
        if mode not in ['independent','temporal']:raise ValueError('Unsupported enhancement mode')
        try:raw=base64.b64decode(request['image'],validate=True)
        except Exception:raise ValueError('Expected base64 PNG or JPEG image') from None
        if len(raw)>2500000:raise ValueError('Image exceeds local preview limit')
        image=Image.open(io.BytesIO(raw));w,h=image.size
        if w*h>2100000 or w<256 or h<144 or w*9!=h*16:raise ValueError('Use a16:9 image of at most2.1megapixels')
        image=image.convert('RGB')
        numeric=[*info.get('camera',[]),*info.get('forward',[])]
        if len(numeric)!=6 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in numeric):raise ValueError('Supply finite camera and forward three-vectors')
        if np.linalg.norm(info['forward'])<1e-6 or not isinstance(info.get('frame'),int):raise ValueError('Invalid view direction or frame index')
        with self.lock:
            previous=self.sessions.pop(session,{'history':[],'view':None,'mode':mode});history=previous['history'];reset=bool(request.get('reset')) or previous['mode']!=mode
            reasons=reset_reasons(previous['view'],info);reset|=bool(reasons)
            if reset:history=[]
            refs=[self.image_tensor(p) for p in history[-1:-5:-1]] if mode=='temporal' and len(history)>=4 else []
            x=torch.stack([self.image_tensor(image),*refs],dim=2)
            torch.cuda.synchronize();start=time.perf_counter()
            with torch.inference_mode():y=self.model(x)
            torch.cuda.synchronize();seconds=time.perf_counter()-start
            if tuple(y.shape)!=(1,3,len(refs)+1,576,1024) or not torch.isfinite(y).all():raise RuntimeError('Invalid enhanced output')
            rgb=((y[0,:,0].float().permute(1,2,0).cpu().numpy()+1)*127.5).clip(0,255).astype(np.uint8);result=Image.fromarray(rgb);buffer=io.BytesIO();result.save(buffer,format='PNG');encoded=base64.b64encode(buffer.getvalue()).decode()
            self.sessions[session]={'history':[*history,result][-4:],'view':info,'mode':mode}
            while len(self.sessions)>2:self.sessions.popitem(last=False)
            self.sequence+=1
            receipt={'sequence':self.sequence,'mode':mode,'history_frames':len(refs),'history_reset':bool(reset),'reset_reasons':reasons,'model_ms':seconds*1000,'view':info,'resolution':[1024,576],'checkpoint_sha256':self.provenance['checkpoint_sha256'],'scope':'Generated enhancement of a captured offline3D reconstruction; no driving control or unseen-view ground truth'}
            if self.record_root:
                prefix=self.record_root/f'{self.sequence:06d}';image.save(prefix.with_suffix('.input.png'));result.save(prefix.with_suffix('.output.png'));prefix.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
            return {'image':encoded,**receipt}

def handler(engine):
    class Handler(BaseHTTPRequestHandler):
        def reply(self,status,value):
            raw=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if self.path!='/health':self.reply(404,{'error':'Unknown endpoint'});return
            self.reply(200,{'ready':True,'model':'nvidia/Harmonizer','learned_parameters_verified':self.engine.provenance['all_learned_parameters_equal_released_tensors'],'modes':['independent','temporal']})
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
    engine=Engine(a.checkpoint,a.components,a.record_root);print('LOCAL_ENHANCER_READY',a.port,flush=True);ThreadingHTTPServer(('127.0.0.1',a.port),handler(engine)).serve_forever()
if __name__=='__main__':main()
