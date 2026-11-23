"""Read completed NuRec receipts and prepare an exact export configuration."""
import argparse,json,re,zipfile,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();root=a.root;log=(root/'nurec-train.log').read_text(errors='replace');steps=re.findall(r'Number of training steps:\s*(\d+)',log);timing=re.findall(r'Train elapsed time:\s*([\d.]+) seconds',log);artifacts=list((root/'train-final').rglob('last.usdz'))
if not steps or not timing or len(artifacts)!=1:raise RuntimeError('A completed NuRec model and training summary are required')
artifact=artifacts[0]
with zipfile.ZipFile(artifact) as z:
 (root/'resolved-export.yaml').write_bytes(z.read('parsed_config.yaml'))
 (root/'training-rig.json').write_bytes(z.read('rig_trajectories.json'))
record={'runtime':'NuRec 26.4.149','image':'nvcr.io/nvidia/nre/nre-ga:26.04@sha256:97f43e7130c5636ce3e80ea3184d97f56a87fdd989b05cce42230881dbdea284','preset':'experimental/3dgut/3dgut_colmap','training_steps':int(steps[-1]),'training_seconds':float(timing[-1]),'artifact':str(artifact.relative_to(root)),'artifact_bytes':artifact.stat().st_size,'artifact_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'inputs':'RGB pixels -> COLMAP rig-constrained bundle adjustment -> NCore + RGB-triangulated SfM seed','uses_lidar':False,'uses_source_sensor_poses':False,'uses_source_annotations':False,'scale':'relative camera-height units; not measured meters','timing_scope':'NuRec-reported training elapsed; excludes SfM, initial compilation, reconstruction input conversion, rendering and enhancement'};(root/'nurec-result.json').write_text(json.dumps(record,indent=2)+'\n');print('NUREC_RGB_COMPLETED',record['training_steps'],record['training_seconds'],flush=True)
