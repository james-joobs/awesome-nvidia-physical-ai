"""Export only RGB-derived COLMAP cameras/points for the NuRec container.

No source sensor calibration, poses, timestamps, depth, LiDAR or annotations.
Times are nominal frame-number/capture-fps values, not measured sensor times.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
import numpy as np
import pycolmap
p=argparse.ArgumentParser();p.add_argument('--rgb-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();src=a.rgb_root;out=a.output;out.mkdir(parents=True,exist_ok=True)
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'rgb-reality-view'))
from input_guard import verify_rgb_inputs
verify_rgb_inputs(src/'work');g=json.loads((src/'viewer/cameras.json').read_text());T=np.array(g['world_to_viewer']);scale=np.linalg.norm(T[0,:3]);R=T[:3,:3]/scale;m=pycolmap.Reconstruction(str(src/'work/undistorted/sparse/0'));rows=[]
for im in sorted(m.images.values(),key=lambda im:im.name):
 cam=m.cameras[im.camera_id];M=np.eye(4);M[:3]=im.cam_from_world().matrix();C=np.linalg.inv(M);N=np.eye(4);N[:3,:3]=R@C[:3,:3];N[:3,3]=(T@np.r_[C[:3,3],1])[:3];dest=out/'rgb'/im.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/'work/undistorted/images'/im.name,dest)
 rows.append({'image':im.name,'camera':im.name.split('/')[0],'timestamp_us':1000000+round(int(Path(im.name).stem)/10*1e6),'camera_to_world':N.tolist(),'K':cam.calibration_matrix().tolist(),'width':cam.width,'height':cam.height,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
points=list(m.points3D.values());P=np.array([p.xyz for p in points]);P=(P@R.T)*scale+T[:3,3];colors=np.array([p.color for p in points],dtype=np.uint8);np.savez_compressed(out/'sfm-points.npz',xyz=P.astype('float32'),rgb=colors)
receipt={'schema':1,'input':'RGB-only COLMAP estimates','uses_lidar':False,'uses_supplied_calibration':False,'uses_supplied_poses':False,'uses_supplied_timestamps':False,'uses_source_annotations':False,'units':'relative camera-height units; not measured meters','time_assumption':'nominal 10 Hz source frame numbers; no provided sensor timestamp files used','frames':rows,'sparse_points':len(P),'front_poses':g['frames'],'scale_assumption':g['scale_assumption']}
(out/'rgb-cameras.json').write_text(json.dumps(receipt,indent=2)+'\n');print('EXPORTED_RGB_ONLY',len(rows),'images',len(P),'SfM points',flush=True)
