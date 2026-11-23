"""Extract observed NuRec timing and configuration from a completed local run."""
import json
import os
from pathlib import Path
import re

root=Path(os.environ['REALITY_VIEW_ROOT'])
log=(root/'nurec-train.log').read_text(errors='replace')
steps=re.findall(r'Number of training steps:\s*(\d+)',log)
timing=re.findall(r'Train elapsed time:\s*([\d.]+) seconds',log)
artifacts=list((root/'train').rglob('last.usdz'))
if not steps or not timing or len(artifacts)!=1:
    raise RuntimeError('A complete training log and exactly one last.usdz are required')
(root/'nurec-result.json').write_text(json.dumps({
    'runtime':'26.4.149','image':'nvcr.io/nvidia/nre/nre-ga:26.04',
    'renderer':'gsplat','training_steps':int(steps[-1]),'training_seconds':float(timing[-1]),
    'timing_scope':'NuRec-reported training elapsed time; excludes environment setup and data preparation',
    'artifact_bytes':artifacts[0].stat().st_size,
},indent=2)+'\n')
print('Collected completed NuRec training metadata')
