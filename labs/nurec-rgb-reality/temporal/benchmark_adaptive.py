"""One-GPU preview/HQ experiment against full-resolution model references."""
from __future__ import annotations
import argparse,base64,hashlib,io,json,time
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from service import Engine
from benchmark_speed import ssim


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['input','rig','out','checkpoint','components']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--max-frames',type=int);p.add_argument('--quality-stride',type=int,default=8)
    a=p.parse_args()
    files=sorted(f for f in a.input.iterdir() if f.suffix.lower() in {'.png','.jpg','.jpeg'})
    if a.max_frames:files=files[:a.max_frames]
    if len(files)<8 or a.quality_stride<1:raise ValueError('Use at least8 frames and a positive quality stride')
    poses=json.loads(a.rig.read_text())['rig_trajectories'][0]['T_rig_worlds']
    if len(poses)<len(files):raise ValueError('One ordered rig pose is required per input frame')
    if a.out.exists():raise ValueError('Choose a fresh output directory to preserve earlier results')
    a.out.mkdir(parents=True);images=a.out/'images';images.mkdir()
    engine=Engine(a.checkpoint,a.components);engine.warmup();rows=[];quality=[]
    def request(i,session,execution,phase=None,reset=False):
        image=Image.open(files[i]).convert('RGB');buf=io.BytesIO();image.save(buf,format='PNG',compress_level=1)
        m=np.asarray(poses[i]);return dict(session=session,execution=execution,phase=phase,mode='temporal',reset=reset,
            image=base64.b64encode(buf.getvalue()).decode(),view=dict(camera=m[:3,3].tolist(),forward=m[:3,2].tolist(),
            frame=i,variant='guided',projection=[64,16/9,1,1]))
    def decode(result):return np.asarray(Image.open(io.BytesIO(base64.b64decode(result['image']))).convert('RGB'))
    # Same rendered sequence, fresh continuous full-resolution history.
    with torch.inference_mode():
        for i,file in enumerate(files):
            result=engine.infer(request(i,'continuous-reference','exact',reset=i==0))
            Image.fromarray(decode(result)).save(images/f'continuous-{i:06d}.png',compress_level=1)
        for i,file in enumerate(files):
            result=engine.infer(request(i,'preview-stream','adaptive','preview',reset=i==0));rgb=decode(result)
            Image.fromarray(rgb).save(images/f'preview-{i:06d}.png',compress_level=1)
            ref=np.asarray(Image.open(images/f'continuous-{i:06d}.png'))
            large=np.asarray(Image.fromarray(rgb).resize((1024,576),Image.Resampling.BICUBIC))
            mse=float(np.mean((large.astype(np.float32)-ref.astype(np.float32))**2))
            row={k:result[k] for k in ['model_ms','final_forward_ms','history_frames','resolution','server_total_ms','rgb_sha256']}
            row.update(frame=i,input_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                       psnr_vs_hq_db=float(10*np.log10(255**2/mse)) if mse else None,ssim_vs_hq=ssim(large,ref))
            rows.append(row)
        for i in range(0,len(files),a.quality_stride):
            session=f'quality-{i}'
            engine.infer(request(i,session,'adaptive','preview',reset=True))
            got=engine.infer(request(i,session,'adaptive','refine'));adaptive=decode(got)
            # Five ACTUAL stationary full-resolution forwards, not a moving
            # temporal-history reference. A fresh history for every pose.
            current=engine.image_tensor(Image.open(files[i]).convert('RGB'));history=[];times=[]
            for _ in range(5):
                refs=history[-1:-5:-1] if len(history)>=4 else []
                x=torch.stack([current,*refs],dim=2);torch.cuda.synchronize();born=time.perf_counter()
                y=engine.fast(x);torch.cuda.synchronize();times.append((time.perf_counter()-born)*1000)
                rgb=((y[0,:,0].float().permute(1,2,0).cpu().numpy()+1)*127.5).clip(0,255).astype(np.uint8)
                history=[*history,engine.image_tensor(Image.fromarray(rgb))][-4:]
            equal=bool(np.array_equal(adaptive,rgb))
            quality.append(dict(frame=i,pixel_equal_fresh_hq_reference=equal,model_ms=got['model_ms'],
                model_calls=got['model_calls'],reused_reference_slots=got['reused_reference_slots'],
                resolution=got['resolution'],hq_uses_preview_history=got['hq_uses_preview_history'],
                reference_five_forward_ms=sum(times),actual_two_forward_ms=got['model_ms'],
                rgb_sha256=got['rgb_sha256'],reference_rgb_sha256=hashlib.sha256(rgb.tobytes()).hexdigest()))
            Image.fromarray(rgb).save(images/f'reference-{i:06d}.png',compress_level=1)
            Image.fromarray(adaptive).save(images/f'refined-{i:06d}.png',compress_level=1)
            if not equal:raise RuntimeError('Stationary HQ differs from the actual five-forward reference')
    report=dict(schema=1,device=torch.cuda.get_device_name(0),checkpoint_sha256=engine.provenance['checkpoint_sha256'],
        parameters_verified=engine.provenance['all_learned_parameters_equal_released_tensors'],preview=rows,refinement=quality,
        scope='Experimental512 research-model preview, not an official NIM mode. Preview fidelity is against continuous1024 outputs. Restored HQ is against five actual stationary1024 forwards with fresh history; not moving-history equality or unseen-view accuracy.')
    (a.out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ADAPTIVE_BENCHMARK_DONE',len(rows),len(quality),flush=True)


if __name__=='__main__':main()
