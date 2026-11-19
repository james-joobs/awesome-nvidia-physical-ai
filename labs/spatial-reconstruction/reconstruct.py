"""Train an fVDB 3DGS scene from known CARLA cameras; hold out every eighth image."""
import argparse
import hashlib
import json
import math
import subprocess
import time
from pathlib import Path

import fvdb
import numpy as np
import torch
from PIL import Image
from plyfile import PlyData
from scipy.spatial.transform import Rotation, Slerp
from fvdb_reality_capture.radiance_fields import GaussianSplatReconstruction, GaussianSplatReconstructionConfig, GaussianSplatOptimizerConfig
from fvdb_reality_capture.sfm_scene import SfmScene
from fvdb_reality_capture.sfm_scene.sfm_scene import SpatialScaleMode


def export_browser_splat(source, target, maximum=200_000):
    """32-byte .splat, DC color only, deterministic opacity-weighted subset.

    Browser preview is deliberately smaller than the original SH-degree-3 model.
    """
    vertices = PlyData.read(source)["vertex"].data
    opacity = 1/(1+np.exp(-np.clip(vertices["opacity"],-40,40)))
    valid = np.flatnonzero(opacity>.04)
    if len(valid)>maximum:
        rng=np.random.default_rng(42)
        weights=opacity[valid].astype(np.float64)
        valid=np.sort(rng.choice(valid,maximum,replace=False,p=weights/weights.sum()))
    v=vertices[valid]
    packed=np.empty(len(v),dtype=[("position","<f4",3),("scale","<f4",3),("rgba","u1",4),("rotation","u1",4)])
    packed["position"]=np.stack([v[k] for k in ("x","y","z")],-1)
    packed["scale"]=np.exp(np.stack([v[f"scale_{i}"] for i in range(3)],-1))
    color=.5+.28209479177387814*np.stack([v[f"f_dc_{i}"] for i in range(3)],-1)
    packed["rgba"][:,:3]=np.clip(color*255,0,255).astype(np.uint8)
    packed["rgba"][:,3]=np.clip(opacity[valid]*255,0,255).astype(np.uint8)
    quat=np.stack([v[f"rot_{i}"] for i in range(4)],-1)
    quat/=np.linalg.norm(quat,axis=1,keepdims=True).clip(1e-8)
    packed["rotation"]=np.clip(quat*128+128,0,255).astype(np.uint8)
    packed.tofile(target)
    return {"gaussians":len(v),"bytes":target.stat().st_size,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
        "format":"32-byte .splat; DC color; opacity > .04; deterministic weighted sampling if needed"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--epochs",type=int,default=40)
    parser.add_argument("--ffmpeg",default="ffmpeg")
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    torch.backends.cudnn.enabled=False  # OMEN cuDNN library mismatch; native CUDA convolutions still work.
    scene=SfmScene.from_simple_directory(args.input)
    config=GaussianSplatReconstructionConfig(max_epochs=args.epochs,optimize_camera_poses=False,
        refine_stop_epoch=args.epochs,near_plane=.05,far_plane=200)
    optimizer=GaussianSplatOptimizerConfig(spatial_scale_mode=SpatialScaleMode.MAX_CAMERA_TO_CENTROID,max_gaussians=750_000)
    runner=GaussianSplatReconstruction.from_sfm_scene(scene,config=config,optimizer_config=optimizer,use_every_n_as_val=8)
    start=time.monotonic()
    runner.optimize()
    seconds=time.monotonic()-start
    model=runner.model
    model_path=args.output/"town03.ply"
    runner.save_ply(model_path)
    browser=export_browser_splat(model_path,args.output/"town03.splat")
    width,height=640,360
    K=np.array(scene.images[0].camera_metadata.projection_matrix,dtype=np.float32)

    def render(c2w):
        with torch.inference_mode():
            rgb,alpha=model.render_images(torch.tensor(np.linalg.inv(c2w)[None],dtype=torch.float32,device="cuda"),
                torch.tensor(K[None],dtype=torch.float32,device="cuda"),width,height,.05,200)
        return rgb[0,:,:,:3].clamp(0,1).cpu().numpy(),float(alpha.mean())

    metrics=[]
    for i in range(0,len(scene.images),8):
        pred,alpha=render(scene.camera_to_world_matrices[i])
        ref=np.array(Image.open(scene.images[i].image_path).convert("RGB"))/255
        mse=np.mean((pred-ref)**2)
        metrics.append({"view":i,"psnr_db":round(-10*math.log10(max(float(mse),1e-12)),3),"mean_alpha":round(alpha,4)})
        if i==0:
            Image.fromarray((pred*255).astype(np.uint8)).save(args.output/"held-out-render.png")
            Image.fromarray((ref*255).astype(np.uint8)).save(args.output/"held-out-reference.png")
    poses=scene.camera_to_world_matrices
    keys=np.arange(len(poses)+1,dtype=float)
    closed=np.concatenate([poses,poses[:1]],axis=0)
    rotations=Slerp(keys,Rotation.from_matrix(closed[:,:3,:3]))
    fps,frames=24,384
    movie=args.output/"flythrough.mp4"
    encoder=subprocess.Popen([args.ffmpeg,"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24",
        "-s",f"{width}x{height}","-r",str(fps),"-i","pipe:0","-an","-c:v","libx264","-crf","22",
        "-pix_fmt","yuv420p","-movflags","+faststart",str(movie)],stdin=subprocess.PIPE)
    alphas=[]
    for t in np.linspace(0,len(poses),frames,endpoint=False):
        pose=np.eye(4)
        pose[:3,:3]=rotations(float(t)).as_matrix()
        pose[:3,3]=[np.interp(t,keys,closed[:,axis,3]) for axis in range(3)]
        rgb,alpha=render(pose)
        alphas.append(alpha)
        encoder.stdin.write((rgb*255).astype(np.uint8).tobytes())
    encoder.stdin.close()
    assert encoder.wait()==0
    report={"mode":"multi-view reconstruction, not generative world-model inference",
        "input":json.loads((args.input/"capture.json").read_text()),"input_views":len(poses),
        "training_views":len(poses)-len(metrics),"held_out_views":len(metrics),"epochs":args.epochs,
        "optimization_seconds":round(seconds,3),"gaussians":int(model.num_gaussians),
        "held_out_psnr_db":round(float(np.mean([m["psnr_db"] for m in metrics])),3),"per_view":metrics,
        "runtime":{"fvdb":fvdb.__version__,"torch":torch.__version__,"gpu":torch.cuda.get_device_name(0),"cudnn_enabled":False},
        "browser":browser,"render":{"frames":frames,"fps":fps,"resolution":[width,height],
        "median_alpha":float(np.median(alphas)),"sha256":hashlib.sha256(movie.read_bytes()).hexdigest()},
        "limitations":["Static radiance field; no collision mesh or dynamic traffic", "CARLA water and distant sky are difficult to reconstruct", "Intermediate .splat uses sampled DC-only data; use compress_web.py on the full PLY for the published SPZ"]}
    (args.output/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":
    main()
