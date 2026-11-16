# Simulate particle contacts with Warp

## How it works

Warp's discrete element method example uses a spatial hash grid to find nearby particles and computes contacts on CUDA. The lab wrapper steps the scene, synchronizes the GPU before timing, checks finite positions, and draws one in four particles with the OpenGL viewer.

## Run it

Use an NVIDIA GPU and install Warp 1.17.0 with the examples dependencies. Run the published wrapper from the repository root. Add `--headless` when you only want to run the computation and save the report.

```sh
python -m pip install "warp-lang[examples]==1.17.0"
python labs/warp-particles/run_dem.py ./runs/warp
```

[NVIDIA Warp DEM source](https://github.com/NVIDIA/warp/blob/main/warp/examples/core/example_dem.py)

## Check the result

The recorded run advanced 65,536 particles across 200 frames, about 3.33 seconds of simulated time. The viewer drew 16,384 particles. The mean displacement was 17.05 m in our setup. The output `result.json` reports the particle count, frame count, measured displacement and timing on your GPU. [Recorded result](../../../labs/warp-particles/recorded.json)
