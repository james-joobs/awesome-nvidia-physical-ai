# Hands-on labs from the video gallery

[한국어](README.ko.md) · [Video gallery](https://james-joobs.github.io/awesome-nvidia-physical-ai/showcase/)

Start with the video that interests you. Each lab explains what ran, gives the commands and code, and shows the measurements recorded for the video.

| Start with a field | Try this first | What you can inspect |
| --- | --- | --- |
| Robotics | [GR00T placement](../docs/en/labs/gr00t-placement.md) and [cuRobo replanning](../docs/en/labs/robot-motion.md) | Camera observations, action chunks, robot paths and placement success. |
| Physics engines | [Newton cloth and cables](../docs/en/labs/newton-materials.md), then [PhysX contact](../docs/en/labs/physics.md) | Vertex positions, deformation, friction and rebound measurements. |
| 3D worlds and world models | [3DGS plaza](../docs/en/labs/spatial-reconstruction.md), [Infinigen house](../docs/en/labs/scene-generation.md), [tool comparison](../docs/en/spatial-worlds.md) | Explore a reconstructed radiance field, inspect generated meshes, then compare Cosmos video output. |
| Autonomous driving | [CARLA ego cameras](../docs/en/labs/carla-ego.md), [Alpamayo](../docs/en/labs/world-driving.md), [AlpaSim](../docs/en/workflows/alpasim-closed-loop.md) | Four road environments, measured trajectories, learned inference and separate policy evaluation. |

[Run and verify with the lab CLI](cli/README.md). The CLI uses real simulator/model backends and records commands, logs and artifact hashes. Each runtime has its own dependencies.

[Explore 12 experiments and their current results](EXPERIMENTS.md) · [Watch four fields on one GPU](../site/public/showcase/four-domain-grid.mp4)

Recreate the labeled comparison video without a GPU (FFmpeg and Pillow required):

```sh
python3 labs/render_grid.py --output ./runs/four-domain-grid.mp4
```

For a scene-building project, [Workbench CAD → Isaac Sim → Replicator](../docs/en/labs/workbench-capstone.md) includes setup, capture code and a CPU-only replay check.

```sh
git clone https://github.com/james-joobs/awesome-nvidia-physical-ai.git
cd awesome-nvidia-physical-ai
```

| Lab | Tools used | First thing to try |
| --- | --- | --- |
| [Robot motion](../docs/en/labs/robot-motion.md) | cuRobo, AutoData, MimicGen, Isaac Lab, Newton, GR00T | Compare the two Franka path replays. |
| [Physics](../docs/en/labs/physics.md) | Isaac Sim, PhysX, OpenUSD, SimReady, Newton | Open the collider-offset scene and press Play. |
| [Newton materials](../docs/en/labs/newton-materials.md) | Newton, Warp, OpenUSD, Isaac Sim | Compute cloth and cable states, then open the review scene in the GUI. |
| [World and driving models](../docs/en/labs/world-driving.md) | Cosmos3-Edge, Alpamayo2-Edge, Isaac Sim | Generate video and inspect 64 predicted vehicle poses with your own input images. |
| [CAD to sensor data](../docs/en/labs/scene-to-data.md) | CadQuery, OpenUSD, Isaac Sim, PhysX, Replicator | Measure cube displacement from the included camera data. |
| [Desk experiments](../docs/en/labs/everyday-robots.md) | Isaac Sim, PhysX, OpenUSD, OpenCV | Replay the alarm, drawer, cleanup or cart. |
| [GR00T placement](../docs/en/labs/gr00t-placement.md) | GR00T N1.6-DROID, Isaac Lab-Arena, Isaac Sim | Run the episode parser on two recorded test logs. |
| [Replicator outputs](../docs/en/labs/replicator-outputs.md) | Isaac Sim, Replicator, OpenUSD | Render twelve matching RGB, depth and mask triplets. |
| [Microduck](../docs/en/labs/microduck.md) | Isaac Lab, Newton, RSL-RL | Train the walking policy and replay the checkpoint. |
| [Warp particles](../docs/en/labs/warp-particles.md) | NVIDIA Warp, CUDA, OpenGL | Run the particle simulation and inspect its metrics. |

From the repository root, `python3 labs/verify.py` checks the included measurements and lab source references without an NVIDIA GPU. Each guide gives the separate runtime requirements for new simulation runs.
