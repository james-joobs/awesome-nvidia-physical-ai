# Simulate particle contacts with Warp

## How it works

Checking every pair of particles gets expensive as the number of particles grows. Warp divides space into cells to look for nearby particles. When particles touch, Warp computes the force between them and updates their positions for the next frame.

## Run it

**Before you start** · On an NVIDIA GPU machine, [check that Linux sees the GPU](../onboarding/nvidia-linux.md). Enter this repository in a terminal.

### 1. Install Warp in an isolated Python environment

Run these three lines in the same terminal. The `examples` extra installs the dependencies for the example and viewer.

```sh
python3 -m venv .venv-warp
source .venv-warp/bin/activate
python -m pip install "warp-lang[examples]==1.17.0"
```

### 2. Move the particles and read the report

Run the first command below on a machine with a display. If you connected without a desktop, add `--headless` to the first line. The GPU still computes the simulation. When it finishes, run the second command to format the report in your terminal.

```sh
python labs/warp-particles/run_dem.py ./runs/warp
python -m json.tool ./runs/warp/result.json
```

`frames` is how many frames Warp computed. The same report gives the number of particles and their mean displacement. [NVIDIA Warp particle example](https://github.com/NVIDIA/warp/blob/main/warp/examples/core/example_dem.py)

## Check the result

The recorded run advanced 65,536 particles across 200 frames, about 3.33 seconds of simulated time. The viewer drew 16,384 particles. The mean displacement was 17.05 m in our setup. The output `result.json` reports the particle count, frame count, measured displacement and timing on your GPU. [Recorded result](../../../labs/warp-particles/recorded.json)
