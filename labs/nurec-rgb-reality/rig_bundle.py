"""Constrain the RGB-estimated cameras to a fixed rig with COLMAP bundle adjustment.

Uses camera folder/stem grouping as a nominal synchronization assumption. No
provided calibration, timestamps, GPS, LiDAR or object labels enter the solver.
"""
import argparse,json,shutil,time
from pathlib import Path
import pycolmap as c
p=argparse.ArgumentParser();p.add_argument('--rgb-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();src=a.rgb_root;out=a.output;out.mkdir(parents=True,exist_ok=True);start=time.perf_counter();m=c.Reconstruction(str(src/'work/undistorted/sparse/0'));before=m.compute_mean_reprojection_error();groups={im.name.split('/')[0] for im in m.images.values()};expected={'front_camera','front_left_camera','front_right_camera','left_camera','right_camera','back_camera'}
if groups!=expected:raise ValueError('This six-camera example needs front_camera, front_left_camera, front_right_camera, left_camera, right_camera and back_camera folders. Use an explicit adapter for another layout.')
shutil.copy2(src/'work/database.db',out/'database.db');config=c.RigConfig(cameras=[c.RigConfigCamera(image_prefix=f'{cam}/',ref_sensor=cam=='front_camera') for cam in ['front_camera','front_left_camera','front_right_camera','left_camera','right_camera','back_camera']])
with c.Database.open(str(out/'database.db')) as db:c.apply_rig_config([config],db,m)
options=c.BundleAdjustmentOptions();options.refine_focal_length=False;options.refine_principal_point=False;options.refine_extra_params=False;options.refine_sensor_from_rig=True;options.use_gpu=False;options.solver_options.num_threads=8;options.solver_options.max_num_iterations=200;options.solver_options.function_tolerance=1e-6;options.solver_options.parameter_tolerance=1e-6;options.loss_function_type=c.LossFunctionType.CAUCHY;options.loss_function_scale=2
c.bundle_adjustment(m,options);target=out/'work/undistorted/sparse/0';target.mkdir(parents=True,exist_ok=True);m.write(str(target));m.write_text(str(target));(out/'work/undistorted/images').symlink_to((src/'work/undistorted/images').resolve(),target_is_directory=True);(out/'work/images').symlink_to((src/'work/images').resolve(),target_is_directory=True);shutil.copy2(src/'work/input-manifest.json',out/'work/input-manifest.json')
report={'input_images':m.num_reg_images(),'points':m.num_points3D(),'rig_frames':m.num_frames(),'rigs':m.num_rigs(),'reprojection_before_px':before,'reprojection_after_px':m.compute_mean_reprojection_error(),'elapsed_seconds':time.perf_counter()-start,'constraints':'one fixed six-camera rig; folder/stem nominal time pairing; RGB-derived intrinsics frozen; no source sensor calibration or pose labels'};(out/'rig-bundle-result.json').write_text(json.dumps(report,indent=2)+'\n');print('RGB_RIG_BUNDLE_COMPLETE',report,flush=True)
