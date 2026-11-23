"""Run the official, non-temporal Harmonizer TorchScript checkpoint on NuRec frames.

Built on NVIDIA Cosmos. Model weights are obtained separately under the NVIDIA
Open Model License. This is per-frame inference; no temporal coherence is claimed.
Run inside the pinned NuRec runtime, which provides the required TE custom ops.
"""
import hashlib
import json
import os
from pathlib import Path
import time

import numpy as np
from PIL import Image
import torch
import transformer_engine  # registers tex_ts::* TorchScript operations

root = Path(os.environ['REALITY_VIEW_ROOT'])
source = root/'novel'
target = root/'enhanced'
target.mkdir(exist_ok=True)
checkpoint = root/'checkpoints/Harmonizer/harmonizer_nontemporal.pt'
with checkpoint.open('rb') as stream:
    checkpoint_digest = hashlib.file_digest(stream, 'sha256').hexdigest()
if checkpoint_digest != 'ece8e2daa914e8c2a027a2da94e0eb2064491d5b3fd8514009fae9a442e06e90':
    raise ValueError('Harmonizer checkpoint differs from the pinned revision')
# Preserve the original placement of frozen CPU constants and CUDA weight tensors.
# Forcing map_location='cuda' also moves shape/timestep constants and breaks the trace.
model = torch.jit.load(str(checkpoint)).eval().cuda()
files = sorted(source.rglob('*.png'))
if not files:
    raise RuntimeError('Render the novel-view sequence before running Harmonizer')
latencies = []
torch.cuda.reset_peak_memory_stats()
for i, path in enumerate(files):
    rgb = np.array(Image.open(path).convert('RGB').resize((1024,576)))
    x = torch.from_numpy(rgb.copy()).permute(2,0,1)[None,:,None].cuda().float()/127.5-1
    torch.cuda.synchronize()
    start = time.perf_counter()
    with torch.inference_mode(), torch.amp.autocast('cuda', enabled=False):
        y = model(x)
    torch.cuda.synchronize()
    latency = time.perf_counter()-start
    if not torch.isfinite(y).all():
        raise RuntimeError('Harmonizer produced nonfinite values')
    if y.ndim == 5:y=y[:,:,0]
    if tuple(y.shape) != (1,3,576,1024):
        raise RuntimeError(f'Unexpected output shape: {list(y.shape)}')
    result = ((y[0].float().permute(1,2,0).cpu().numpy()+1)*127.5).clip(0,255).astype('uint8')
    Image.fromarray(result).save(target/path.name)
    latencies.append(latency)
    if i%10==0:print(f'HARMONIZER frame {i+1}/{len(files)}: {latency:.3f} s',flush=True)
receipt={'mode':'non-temporal single-frame; no previous-frame conditioning',
 'model_id':'nvidia/Harmonizer','model_revision':'20ca33d4612b1e98e0526b3a7ee604af5b289f58',
 'checkpoint':'harmonizer_nontemporal.pt','checkpoint_sha256':checkpoint_digest,
 'frames':len(files),'resolution':[1024,576],'per_frame_seconds':latencies,
 'median_seconds_excluding_first':float(np.median(latencies[1:])) if len(files)>1 else latencies[0],
 'peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,
 'torch':torch.__version__,'transformer_engine':transformer_engine.__version__,
 'attribution':'Built on NVIDIA Cosmos','weights_license':'NVIDIA Open Model License'}
(root/'harmonizer-result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('HARMONIZER completed',flush=True)
