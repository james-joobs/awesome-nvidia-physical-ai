"""Bake a fixed RGB road atlas and export the verified scene for the browser."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt


def asset(directory, name):
    file=directory/name
    with file.open("rb") as stream:
        digest=hashlib.file_digest(stream,"sha256").hexdigest()
    return {"file":name,"bytes":file.stat().st_size,"sha256":digest}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--sfm",type=Path,required=True)
    parser.add_argument("--fit",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=args.output
    out.mkdir(parents=True,exist_ok=True)
    fit=json.loads((args.fit/"fit.json").read_text())
    records=json.loads((args.sfm/"cameras.json").read_text())["records"]
    geometry=np.load(args.fit/"geometry.npz")
    poses,k,indices=[geometry[key] for key in ("poses","intrinsics","indices")]
    xx=np.array([x["pose"][0][3] for x in fit["front_path"]])
    bounds=[float(xx.min()-5),-9,float(xx.max()+15),9]
    width=1920
    height=round(width*(bounds[3]-bounds[1])/(bounds[2]-bounds[0]))
    x,y=np.meshgrid(np.linspace(bounds[0],bounds[2],width,endpoint=False),
                    np.linspace(bounds[3],bounds[1],height,endpoint=False))
    world=np.dstack([x,y,np.zeros(x.shape)])
    weighted=np.zeros((*x.shape,3),np.float32)
    weight=np.zeros(x.shape,np.float32)
    votes=np.zeros(x.shape,np.uint8)
    for i in indices:
        pose=poses[i]
        relative=world-pose[:3,3]
        camera=relative@pose[:3,:3]
        z=camera[...,2]
        focal=np.array([k[i,0,0],k[i,1,1]])
        uv=camera[...,:2]*focal/np.maximum(z[...,None],.1)+k[i,:2,2]
        u,v=uv[...,0].astype(np.float32),uv[...,1].astype(np.float32)
        row=records[i]
        labels=cv2.imread(str(args.sfm/"labels"/row["file"].replace(".jpg",".png")),0)
        mask=cv2.erode((labels==0).astype(np.uint8),np.ones((9,9),np.uint8))
        mask[round(mask.shape[0]*.84):]=0
        shown=cv2.remap(mask,u,v,cv2.INTER_NEAREST)>0
        valid=shown & (z>1.5) & (z<26) & (pose[2,3]>0)
        quality=np.where(valid,pose[2,3]*focal[1]/np.maximum(z,1.0)**2,0)
        if valid.any():
            image=cv2.cvtColor(cv2.imread(str(args.input/"sources"/row["file"])),cv2.COLOR_BGR2RGB)
            colors=cv2.remap(image,u*(image.shape[1]/labels.shape[1]),v*(image.shape[0]/labels.shape[0]),cv2.INTER_LINEAR)
            # Feather camera boundaries and blend RGB across times so moving shadows
            # do not leave the sharp triangular seams of a single-view winner.
            edge=cv2.distanceTransform(mask,cv2.DIST_L2,5)
            interior=cv2.remap(edge,u,v,cv2.INTER_LINEAR)
            contribution=(np.clip(quality,0,65)**.85*np.clip(interior/45,0,1)).astype(np.float32)
            weighted += colors*contribution[...,None]
            weight += contribution
        votes+=valid
    mask=votes>=2
    if mask.mean()<.1:
        raise ValueError(f"Insufficient multiple-view road coverage: {mask.mean():.1%}")
    pixels = np.rint(weighted / np.maximum(weight[...,None],1e-6)).clip(0,255).astype(np.uint8)
    distance, nearest=distance_transform_edt(~mask,return_indices=True)
    pixels[~mask]=pixels[tuple(nearest[:,~mask])]
    pixels[distance>16]=0
    pixels=np.rint(255*(pixels/255)**.86).astype(np.uint8)
    alpha=(np.clip(cv2.distanceTransform(mask.astype(np.uint8),cv2.DIST_L2,5)/5,0,1)*255).astype(np.uint8)
    Image.fromarray(np.dstack([pixels,alpha])).save(out/"ground.webp",quality=92)
    for name in ("scene.spz","sky.webp"):
        shutil.copyfile(args.fit/name,out/name)
    fit["sky"].update(asset(out,"sky.webp"))
    fit.update(road_coverage=float(mask.mean()),road_size=[width,height],
               atlas_asset=asset(out,"ground.webp"))
    # Shared browser road package. The field name comes from the PandaSet reader.
    report={"schema":1,"texture":"ground.webp","bounds_xy":bounds,"height_coefficients":[0,0,0,0],
            "road_clearance":[1.5,2.25],
            "sky_filtered":asset(out,"scene.spz"),"surroundings":{"sky":fit["sky"],"facades":[]},
            "scene_fit":fit}
    (out/"road.json").write_text(json.dumps(report,separators=(",",":"))+"\n")
    print(f"{mask.mean():.1%} of the atlas has observed road support")


if __name__=="__main__":
    main()
