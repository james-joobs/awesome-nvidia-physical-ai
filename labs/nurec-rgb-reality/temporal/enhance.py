"""Matched V=1 / V=5 inference with the official temporal Harmonizer model.

Launch in the pinned official Cosmos environment, from its src directory.
The original render and generated output remain separate. This is an image
enhancer, not Tesla UVE, a driving policy, or a reconstruction ground truth.
"""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from PIL import Image
import torch

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--mode',choices=['temporal','independent'],required=True);p.add_argument('--standalone-components',type=Path);p.add_argument('--cut-frames',default='');p.add_argument('--max-frames',type=int);a=p.parse_args()
    import pix2pix_turbo_harmonizer as upstream
    standalone=None
    if a.standalone_components:
        from standalone import prepare,patch_config
        paths,standalone=prepare(a.checkpoint,a.standalone_components);patch_config(upstream,paths)
    if a.out.exists() and any(a.out.iterdir()):raise ValueError('Choose a fresh output folder; autoregressive outputs cannot be silently reused')
    files=sorted(p for p in a.input.iterdir() if p.suffix.lower() in ['.jpg','.png','.jpeg'])
    if a.max_frames:files=files[:a.max_frames]
    if not files:raise ValueError('No input frames')
    cuts={0,*[int(x) for x in a.cut_frames.split(',') if x]}
    if min(cuts)<0 or max(cuts)>=len(files):raise ValueError('Cut indices must belong to the selected frame range')
    a.out.mkdir(parents=True);torch.manual_seed(42);torch.set_num_threads(8)
    model=upstream.Pix2Pix_Turbo(pretrained_path=str(a.checkpoint),timestep=250,train_full_unet=True,freeze_vae=False,vae_skip_connection=False,use_sched=False,device='cuda',dtype=torch.bfloat16)
    if standalone is not None:
        from standalone import verify_parameters
        standalone.update(verify_parameters(model,a.checkpoint))
    model.set_eval();model=model.to(device='cuda',dtype=torch.bfloat16);history=[];records=[];torch.cuda.reset_peak_memory_stats()
    def tensor(rgb):
        if rgb.size!=(1024,576):rgb=rgb.resize((1024,576),Image.Resampling.BILINEAR)
        return torch.from_numpy(np.asarray(rgb,dtype=np.uint8).copy()).permute(2,0,1)[None].to(device='cuda',dtype=torch.bfloat16)/127.5-1
    with torch.inference_mode():
        for index,path in enumerate(files):
            if index in cuts:history.clear()
            image=Image.open(path).convert('RGB')
            if image.width*9!=image.height*16:raise ValueError('Use16:9 input; the model directly resizes to1024x576')
            current=tensor(image.resize((1024,576),Image.Resampling.BILINEAR));references=[]
            if a.mode=='temporal' and len(history)>=4:references=[tensor(p) for p in history[-1:-5:-1]]
            stacked=torch.stack([current,*references],dim=2)
            torch.cuda.synchronize();start=time.perf_counter();pred=model(stacked);torch.cuda.synchronize();seconds=time.perf_counter()-start
            if tuple(pred.shape)!=(1,3,len(references)+1,576,1024) or not torch.isfinite(pred).all():raise ValueError(f'Invalid model output {tuple(pred.shape)}')
            rgb=((pred[0,:,0].float().permute(1,2,0).cpu().numpy()+1)*127.5).clip(0,255).astype(np.uint8);small=Image.fromarray(rgb);result=small.resize(image.size,Image.Resampling.BICUBIC);destination=a.out/f'{index:06d}.png';result.save(destination)
            # Match official autoregressive PNG feedback: previous enhanced
            # outputs, never future frames or independent ground truth.
            history.append(result);history=history[-4:]
            records.append({'frame':index,'input':path.name,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'output':destination.name,'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'history_frames':len(references),'model_seconds':seconds,'cut_reset':index in cuts})
            if index%20==0:print('TEMPORAL_ENHANCE',a.mode,index+1,len(files),round(seconds,4),len(references),flush=True)
    warm=[r['model_seconds'] for r in records if r['frame']>=4]
    report={'schema':1,'mode':a.mode,'model':'nvidia/Harmonizer','model_revision':'20ca33d4612b1e98e0526b3a7ee604af5b289f58','checkpoint_sha256':hashlib.sha256(a.checkpoint.read_bytes()).hexdigest(),'model_license':'NVIDIA Open Model License','source_code_license':'Apache-2.0','attribution':'Built on NVIDIA Cosmos','frames':len(files),'internal_resolution':[1024,576],'context':'Current rendered RGB plus four previous enhanced outputs when available; reset at declared cuts','uses_future_frames':False,'model_median_seconds_after_frame4':float(np.median(warm)) if warm else None,'model_p95_seconds_after_frame4':float(np.percentile(warm,95)) if warm else None,'peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,'timing_scope':'Synchronized model forward only, not capture, preparation, transport, encoding, or end-to-end generation FPS','torch':torch.__version__,'records':records}
    if standalone is not None:report['standalone_initialization']=standalone
    (a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('TEMPORAL_ENHANCE_COMPLETE',a.mode,len(files),flush=True)
if __name__=='__main__':main()
