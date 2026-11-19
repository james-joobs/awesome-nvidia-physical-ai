# Run and inspect Physical AI labs

[English](README.md) · [한국어](README.ko.md)

This small Python standard-library harness calls the existing lab programs directly. It is inspired by CLI-Anything's command, structured-output and evidence workflow; it is not an upstream CLI-Anything integration. It does not install GPU packages or substitute generated footage for an application recording.

## Start with an environment check

Run these commands from the repository checkout on your Linux GPU machine. Use the Python executable from the environment that already runs the chosen platform. The harness itself needs only Python 3.10 or later.

```bash
python3 labs/cli.py list
python3 labs/cli.py --json doctor physics-friction \
  --python /path/to/isaaclab/.venv/bin/python --ffmpeg /usr/bin/ffmpeg
```

`doctor` checks source files, Python module availability, `nvidia-smi`, and the display/recorder dependencies needed by that scenario. It does not initialize a simulator, download models, accept licenses or prove that a model can load in GPU memory. A failed check exits with status 1.

## Plan, run, verify

```bash
python3 labs/cli.py --json run physics-friction \
  --python /path/to/isaaclab/.venv/bin/python --ffmpeg /usr/bin/ffmpeg \
  --output /tmp/physical-ai/friction-001 --dry-run

python3 labs/cli.py --json run physics-friction \
  --python /path/to/isaaclab/.venv/bin/python --ffmpeg /usr/bin/ffmpeg \
  --output /tmp/physical-ai/friction-001

python3 labs/cli.py --json verify /tmp/physical-ai/friction-001
python3 labs/cli.py --json preview /tmp/physical-ai/friction-001
```

Choose a **new output directory** for each run. `--dry-run` reports the argument array and readiness without creating that directory or running the experiment; its exit status is 0 for a valid plan even when the reported environment is not ready. An actual run with a failed preflight creates a failed run record and exits with status 1. `preview` lists local files and the reported result; it does not open a browser or imply integrity verification.

| Scenario | What runs | Evidence | Additional setup |
|---|---|---|---|
| `physics-friction` | Three bodies slide under different friction settings | Actual Isaac Sim GUI MP4 plus live PhysX positions | Isaac Lab/Isaac Sim, X11 `DISPLAY`, `xwininfo`, ffmpeg |
| `physics-bounce` | Three restitution settings | Actual Isaac Sim GUI MP4 plus live PhysX positions | Same GUI environment |
| `curobo-replan` | Franka baseline and obstacle-aware planning | New JSON result and NPZ trajectories; this command does **not** record a GUI | Compatible cuRobo environment |
| `warp-dem` | 200 frames of GPU particle simulation | Warp OpenGL viewer and JSON measurements; this command does **not** record video | Warp, NumPy, CUDA; `--headless` skips the viewer |
| `newton-materials` | Official XPBD/VBD cloth and cable examples with `--test` | Animated USD and separate review-camera layers; later GUI display is a **replay** | Newton example dependencies, Warp, NumPy, usd-core |
| `cosmos-i2v` | Actual Cosmos backend image-to-video inference | Generated MP4 and upstream success receipt; generation is not physics simulation | Prepared Cosmos checkout, checkpoint and input JSON |
| `alpamayo-synthetic` | Actual Alpamayo inference on synthetic camera frames | Finite predicted trajectory tensors; an interface test, not closed-loop driving | Prepared Alpamayo environment, local weights and input directory |
| `gr00t-placement` | Setup recipe only | No new execution is claimed | [Policy server, model and Arena setup](../../docs/en/labs/gr00t-placement.md) |
| `microduck-walk` | Setup recipe only | No new execution is claimed | [Isaac Lab environment and a trained PT checkpoint](../../docs/en/labs/microduck.md) |

For example, a data-only Warp run uses:

```bash
python3 labs/cli.py --json run warp-dem --headless \
  --python /path/to/warp-env/bin/python --output /tmp/physical-ai/warp-001
```

`PHYSICAL_AI_PYTHON` and `PHYSICAL_AI_FFMPEG` set defaults. `--source /path/to/repo` selects a different checkout; the source registry is `labs/scenarios.json` in that checkout. No shell expansion is used for commands, so supply actual paths rather than strings such as `python -m uv`.

The child process inherits environment variables, including `PYTHONPATH` when a prepared vendor checkout needs it. The harness does not install packages or change that environment. On a shared GPU server, serialize your runs with the same `flock` lock file rather than starting several simulator jobs together.

## Model inputs and prepared backends

These model commands use environments and weights you have already prepared; they do not install a backend or download its checkpoint. Refer to `labs/world-driving/model-pins.json` for the checked source/model revisions.

```bash
python3 labs/cli.py --json run cosmos-i2v \
  --python /path/to/cosmos-framework/.venv/bin/python \
  --backend /path/to/cosmos-framework --input /path/to/workbench-right.json \
  --model /path/to/Cosmos3-Edge --seed 19 --output /tmp/physical-ai/cosmos-001

python3 labs/cli.py --json run alpamayo-synthetic \
  --python /path/to/alpamayo2-edge/.venv/bin/python \
  --input /path/to/synthetic-intersection --model /path/to/Alpamayo2-Edge \
  --seed 19 --output /tmp/physical-ai/alpamayo-001
```

Cosmos input is a JSON file with a local `vision_path`; Alpamayo input is a directory containing `input.json` and its referenced camera images. The harness hashes those input files, records model metadata hashes, lists checkpoint shard sizes, and records available Hugging Face cache revisions and backend Git revision. It does not hash every multi-gigabyte checkpoint shard. A declared reference revision is distinguished from revisions observed in local cache metadata.

The Cosmos adapter starts the selected interpreter in the backend checkout, prepends that interpreter's directory to `PATH` for upstream `uv` subprocesses, and saves the actual backend command. It keeps upstream content filters enabled by default. The explicit Cosmos-only `--no-guardrails` option disables those filters and records that choice in both manifests; it is useful only when intentionally reproducing that configuration on controlled inputs. Default filters may need additional model downloads and GPU memory.

Model completion checks establish that an upstream success receipt and local MP4 exist, or that Alpamayo saved finite trajectory tensors with the expected shapes. They do not establish prompt adherence, realistic dynamics, driving skill or safety.

## What is saved and checked

Each run saves `request.json` before execution, all child stdout/stderr in `run.log`, and a final `run.json` once execution ends. The final record includes the exact command, source SHA-256 hashes, start/end times, process return code, evidence mode, validation and artifact sizes/hashes. Existing run records are never overwritten by the harness. `RUNNING` marks an unfinished attempt; a hard kill can leave it behind without a final manifest.

`verify` checks the recorded artifact list and hashes, then reruns the scenario's output checks. Physics checks compare sampled positions with friction/bounce summaries and require a nontrivial MP4 container. cuRobo checks finite arrays, matching starts/tool goals and sampled tool positions relative to the obstacle; full robot swept-collision validation remains cuRobo's responsibility. Warp checks completion, finite particle displacement and viewer mode. These checks do not independently assess visual composition or model generalization.

The underlying GUI recorder can exit with code 0 after a simulator failure. The harness treats its `capture-failed` marker as failure and preserves that evidence. Review both `run.json` and `run.log` before sharing footage. A local file can still be edited outside this harness; hashes detect artifact changes against the manifest, not malicious edits to the manifest itself.

## Test the harness without a GPU

```bash
python3 -m unittest discover -s labs/cli -p 'test_*.py' -v
```

Tests use explicitly synthetic subprocess outputs, never label them as simulator results, and cover JSON isolation, failed subprocesses, the GUI failure marker, changed artifacts and output-directory reuse.
