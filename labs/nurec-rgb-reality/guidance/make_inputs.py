"""Create a separate RGB-only experiment with held-out timestamps and training-only seeds."""
import argparse, hashlib, json, os, shutil
from pathlib import Path
import numpy as np
import pycolmap
from PIL import Image


def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--no-holdout',action='store_true',help='Fit the final viewer model to all RGB; never use this mode for held-out scores');a=p.parse_args()
    base, root=a.base.resolve(),a.root.resolve();root.mkdir(parents=True,exist_ok=True)
    meta=json.loads((base/'rgb-cameras.json').read_text());frames=meta['frames']
    times=sorted({r['timestamp_us'] for r in frames});held=set() if a.no_holdout else {t for i,t in enumerate(times) if i%6==3}
    train=[r for r in frames if r['timestamp_us'] not in held];test=[r for r in frames if r['timestamp_us'] in held]
    assert (len(train),len(test))==((162,0) if a.no_holdout else (138,24))
    (root/'rgb').mkdir(exist_ok=True)
    for r in frames:
        src=base/'rgb'/r['image'];dst=root/'rgb'/r['image'];dst.parent.mkdir(parents=True,exist_ok=True)
        assert hashlib.sha256(src.read_bytes()).hexdigest()==r['sha256']
        if not dst.exists():os.link(src,dst)
    full={**meta,'frames':frames};(root/'all-cameras.json').write_text(json.dumps(full,indent=2)+'\n')
    (root/'rgb-cameras.json').write_text(json.dumps({**meta,'frames':train},indent=2)+'\n')
    reconstruction=pycolmap.Reconstruction(str(base/'rig-source/work/undistorted/sparse/0'))
    T=np.asarray(json.loads((base/'rig-source/viewer/cameras.json').read_text())['world_to_viewer'])
    train_names={r['image'] for r in train};images={}
    for im in reconstruction.images.values():
        if im.name in train_names:
            cam=reconstruction.cameras[im.camera_id];M=im.cam_from_world().matrix();R=M[:,:3];C=-R.T@M[:,3]
            images[im.image_id]=(im,cam.calibration_matrix(),R,C,np.asarray(Image.open(root/'rgb'/im.name).convert('RGB')))
    xyz=[];colors=[];tracks=[]
    for point in reconstruction.points3D.values():
        observations=[]
        for e in point.track.elements:
            if e.image_id not in images:continue
            im,K,R,C,rgb=images[e.image_id];uv=im.points2D[e.point2D_idx].xy
            d=R.T@np.linalg.solve(K,np.r_[uv,1]);d/=np.linalg.norm(d)
            observations.append((e.image_id,uv,R,C,d,rgb))
        if len(observations)<3:continue
        projectors=[np.eye(3)-np.outer(o[4],o[4]) for o in observations]
        A=sum(projectors);b=sum(P@o[3] for P,o in zip(projectors,observations))
        if np.linalg.cond(A)>1e6:continue
        X=np.linalg.solve(A,b);good=[]
        for ident,uv,R,C,d,rgb in observations:
            K=images[ident][1];q=K@(R@(X-C));xy=q[:2]/q[2]
            if q[2]<=0 or np.linalg.norm(xy-uv)>2.5:continue
            x,y=np.rint(uv).astype(int)
            if 0<=y<rgb.shape[0] and 0<=x<rgb.shape[1]:good.append((ident,uv,rgb[y,x]))
        if len(good)<3:continue
        P=(T@np.r_[X,1])[:3];idx=len(xyz);xyz.append(P);colors.append(np.mean([g[2] for g in good],axis=0))
        for ident,uv,_ in good:tracks.append((images[ident][0].name,uv.tolist(),idx))
    np.savez_compressed(root/'sfm-points.npz',xyz=np.asarray(xyz,np.float32),rgb=np.asarray(colors,np.uint8))
    (root/'training-tracks.json').write_text(json.dumps(tracks,separators=(',',':'))+'\n')
    for f in ['PANDASET-DATA-LICENSE.txt']:
        if (base/f).exists():shutil.copy2(base/f,root/f)
    (root/'runtime-home').mkdir(exist_ok=True)
    torch_cache=base/'runtime-home/.cache/torch'
    def link_cached(source,destination):
        if not Path(destination).exists():os.link(source,destination)
        return destination
    if torch_cache.exists():shutil.copytree(torch_cache,root/'runtime-home/.cache/torch',dirs_exist_ok=True,copy_function=link_cached)
    report={'schema':1,'production_fit':a.no_holdout,'train_images':len(train),'held_out_images':len(test),'train_times':len(times)-len(held),'held_out_times':len(held),'held_out_timestamp_us':sorted(held),'seed_points':len(xyz),'seed_color_source':'Training RGB only; points retriangulated from training observations at fixed RGB-derived poses','pose_scope':'Offline COLMAP camera estimates use the full image set. The held-out mode is a fixed-camera RGB comparison, not an online causal reconstruction benchmark. The all-image production fit is not an independent validation model.','uses_lidar':False,'uses_supplied_depth':False,'uses_source_calibration':False,'uses_source_labels':False}
    (root/'split.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':main()
