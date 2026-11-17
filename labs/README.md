# Hands-on labs from the video gallery

[한국어](README.ko.md) · [Video gallery](https://james-joobs.github.io/awesome-nvidia-physical-ai/showcase/)

Start with the video that interests you. Each lab explains what ran, gives the commands and code, and shows the measurements recorded for the video.

**Start here for an end-to-end project.** [Workbench CAD → Isaac Sim → Replicator](../docs/en/labs/workbench-capstone.md) includes the setup, capture code, and CPU-only replay check.

```sh
git clone https://github.com/james-joobs/awesome-nvidia-physical-ai.git
cd awesome-nvidia-physical-ai
```

| Lab | Tools used | First thing to try |
| --- | --- | --- |
| [Robot motion](../docs/en/labs/robot-motion.md) | cuRobo, AutoData, MimicGen, Isaac Lab, Newton, GR00T | Compare the two Franka path replays. |
| [Physics](../docs/en/labs/physics.md) | Isaac Sim, PhysX, OpenUSD, SimReady, Newton | Open the collider-offset scene and press Play. |
| [CAD to sensor data](../docs/en/labs/scene-to-data.md) | CadQuery, OpenUSD, Isaac Sim, PhysX, Replicator | Measure cube displacement from the included camera data. |
| [Desk experiments](../docs/en/labs/everyday-robots.md) | Isaac Sim, PhysX, OpenUSD, OpenCV | Replay the alarm, drawer, cleanup or cart. |
| [GR00T placement](../docs/en/labs/gr00t-placement.md) | GR00T N1.6-DROID, Isaac Lab-Arena, Isaac Sim | Run the episode parser on two recorded test logs. |
| [Replicator outputs](../docs/en/labs/replicator-outputs.md) | Isaac Sim, Replicator, OpenUSD | Render twelve matching RGB, depth and mask triplets. |
| [Microduck](../docs/en/labs/microduck.md) | Isaac Lab, Newton, RSL-RL | Train the walking policy and replay the checkpoint. |
| [Warp particles](../docs/en/labs/warp-particles.md) | NVIDIA Warp, CUDA, OpenGL | Run the particle simulation and inspect its metrics. |

From the repository root, `python3 labs/verify.py` checks the included measurements and lab source references without an NVIDIA GPU. Each guide gives the separate runtime requirements for new simulation runs.
