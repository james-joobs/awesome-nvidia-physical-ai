"""One-GPU matched autoregressive speed/quality experiment, no frame interpolation."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import cv2,numpy as np,torch
from PIL import Image
from service import Engine
from fast import CurrentFrame,set_layout
from evaluate import backward_map

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(y):return ((y[0,:,0].float().permute(1,2,0).cpu().numpy()+1)*127.5).clip(0,255).astype(np.uint8)
def ssim(a,b):
 a=a.astype(np.float64);b=b.astype(np.float64);blur=lambda v:cv2.GaussianBlur(v,(11,11),1.5)
 ma,mb=blur(a),blur(b);va=blur(a*a)-ma*ma;vb=blur(b*b)-mb*mb;cov=blur(a*b)-ma*mb
 return float((((2*ma*mb+6.5025)*(2*cov+58.5225))/((ma*ma+mb*mb+6.5025)*(va+vb+58.5225)))[5:-5,5:-5].mean())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--components',type=Path,required=True);p.add_argument('--max-frames',type=int);a=p.parse_args()
 if a.out.exists() and any(a.out.iterdir()):raise ValueError('Use a fresh result directory')
 a.out.mkdir(parents=True,exist_ok=True);engine=Engine(a.checkpoint,a.components);m=engine.model;fast=CurrentFrame(m);files=sorted(x for x in a.input.iterdir() if x.suffix.lower() in {'.png','.jpg','.jpeg'})
 if a.max_frames:files=files[:a.max_frames]
 if len(files)<8:raise ValueError('At least eight continuous source frames are needed')
 report={'schema':1,'device':torch.cuda.get_device_name(0),'resolution':[1024,576],'precision':'bfloat16','previous_outputs':4,'checkpoint_sha256':digest(a.checkpoint),'learned_parameters':engine.provenance,'profiles':{},'scope':'Same RGB sequence, resolution, weights, four previous generated outputs and one diffusion step. Model-forward FPS excludes encoding/transport/recording; quality is fidelity to baseline, not unseen-view ground truth.'}
 with torch.inference_mode():
  for profile in ['baseline','exact','tuned']:
   set_layout(m,profile);torch.manual_seed(42);folder=a.out/profile;folder.mkdir();history=[];records=[];torch.cuda.reset_peak_memory_stats()
   for i,file in enumerate(files):
    image=Image.open(file).convert('RGB');refs=history[-1:-5:-1] if len(history)>=4 else [];x=torch.stack([engine.image_tensor(image),*[engine.image_tensor(v) for v in refs]],dim=2)
    torch.cuda.synchronize();start=time.perf_counter();y=m(x) if profile=='baseline' else fast(x);torch.cuda.synchronize();ms=(time.perf_counter()-start)*1000;rgb=pixels(y);out=folder/f'{i:06d}.png';Image.fromarray(rgb).save(out,compress_level=1);history=[*history,Image.fromarray(rgb)][-4:]
    row={'frame':i,'input_sha256':digest(file),'output_sha256':digest(out),'rgb_sha256':hashlib.sha256(rgb.tobytes()).hexdigest(),'model_ms':ms,'history_frames':len(refs)}
    if profile!='baseline':
     ref=np.asarray(Image.open(a.out/'baseline'/out.name));error=rgb.astype(np.float32)-ref.astype(np.float32);mse=float(np.mean(error**2));row['baseline_fidelity']={'pixel_equal':bool(np.array_equal(rgb,ref)),'mae_u8':float(np.abs(error).mean()),'max_abs_u8':float(np.abs(error).max()),'psnr_db':float(10*np.log10(255**2/mse)) if mse else None,'ssim':ssim(rgb,ref)}
    records.append(row)
    if i%20==0:print('SPEED',profile,i,len(files),round(ms,2),flush=True)
   warm=[r['model_ms'] for r in records if r['frame']>=4];stats={'model_median_ms':float(np.median(warm)),'model_p95_ms':float(np.percentile(warm,95)),'model_throughput_fps':1000/float(np.mean(warm)),'peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,'records':records}
   if profile!='baseline':
    q=[r['baseline_fidelity'] for r in records];nonzero=[x['psnr_db'] for x in q if x['psnr_db'] is not None];stats['fidelity']={'all_frames_pixel_equal':all(x['pixel_equal'] for x in q),'mean_mae_u8':float(np.mean([x['mae_u8'] for x in q])),'max_abs_u8':max(x['max_abs_u8'] for x in q),'mean_ssim':float(np.mean([x['ssim'] for x in q])),'mean_finite_psnr_db':float(np.mean(nonzero)) if nonzero else None}
   report['profiles'][profile]=stats;(a.out/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n');print('PROFILE_DONE',profile,{k:v for k,v in stats.items() if k!='records'},flush=True)
 # Shared native optical flow on the same valid pixels for all profiles.
 stability={k:[] for k in report['profiles']};previous=None
 for i,file in enumerate(files):
  native=cv2.resize(cv2.cvtColor(cv2.imread(str(file)),cv2.COLOR_BGR2RGB),(512,288));frames={k:cv2.resize(cv2.cvtColor(cv2.imread(str(a.out/k/f'{i:06d}.png')),cv2.COLOR_BGR2RGB),(512,288)) for k in stability}
  if previous and i>=4:
   mx,my,valid=backward_map(previous[0],native)
   for k in stability:
    warped=cv2.remap(previous[1][k],mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT);stability[k].append(float((np.abs(frames[k].astype(np.float32)-warped)/255)[valid].mean()))
  previous=(native,frames)
 for k,values in stability.items():report['profiles'][k]['shared_flow_warp_l1']=float(np.mean(values))
 (a.out/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n');print('BENCHMARK_DONE',flush=True)
if __name__=='__main__':main()
