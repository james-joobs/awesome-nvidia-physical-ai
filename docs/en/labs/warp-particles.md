# Simulate particle contacts with Warp

## How it works

### Why search only the nearby particles?

Each particle has a position `[x, y, z]` and a velocity. Warp’s DEM example bins the particles into a spatial grid, then searches nearby bins for each particle’s potential contacts. It computes contact forces from the relative positions and motion. GPU kernels compute the forces across particles, then integrate velocity and position over a time step. [Official Warp DEM source](https://github.com/NVIDIA/warp/blob/main/warp/examples/core/example_dem.py)

### Compare the simulation array with the viewer

After copying positions for inspection, the array shape is `[65536, 3]`. One row is one particle, with columns for scene X, Y, and Z. The viewer draws `points[::4]`. Accordingly, the [record](../../../labs/warp-particles/recorded.json) shows `particles: 65536` and `displayed_particles: 16384`.

The script calculates `mean_particle_displacement_m` by finding each particle’s straight-line displacement from its starting position, then averaging. It does not accumulate distance along the full paths. The same calculation runs with the viewer disabled. [Reporting code](../../../labs/warp-particles/run_dem.py)

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
