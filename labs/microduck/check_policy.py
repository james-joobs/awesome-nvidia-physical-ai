"""Run the bundled single-file Microduck ONNX policy on a CPU."""
import hashlib
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort

folder = Path(__file__).resolve().parent
model = folder / 'policy.onnx'
record = json.loads((folder / 'policy-publication.json').read_text())
assert hashlib.sha256(model.read_bytes()).hexdigest() == record['sha256']
session = ort.InferenceSession(str(model), providers=['CPUExecutionProvider'])
assert [(x.name, x.shape) for x in session.get_inputs()] == [('obs', [1, 61])]
rng = np.random.default_rng(42)
for _ in range(20):
    action, = session.run(None, {'obs': rng.standard_normal((1, 61)).astype(np.float32)})
    assert action.shape == (1, 14) and np.isfinite(action).all()
print('Microduck ONNX: 61 observations → 14 joint targets; 20 CPU smoke inputs passed.')
print('Random inputs verify the model interface, not walking performance.')
