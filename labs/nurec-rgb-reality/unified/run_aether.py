"""Run public Aether RGB→disparity/camera reconstruction on one CUDA GPU.

Original pipeline and weights are loaded from pinned upstream checkouts. The
real empty text embedding is computed once, then T5 is released before inference.
No WorldLatent, LiDAR, external depth or external camera pose enters this model.
"""
import argparse
import gc
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image
import torch


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream', type=Path, required=True)
    p.add_argument('--models', type=Path, required=True)
    p.add_argument('--images', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--width', type=int, default=720)
    p.add_argument('--height', type=int, default=480)
    p.add_argument('--steps', type=int, default=4)
    p.add_argument('--frames', type=int, default=17, choices=[17,25,33,41])
    p.add_argument('--model-fps', type=int, default=12, choices=[8,10,12,15,24])
    p.add_argument('--offload', action='store_true')
    p.add_argument('--camera-from', type=Path, help='Prediction: geometry.npz from a completed RGB-only Aether reconstruction')
    a = p.parse_args()
    if a.out.exists():
        raise ValueError('Choose a fresh output directory; earlier results are preserved')
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA GPU required')
    a.out.mkdir(parents=True)
    sys.path.insert(0, str(a.upstream.resolve()))
    from aether.pipelines.aetherv1_pipeline_cogvideox import AetherV1PipelineCogVideoX
    from aether.utils.postprocess_utils import postprocess_pointmap, camera_pose_to_raymap
    from diffusers import AutoencoderKLCogVideoX, CogVideoXDPMScheduler, CogVideoXTransformer3DModel
    from transformers import AutoTokenizer, T5EncoderModel
    paths=sorted(x for x in a.images.iterdir() if x.suffix.lower() in {'.jpg','.png','.jpeg'})[:a.frames]
    if len(paths)!=a.frames:
        raise ValueError('Insufficient distinct input frames')
    rgb=[];records=[]
    for path in paths:
        image=Image.open(path).convert('RGB');w,h=image.size
        # Match the upstream center crop explicitly, then supply exact-sized PILs.
        if a.height/a.width>h/w:
            cw=int(h/a.height*a.width);ch=h;left=int((w-h/a.height*a.width)/2);top=0
        else:
            cw=w;ch=int(w/a.width*a.height);left=0;top=int((h-w/a.width*a.height)/2)
        image=image.crop((left,top,left+cw,top+ch)).resize((a.width,a.height),Image.Resampling.BILINEAR)
        rgb.append(image)
        records.append({'name':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'loaded_size':[w,h],'crop_xywh':[left,top,cw,ch],'resize':[a.width,a.height]})
    print('LOADING_PUBLIC_AETHER',flush=True);start=time.perf_counter()
    base=str(a.models/'cogvideox');model=str(a.models/'aether')
    pipe=AetherV1PipelineCogVideoX(
        tokenizer=AutoTokenizer.from_pretrained(base,subfolder='tokenizer',local_files_only=True),
        text_encoder=T5EncoderModel.from_pretrained(base,subfolder='text_encoder',torch_dtype=torch.bfloat16,low_cpu_mem_usage=True,local_files_only=True),
        vae=AutoencoderKLCogVideoX.from_pretrained(base,subfolder='vae',torch_dtype=torch.bfloat16,local_files_only=True),
        scheduler=CogVideoXDPMScheduler.from_pretrained(base,subfolder='scheduler',local_files_only=True),
        transformer=CogVideoXTransformer3DModel.from_pretrained(model,subfolder='transformer',torch_dtype=torch.bfloat16,low_cpu_mem_usage=True,local_files_only=True))
    # Official __init__ computed the real empty-prompt T5 embedding. No zeros.
    pipe.register_modules(text_encoder=None)
    gc.collect()
    pipe.vae.enable_slicing();pipe.vae.enable_tiling()
    if a.offload: pipe.enable_model_cpu_offload()
    else: pipe.to('cuda')
    torch.cuda.synchronize();load_seconds=time.perf_counter()-start
    torch.cuda.reset_peak_memory_stats();start=time.perf_counter()
    kwargs={'task':'reconstruction','video':rgb,'guidance_scale':1.}
    if a.camera_from:
        previous=np.load(a.camera_from)
        poses=previous['camera_pose'].copy();poses=np.linalg.inv(poses[0])[None]@poses
        rays=camera_pose_to_raymap(camera_pose=poses,intrinsic=previous['intrinsics'].copy(),H=a.height,W=a.width,dmax=1.)
        kwargs={'task':'prediction','image':rgb[0],'raymap':rays,'guidance_scale':3.}
    result=pipe(**kwargs,height=a.height,width=a.width,num_frames=a.frames,num_inference_steps=a.steps,fps=a.model_fps,generator=torch.Generator(device='cuda').manual_seed(42))
    torch.cuda.synchronize();seconds=time.perf_counter()-start
    stats={'load_seconds':load_seconds,'inference_seconds':seconds,'frames_per_second_offline':a.frames/seconds,'peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,'peak_reserved_gib':torch.cuda.max_memory_reserved()/2**30}
    # Upstream stores direction + signed-log origin, NOT Plucker d/m rays.
    # postprocess_pointmap mutates the raymap, so preserve original raw values.
    np.savez_compressed(a.out/'raw.npz',rgb=result.rgb,disparity=result.disparity,raymap=result.raymap)
    geometry=postprocess_pointmap(result.disparity,result.raymap.copy(),vae_downsample_scale=8,ray_o_scale_inv=.1,smooth_camera=False)
    original=np.stack([np.asarray(x) for x in rgb])
    arrays={'observed_rgb':original,'decoded_rgb':result.rgb,**geometry}
    for key,value in arrays.items():
        if not np.isfinite(value).all(): raise RuntimeError(f'Nonfinite output: {key}')
    np.savez_compressed(a.out/'geometry.npz',**arrays)
    report={'schema':1,'model':'AetherV1','task':kwargs['task'],'input':'first RGB + camera raymap estimated from all 17 RGB frames in the separate reconstruction pass' if a.camera_from else 'camera RGB only','condition_geometry_sha256':hashlib.file_digest(a.camera_from.open('rb'),'sha256').hexdigest() if a.camera_from else None,'steps':a.steps,'seed':42,'shape':list(original.shape),'model_fps_condition':a.model_fps,'source_timestamps_used':False,'camera_ground_truth_used':False,'lidar_used':False,'source_records':records,'device':torch.cuda.get_device_name(),'torch':torch.__version__,'cuda':torch.version.cuda,'precision':'bfloat16','offload':a.offload,'empty_prompt':'real T5 embedding; encoder released after upstream initialization','camera_postprocess':'upstream raymap_to_poses, origin scale .1, no temporal smoothing','depth_units':'model-relative; not measured meters','raymap':'direction and signed-log origin; not Plucker moment','timing':stats,'output_shapes':{k:list(v.shape) for k,v in arrays.items()}}
    (a.out/'run.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(stats),flush=True);print('AETHER_COMPLETE',flush=True)


if __name__=='__main__':main()
