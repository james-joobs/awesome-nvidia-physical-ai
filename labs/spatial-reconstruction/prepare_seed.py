"""Seed 3DGS only from training-view depth and colors; reserve indices 0,8,16,..."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def prepare(folder):
    cameras=json.loads((folder/"cameras.json").read_text())
    clouds,colors=[],[]
    for i,camera in enumerate(cameras):
        if i%3 or i%8==0:
            continue
        rgb=np.array(Image.open(folder/"images"/camera["image_path"]).convert("RGB"))
        depth=np.load(folder/"depth"/f"view_{i:03}.npy")
        h,w=depth.shape
        K=np.array(camera["camera_intrinsics"])
        c2w=np.linalg.inv(camera["world_to_camera"])
        v,u=np.mgrid[0:h:6,0:w:6]
        d=depth[v,u]
        good=(d>.5)&(d<80)
        cv=np.stack([(u-K[0,2])/K[0,0]*d,(v-K[1,2])/K[1,1]*d,d],-1)[good]
        clouds.append(cv@c2w[:3,:3].T+c2w[:3,3])
        colors.append(rgb[v,u][good])
    xyz,rgb=np.concatenate(clouds),np.concatenate(colors)
    _,indices=np.unique(np.floor(xyz/.12).astype(int),axis=0,return_index=True)
    xyz,rgb=xyz[indices],rgb[indices]
    with (folder/"pointcloud.ply").open("w") as f:
        f.write("ply\nformat ascii 1.0\nelement vertex %d\n"%len(xyz))
        f.write("property float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n")
        for p,c in zip(xyz,rgb):
            f.write("%.5f %.5f %.5f %d %d %d\n"%(*p,*c))
    return len(xyz)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("folder",type=Path)
    args=parser.parse_args()
    count=prepare(args.folder)
    report=json.loads((args.folder/"capture.json").read_text())
    report.update(seed_points=count,seed_views=[i for i in range(len(json.loads((args.folder/"cameras.json").read_text()))) if i%3==0 and i%8!=0],held_out_modulo=8)
    (args.folder/"capture.json").write_text(json.dumps(report,indent=2)+"\n")
    print(f"Seeded {count} points; held-out RGB and depth excluded.")
