"""Recover intrinsics, camera poses and sparse 3D using only RGB image matches."""
import argparse,hashlib,json,time
from pathlib import Path
import pycolmap as c
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--features',type=int,default=4096);p.add_argument('--device',choices=['auto','cpu','cuda'],default='auto');a=p.parse_args();r=a.root;start=time.perf_counter()
from input_guard import verify_rgb_inputs
manifest=verify_rgb_inputs(r);listed={row['image'] for row in manifest['images']}
db=r/'database.db';device=getattr(c.Device,a.device);ex=c.FeatureExtractionOptions();ex.max_image_size=1024;ex.num_threads=8;ex.sift.max_num_features=a.features
c.extract_features(str(db),str(r/'images'),camera_mode=c.CameraMode.PER_FOLDER,camera_model='SIMPLE_RADIAL',extraction_options=ex,device=device)
print('SIFT_COMPLETE',round(time.perf_counter()-start,2),flush=True)
mt=c.FeatureMatchingOptions();mt.num_threads=8;mt.max_num_matches=8192;mt.guided_matching=True
c.match_exhaustive(str(db),matching_options=mt,device=device)
print('MATCHING_COMPLETE',round(time.perf_counter()-start,2),flush=True)
options=c.IncrementalPipelineOptions();options.num_threads=8;options.ba_refine_focal_length=True;options.ba_refine_extra_params=True
(r/'sparse').mkdir(exist_ok=True)
models=c.incremental_mapping(str(db),str(r/'images'),str(r/'sparse'),options=options)
if not models:raise RuntimeError('RGB-only SfM could not register a connected scene; capture more overlapping views')
model=max(models.values(),key=lambda m:m.num_reg_images())
if model.num_reg_images()<len(listed)*.8:raise RuntimeError('Fewer than 80% of RGB images registered in one scene. Capture more overlap.')
# Returned model IDs need not match the output directory ordering. Export the
# selected in-memory reconstruction to an independent folder in binary AND text.
selected=r/'sfm-selected';selected.mkdir(exist_ok=True);model.write(str(selected));model.write_text(str(selected))
report={'pycolmap':c.__version__,'cuda_build':bool(c.has_cuda),'device':a.device,'input_images':len(listed),'registered_images':model.num_reg_images(),'sparse_points':model.num_points3D(),'mean_reprojection_error_px':model.compute_mean_reprojection_error(),'elapsed_seconds':time.perf_counter()-start,'selected_model':'sfm-selected','intrinsics':'estimated from RGB, SIMPLE_RADIAL shared per image folder','camera_poses':'estimated by COLMAP SfM; no dataset poses, GPS, IMU or LiDAR','scale':'arbitrary SfM units before explicitly labeled display normalization'}
(r/'sfm-result.json').write_text(json.dumps(report,indent=2)+'\n');print('SFM_COMPLETE',report,flush=True)
und=c.UndistortCameraOptions();und.max_image_size=1024
c.undistort_images(str(r/'undistorted'),str(selected),str(r/'images'),undistort_options=und)
# 3DGRUT expects the COLMAP sparse/0 layout; keep the MVS root model too.
normalized=r/'undistorted/sparse/0';normalized.mkdir(exist_ok=True);undistorted=c.Reconstruction(str(r/'undistorted/sparse'))
if undistorted.num_reg_images()!=model.num_reg_images():raise RuntimeError('Undistorted model does not match the selected RGB reconstruction')
undistorted.write(str(normalized))
print('UNDISTORTED',flush=True)
