"""Run SHARP on our CARLA inputs, using the known 90-degree camera intrinsics.

SHARP weights are research-only. This predicts nearby views, not a complete 360 world.
"""
import argparse
import hashlib
import json
import math
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from fvdb_reality_capture import GaussianSplat3d
from sharp.cli.predict import predict_image
from sharp.models import PredictorParams, create_predictor
from sharp.utils.gaussians import save_ply


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--checkpoint",type=Path,required=True)
    parser.add_argument("--ffmpeg",default="ffmpeg")
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    torch.backends.cudnn.enabled=False
    predictor=create_predictor(PredictorParams())
    predictor.load_state_dict(torch.load(args.checkpoint,weights_only=True))
    predictor.eval().cuda()
    reports=[]
    for image_path in sorted(args.input.glob("*.jpg")):
        image=np.array(Image.open(image_path).convert("RGB"))
        height,width=image.shape[:2]
        f_px=width/2 # Our CARLA camera has a known horizontal FOV of 90 degrees.
        torch.cuda.synchronize()
        start=time.monotonic()
        with torch.inference_mode():
            gaussians=predict_image(predictor,image,f_px,torch.device("cuda"))
        torch.cuda.synchronize()
        seconds=time.monotonic()-start
        ply=args.output/f"{image_path.stem}.ply"
        save_ply(gaussians,f_px,(height,width),ply)
        del gaussians
        splats,_=GaussianSplat3d.from_ply(str(ply))
        w,h,fps,frames=640,360,24,192
        K=np.array([[f_px*w/width,0,(w-1)/2],[0,f_px*h/height,(h-1)/2],[0,0,1]])
        movie=args.output/f"{image_path.stem}.mp4"
        encoder=subprocess.Popen([args.ffmpeg,"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24",
            "-s",f"{w}x{h}","-r",str(fps),"-i","pipe:0","-an","-c:v","libx264","-crf","22",
            "-pix_fmt","yuv420p","-movflags","+faststart",str(movie)],stdin=subprocess.PIPE)
        for i in range(frames):
            phase=i/(frames-1)*2*math.pi
            eye=np.array([.35*math.sin(phase),0,.1*(1-math.cos(phase))])
            forward=np.array([0,0,12])-eye
            forward/=np.linalg.norm(forward)
            right=np.cross([0,1,0],forward);right/=np.linalg.norm(right)
            pose=np.eye(4);pose[:3,:3]=np.stack([right,np.cross(forward,right),forward],axis=1);pose[:3,3]=eye
            with torch.inference_mode():
                rgb,_=splats.render_images(torch.tensor(np.linalg.inv(pose)[None],dtype=torch.float32,device="cuda"),
                    torch.tensor(K[None],dtype=torch.float32,device="cuda"),w,h,.01,1000)
            rgb=rgb[0,:,:,:3].clamp(0,1).cpu().numpy()
            encoder.stdin.write((rgb*255).astype(np.uint8).tobytes())
            if i==0:
                Image.fromarray((rgb*255).astype(np.uint8)).save(args.output/f"{image_path.stem}.jpg",quality=90)
        encoder.stdin.close()
        assert encoder.wait()==0
        reports.append({"input":image_path.name,"input_sha256":hashlib.sha256(image_path.read_bytes()).hexdigest(),
            "input_resolution":[width,height],"focal_px":f_px,"inference_seconds":round(seconds,3),
            "gaussians":int(splats.num_gaussians),"video":movie.name,"video_sha256":hashlib.sha256(movie.read_bytes()).hexdigest(),
            "frames":frames,"fps":fps,"camera_motion_m":{"x_amplitude":.35,"z_range":[0,.2]}})
        del splats
    (args.output/"result.json").write_text(json.dumps({"tool":"Apple SHARP","mode":"single-view reconstruction; nearby novel views",
        "renderer":"fVDB","weights_license":"Apple ML Research Model License: noncommercial research purposes",
        "runtime":{"torch":torch.__version__,"gpu":torch.cuda.get_device_name(0),"cudnn_enabled":False},"cases":reports},indent=2)+"\n")


if __name__=="__main__":
    main()
