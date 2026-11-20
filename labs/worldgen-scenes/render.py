"""Render a translated 360-degree camera path through WorldGen's actual 3D PLY.

Run with the separate fVDB Reality Capture runtime, not the WorldGen environment.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from fvdb_reality_capture import GaussianSplat3d


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--scene',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--ffmpeg',default='ffmpeg')
    p.add_argument('--frames',type=int,default=480)
    p.add_argument('--fps',type=int,default=24)
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    torch.backends.cudnn.enabled=False
    model,_=GaussianSplat3d.from_ply(str(a.scene),device='cuda')
    width,height=960,540
    focal=width/(2*math.tan(math.radians(80)/2))
    K=np.array([[focal,0,width/2],[0,focal,height/2],[0,0,1]],dtype=np.float32)
    camera_json={'convention':'OpenCV world-to-camera; x right, y down, z forward; arbitrary WorldGen distance scale',
                 'resolution':[width,height],'K':K.tolist(),'fps':a.fps,'frames':[]}
    video=a.output/'free-view.mp4'
    encoder=subprocess.Popen([a.ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-s',f'{width}x{height}','-r',str(a.fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast',
        '-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
    for i,t in enumerate(np.linspace(0,1,a.frames,endpoint=False)):
        yaw=2*math.pi*t
        # Translation really changes the optical center; this is not a 2D panorama crop.
        center=np.array([.20*math.sin(2*yaw),.045*math.sin(yaw),.15*math.sin(yaw)])
        forward=np.array([math.sin(yaw),.055*math.sin(yaw),math.cos(yaw)])
        forward/=np.linalg.norm(forward)
        right=np.cross([0,1,0],forward); right/=np.linalg.norm(right)
        down=np.cross(forward,right)
        c2w=np.eye(4,dtype=np.float32); c2w[:3,:3]=np.stack([right,down,forward],axis=1); c2w[:3,3]=center
        w2c=np.linalg.inv(c2w)
        with torch.inference_mode():
            rgb,alpha=model.render_images(torch.tensor(w2c[None],device='cuda'),torch.tensor(K[None],device='cuda'),width,height,.005,100.)
        pixels=(rgb[0,:,:,:3].clamp(0,1).cpu().numpy()*255).astype(np.uint8)
        encoder.stdin.write(pixels.tobytes())
        camera_json['frames'].append({'frame':i,'center':center.tolist(),'world_to_camera':w2c.tolist(),'mean_alpha':float(alpha.mean())})
        if i in (0,a.frames//4,a.frames//2,a.frames*3//4):
            Image.fromarray(pixels).save(a.output/f'view-{i:04}.jpg',quality=90)
            print('Rendered',i,'/',a.frames,flush=True)
    encoder.stdin.close()
    if encoder.wait(): raise RuntimeError('ffmpeg failed')
    assert np.mean([f['mean_alpha'] for f in camera_json['frames']])>.5
    (a.output/'cameras.json').write_text(json.dumps(camera_json,indent=2)+'\n')
    report={'frames':a.frames,'fps':a.fps,'duration_seconds':a.frames/a.fps,'resolution':[width,height],
        'renderer':'fVDB Reality Capture','torch':torch.__version__,'gaussians':int(model.num_gaussians),
        'center_range':np.ptp([f['center'] for f in camera_json['frames']],axis=0).tolist(),
        'mean_alpha':float(np.mean([f['mean_alpha'] for f in camera_json['frames']])),
        'mp4_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'mp4_bytes':video.stat().st_size,
        'cameras_sha256':hashlib.sha256((a.output/'cameras.json').read_bytes()).hexdigest()}
    (a.output/'render.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__': main()
