"""Export compact per-frame RGB-D surfaces; no learned model is re-trained.

The reference is the earlier RGB/SfM camera estimate, not a sensor measurement.
One positive similarity transform aligns each complete sequence for comparison.
No frame-wise depth fitting or camera correction is applied.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image


def align_to_reference(predicted, reference):
    """First-camera rotational gauge + one least-squares translation scale."""
    rotation=reference[0,:3,:3]@predicted[0,:3,:3].T
    x=(predicted[:,:3,3]-predicted[0,:3,3])@rotation.T
    y=reference[:,:3,3]-reference[0,:3,3]
    if np.sum(x*x)<1e-8:raise ValueError('Cannot identify scale from stationary cameras')
    scale=float(np.sum(x*y)/np.sum(x*x))
    if not np.isfinite(scale) or scale<=0:raise ValueError('Invalid sequence alignment scale')
    translation=reference[0,:3,3]-scale*rotation@predicted[0,:3,3]
    aligned=predicted.copy();aligned[:,:3,:3]=rotation[None]@predicted[:,:3,:3]
    aligned[:,:3,3]=scale*predicted[:,:3,3]@rotation.T+translation
    errors=np.linalg.norm(aligned[:,:3,3]-reference[:,:3,3],axis=-1)
    rel=reference[:,:3,:3].transpose(0,2,1)@aligned[:,:3,:3]
    angles=np.rad2deg(np.arccos(np.clip((np.trace(rel,axis1=1,axis2=2)-1)/2,-1,1)))
    path=float(np.linalg.norm(np.diff(reference[:,:3,3],axis=0),axis=-1).sum())
    return aligned,scale,{'rotation':rotation.tolist(),'translation':translation.tolist(),'scale':scale,'camera_center_rmse_reference_units':float(np.sqrt(np.mean(errors**2))),'reference_path_length':path,'camera_center_rmse_percent_path':float(np.sqrt(np.mean(errors**2))/path*100),'rotation_median_degrees':float(np.median(angles)),'rotation_max_degrees':float(np.max(angles)),'reference_is_ground_truth':False,'fit':'First-camera orientation + one positive global scale; no per-frame correction'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--aether',type=Path,required=True);p.add_argument('--da3',type=Path,required=True);p.add_argument('--surround',type=Path);p.add_argument('--calibrated',type=Path);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise ValueError('Use a fresh folder')
    a.out.mkdir(parents=True)
    reference=json.loads(a.reference.read_text());frames=reference['frames'][:17]
    ref=np.repeat(np.eye(4)[None],17,axis=0)
    for i,f in enumerate(frames):ref[i,:3,:3]=f['camera_rotation_opencv'];ref[i,:3,3]=f['camera_position']
    manifest={'schema':1,'default':'da3','units':reference['units'],'source':'PandaSet camera RGB; CC BY-SA 4.0 + original Dataset Terms','source_times':'Existing lab nominal filename/10 times, not imported sensor timestamps','reference_is_ground_truth':False,'display_far':80.,'frames':frames,'vehicle':reference['vehicle'],'models':[]}
    cases=[('da3',a.da3,'DA3-BASE · front RGB'),('aether',a.aether,'AetherV1 · front RGB')]
    if a.surround:cases.insert(0,('surround',a.surround,'DA3-BASE · 6 RGB cameras'))
    if a.calibrated:cases.insert(0,('calibrated',a.calibrated,'DA3-BASE · RGB/SfM camera priors'))
    for name,folder,label in cases:
        data=np.load(folder/'geometry.npz');receipt=json.loads((folder/'run.json').read_text())
        poses=data['camera_pose']
        multi=name in {'surround','calibrated'}
        if multi:
            _,scale,alignment=align_to_reference(poses[1::6],ref)
            C=poses.copy();R=np.array(alignment['rotation']);C[:,:3,:3]=R[None]@poses[:,:3,:3];C[:,:3,3]=scale*poses[:,:3,3]@R.T+alignment['translation']
        else:C,scale,alignment=align_to_reference(poses,ref)
        rgb=data['observed_rgb'];rgb=(rgb*255).round().astype('uint8') if rgb.max()<=1 else rgb.astype('uint8')
        depth=data['depth']*scale;t,h,w=depth.shape;stride=3 if name=='calibrated' else (2 if multi else 3);offset=.5 if name=='aether' else 0.
        small=depth[:,::stride,::stride].copy();valid=np.isfinite(small)&(small>.1)&(small<80)
        if 'confidence' in data:
            conf=data['confidence'];threshold=np.percentile(conf,15,axis=(1,2))
            valid &= conf[:,::stride,::stride]>=threshold[:,None,None]
        else:threshold=None
        q=np.where(valid,np.clip(np.rint(small/80*65535),1,65535),0).astype('<u2')
        blob=a.out/f'{name}.depth.bin';blob.write_bytes(q.tobytes())
        previews=a.out/name;previews.mkdir()
        for i,im in enumerate(rgb):Image.fromarray(im).save(previews/f'{i:02d}.jpg',quality=86,optimize=True)
        model={'id':name,'label':label,'views_per_frame':6 if multi else 1,'camera_names':['back_camera','front_camera','front_left_camera','front_right_camera','left_camera','right_camera'] if multi else ['front_camera'],'source_shape':[t,h,w],'grid':[q.shape[2],q.shape[1]],'stride':stride,'ray_pixel_offset':offset,'depth_encoding':'uint16 little-endian, camera Z = value/65535*80; 0 = display-filtered','depth_file':blob.name,'depth_sha256':hashlib.sha256(blob.read_bytes()).hexdigest(),'depth_bytes':blob.stat().st_size,'depth_max':80,'camera_to_world':C.tolist(),'intrinsics':data['intrinsics'].tolist(),'rgb':[f'{name}/{i:02d}.jpg' for i in range(t)],'display_valid_fraction':[float(m.mean()) for m in valid],'confidence_filter':'bottom 15th percentile per view' if threshold is not None else 'no model confidence head; finite/range only','alignment':alignment,'inference':receipt['timing'],'geometry_sha256':hashlib.file_digest((folder/'geometry.npz').open('rb'),'sha256').hexdigest(),'run':receipt}
        manifest['models'].append(model)
    if a.surround:manifest['default']='surround'
    if a.calibrated:manifest['default']='calibrated'
    (a.out/'scene.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({m['id']:{'bytes':m['depth_bytes'],'valid':float(np.mean(m['display_valid_fraction'])),'alignment':m['alignment']} for m in manifest['models']},indent=2))


if __name__=='__main__':main()
