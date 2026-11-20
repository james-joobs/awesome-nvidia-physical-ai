<div align="center">

# Awesome NVIDIA Physical AI

**English** · [한국어](README.ko.md)

<img src="assets/social-preview.jpg" alt="Awesome NVIDIA Physical AI · Simulation, robotics, and world models" width="460">

**Free, hands-on NVIDIA Physical AI learning for developers.**

Explore robotics, physics engines, world models and autonomous driving through real experiments. Inspect the inputs and outputs, then run the included code and USD scenes.

[Robotics](https://james-joobs.github.io/awesome-nvidia-physical-ai/topics/robotics/) · [Physics engines](https://james-joobs.github.io/awesome-nvidia-physical-ai/topics/simulation/) · [3D worlds & world models](https://james-joobs.github.io/awesome-nvidia-physical-ai/topics/world-models/) · [Autonomous driving](https://james-joobs.github.io/awesome-nvidia-physical-ai/topics/autonomous-driving/)

[🧪 **First exercise**](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/gr00t-placement/#first-exercise) · [📖 **Learning paths**](https://james-joobs.github.io/awesome-nvidia-physical-ai/#workflows) · [**How the tools work**](https://james-joobs.github.io/awesome-nvidia-physical-ai/learn/principles/) · [🎬 **Lab gallery by topic**](https://james-joobs.github.io/awesome-nvidia-physical-ai/topics/)

[GitHub Pages](https://james-joobs.github.io/awesome-nvidia-physical-ai/) · [Site tour video](https://james-joobs.github.io/awesome-nvidia-physical-ai/tour/) · [Lab code](labs/README.md) · [Tool catalog](CATALOG.md)

</div>

## 16 Isaac Sim scenes

[![Animated preview of 16 scenes recorded in Isaac Sim. GR00T puts the cube in the bowl in the first tile.](assets/showcase/isaac-sim-grid.gif)](https://james-joobs.github.io/awesome-nvidia-physical-ai/showcase/)

`Isaac Sim` · `PhysX` · `GR00T` · `Replicator` · `cuRobo` · `AutoData`

[Watch the full video gallery](https://james-joobs.github.io/awesome-nvidia-physical-ai/showcase/) · [Try the interactive walkthrough](https://james-joobs.github.io/awesome-nvidia-physical-ai/#repo-tour)

## From tool concepts to labs

The [theory guides](https://james-joobs.github.io/awesome-nvidia-physical-ai/learn/principles/) include diagrams and data examples. Pick a field for its full reading order, then try the linked exercise.

- **[Setup](https://james-joobs.github.io/awesome-nvidia-physical-ai/learn/principles/#setup)** — NVIDIA Linux → Isaac Sim GUI and CLI. Then [open and play a USD scene](https://james-joobs.github.io/awesome-nvidia-physical-ai/workflows/isaac-sim-first-cube/#open-the-scene).
- **[Physics and simulation](https://james-joobs.github.io/awesome-nvidia-physical-ai/learn/principles/#simulation)** — Isaac Sim and a cube drop → PhysX and SimReady → Newton and Warp. Then [compare colliders, friction, and bounce](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/physics/#run).
- **[3D assets and synthetic data](https://james-joobs.github.io/awesome-nvidia-physical-ai/learn/principles/#synthetic-data)** — OpenUSD and CAD → Replicator → RGB-D reconstruction. Then [check a saved camera dataset without a GPU](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/workbench-capstone/#check-recording).
- **[Robotics and control](https://james-joobs.github.io/awesome-nvidia-physical-ai/learn/principles/#robotics)** — Isaac Lab and Arena → GR00T → motion planning, demonstrations, and learning. Then [score a GR00T trial in your browser](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/gr00t-placement/#first-exercise).
- **[Autonomous driving](https://james-joobs.github.io/awesome-nvidia-physical-ai/learn/principles/#autonomous-driving)** — [CARLA ego cameras](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/carla-ego/) → Alpamayo outputs → AlpaSim → AlpaGym and Cosmos RL. Start with four recorded road environments.
- **[3D worlds and rendering](https://james-joobs.github.io/awesome-nvidia-physical-ai/learn/principles/#world-models)** — [Generate a 3D world from text or an image](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/worldgen-scenes/) → [drive a robot inside it](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/worldgen-isaac/) → [navigate from sensor scans](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/worldgen-navigation/) → [Explore an fVDB 3DGS plaza](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/spatial-reconstruction/) → [generate a furnished house](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/scene-generation/). Compare [Marble, Lyra and reconstruction workflows](https://james-joobs.github.io/awesome-nvidia-physical-ai/tools/spatial-worlds/); Cosmos video generation is a separate output.

## Quick start

Replay the GR00T result check with Python. It reads the bundled Arena report and prints when each trial lifted the cube and whether it ended up in the bowl. No GPU or Isaac Sim installation is needed to read the logs.

```sh
git clone https://github.com/james-joobs/awesome-nvidia-physical-ai.git
cd awesome-nvidia-physical-ai
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-24s.jsonl
```

All three episodes should print `placed no`. Run the same checker on [the second recording](labs/gr00t-placement/recorded-70s.jsonl) to compare. [Lab guide](docs/en/labs/gr00t-placement.md)

## Start with what you want to build

**Setting up your first GPU machine?** [NVIDIA Linux setup](docs/en/onboarding/nvidia-linux.md) · [Isaac Sim GUI and CLI](docs/en/onboarding/isaac-sim-tools.md) · [Workbench capstone with a GPU-free result check](docs/en/labs/workbench-capstone.md)

| Your goal | Where to start | What to check first |
| --- | --- | --- |
| **Learn simulation basics** | [Drop a cube in Isaac Sim](docs/en/workflows/isaac-sim-first-cube.md) | Compare what happens with and without a collider. |
| **Build a scene from CAD** | [Workbench CAD → OpenUSD → Isaac Sim](docs/en/workflows/workbench-cad-to-isaac-sim.md) | Check tabletop dimensions and see whether the cube rests on it. |
| **Render labeled camera data** | [SimReady](docs/en/simready.md) → [Isaac Sim](docs/en/isaac-sim.md) → [Replicator](docs/en/replicator.md) | Export RGB, depth, and a segmentation mask for the same frame. |
| **Evaluate a driving policy** | [AlpaSim closed-loop walkthrough](docs/en/workflows/alpasim-closed-loop.md) | Review driving video, collision metrics, and off-road events. |
| **Test a robot policy** | [Choose and evaluate a robot foundation model](docs/en/robot-foundation-models.md) | Match a checkpoint to a robot or benchmark and record a baseline run. |

**From simulation to a real robot.** Follow the [Microduck guide](docs/en/microduck.md) to see how Isaac Lab and Newton are used to train a walking policy. [Try the browser simulator](https://huggingface.co/spaces/pollen-robotics/microduck-simulator).

## Ecosystem at a glance

A workbench from CAD can become a reusable simulation scene and a source of labeled camera data. The map traces that path alongside driving evaluation from recorded logs and robot learning from demonstrations.

![Three NVIDIA Physical AI workflows. Build a simulation scene from CAD, evaluate a policy using reconstructed driving data, or train a robot policy from demonstrations.](assets/ecosystem/physical-ai-ecosystem.en.svg)

## Explore the ecosystem

<a name="1-projects-with-confirmed-open-source-code"></a>
<a name="data-and-simulation-assets"></a>
<a name="nemo-and-physical-ai-tooling"></a>
<a name="recent-upstream-releases"></a>
<a name="2-platforms-models-products-standards-and-restricted-code"></a>
<a name="3-external-models-and-tools"></a>
<a name="4-how-the-pieces-fit-together"></a>
<a name="robot-foundation-models-and-vlas"></a>

| Area | Guides to start with | Catalog section |
| --- | --- | --- |
| **Physics, 3D, and simulation** | [OpenUSD](docs/en/openusd.md) · [Isaac Sim](docs/en/isaac-sim.md) · [Newton](docs/en/newton.md) | [Simulation tools](CATALOG.md#physics-3d-and-simulation) |
| **Robot learning and control** | [Isaac Capture](docs/en/isaac-capture.md) · [Isaac Lab](docs/en/isaac-lab.md) | [Robotics tools](CATALOG.md#robot-learning-capture-and-control) |
| **Data and simulation assets** | [SimReady](docs/en/simready.md) · [Video to Data](docs/en/video-to-data.md) · [AutoData](docs/en/autodata.md) | [Datasets and assets](CATALOG.md#data-and-simulation-assets) |
| **Robot foundation models** | [GR00T](docs/en/groot-model.md) · [Physical Intelligence π](docs/en/physical-intelligence-pi.md) | [Robot models and VLAs](CATALOG.md#robot-foundation-models-and-vlas) |
| **Autonomous driving** | [NuRec](docs/en/nurec.md) · [Alpamayo](docs/en/alpamayo.md) · [AlpaSim](docs/en/alpasim.md) | [Driving tools](CATALOG.md#autonomous-driving) |
| **World models and NeMo** | [Cosmos](docs/en/cosmos.md) · [NeMo Curator](docs/en/nemo-curator.md) · [NeMo Switchyard](docs/en/nemo-switchyard.md) | [NeMo and Physical AI tooling](CATALOG.md#nemo-and-physical-ai-tooling) |

The catalog links to official sources and records license terms and availability. Open-source rows also show recent commits for the linked repositories.

[📚 Full Markdown catalog](CATALOG.md) · [🔎 Search and filter on Pages](https://james-joobs.github.io/awesome-nvidia-physical-ai/catalog/) · [📰 Upstream releases](CATALOG.md#recent-upstream-releases)

[🤝 Contributing](CONTRIBUTING.md) · [📄 MIT License](LICENSE) · [🖼️ Third-party credits](NOTICE.md) · [🏷️ Latest repository release](https://github.com/james-joobs/awesome-nvidia-physical-ai/releases/latest)
