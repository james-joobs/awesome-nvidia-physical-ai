"""Create a labeled quarter-density browser preview; full PLY stays untouched."""
import argparse
import json
from pathlib import Path
import numpy as np
from plyfile import PlyData, PlyElement

p=argparse.ArgumentParser()
p.add_argument('--folder',type=Path,required=True)
a=p.parse_args()
r=json.loads((a.folder/'result.json').read_text())
w,h=r['resolution']
v=PlyData.read(a.folder/'scene.ply')['vertex'].data
assert len(v)==h*w
# Retain one of four panorama pixels and widen its tangent footprint.
small=v.reshape(h,w)[::2,::2].copy().reshape(-1)
for field in ('scale_0','scale_1'): small[field]+=np.log(2.)
PlyData([PlyElement.describe(small,'vertex')],text=False).write(a.folder/'preview.ply')
print(json.dumps({'source_gaussians':len(v),'preview_gaussians':len(small),'method':'2x2 image-grid stride, tangent scales doubled; DC color unchanged'}))
