"""Replace a NuRec artifact's capture path with our held-out calibrated camera poses."""
import copy
import json
import os
from pathlib import Path
import zipfile

import numpy as np

root = Path(os.environ['REALITY_VIEW_ROOT'])
artifacts = list((root/'train').rglob('last.usdz'))
if len(artifacts) != 1:
    raise RuntimeError(f'Expected one completed NuRec artifact, found {len(artifacts)}')
artifact = artifacts[0]
with zipfile.ZipFile(artifact) as archive:
    name = next(n for n in archive.namelist() if n.endswith('rig_trajectories.json'))
    rig = json.loads(archive.read(name))
rows = json.loads((root/'capture/capture.json').read_text())['held_out']
template = copy.deepcopy(rig['rig_trajectories'][0])
sensor = next(iter(template['cameras_frame_timestamps_us']))
times = [r['timestamp_us'] for r in rows]
c2r = np.array(json.loads((root/'prepared.json').read_text())['camera_to_rig'])
poses = np.array([r['camera_to_world'] for r in rows]) @ np.linalg.inv(c2r)
template['cameras_frame_timestamps_us'] = {sensor: [[t,t] for t in times]}
template['lidars_frame_timestamps_us'] = {}
template['T_rig_worlds'] = poses.tolist()
template['T_rig_world_timestamps_us'] = times
if 'cameras_frame_T_rig_worlds' in template:
    template['cameras_frame_T_rig_worlds'] = {sensor: np.repeat(poses[:,None],2,axis=1).tolist()}
if 'cameras_linear_start_frame_indices' in template:
    template['cameras_linear_start_frame_indices'] = {sensor:0}
if 'lidars_linear_start_frame_indices' in template:
    template['lidars_linear_start_frame_indices'] = {}
rig['rig_trajectories'] = [template]
(root/'novel-rig.json').write_text(json.dumps(rig,indent=2)+'\n')
# Store only a task-relative name. A public receipt must not carry machine paths.
(root/'artifact.json').write_text(json.dumps({'artifact':str(artifact.relative_to(root)),
 'novel_views':len(rows),'sensor_id':sensor},indent=2)+'\n')
print(f'NOVEL_TRAJECTORY prepared {len(rows)} calibrated poses',flush=True)
