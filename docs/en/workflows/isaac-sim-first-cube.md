# Your first Isaac Sim scene with one falling cube

**English** · [한국어](../../ko/workflows/isaac-sim-first-cube.md) · [Isaac Sim guide](../isaac-sim.md)

Drop the same cube twice. A rigid body falls under gravity. Adding a collider lets it make contact with the floor. This exercise uses built-in geometry and the default PhysX workflow.

## Open the practice scene

1. Download [`cube-drop.usda`](../../../assets/lessons/isaac-sim-first-cube/cube-drop.usda) using GitHub’s **Raw** or download button. The scene is a single file with no external assets.
2. Open it in Isaac Sim. For a fixed comparison view, select **LessonCamera** from the viewport camera menu.
3. Select **World** in the Stage panel and find the `collider` variant set in Properties. While stopped, choose **WithoutCollider** and press **Play**. The green cube falls through the gray floor.
4. Stop, change the variant to **WithCollider**, and press **Play** again. The cube settles on the floor. If the scene has retained the previous pose, reopen the file and select the variant before playing.

The two variants use the same starting height, floor, camera, and gravity. Only the cube’s collider changes.

**Verified on RTX 5090 with Isaac Sim 6.2.0.** After 2.5 seconds of headless PhysX simulation, the cube passed below the floor without a collider. With the collider enabled, its center settled at 0.50 m above the floor.

## Build the scene yourself

1. Start with a new stage and add a ground plane. Create an Xform above it and put a Cube inside the Xform.
2. Apply **Rigid Body** to the parent Xform. Play once and stop.
3. Apply **Collider** to the child cube. Play again and compare. The ground plane already has a collision shape.
4. Stop and save your stage as `.usda` so you can reopen it with the same starting pose.

[Isaac Sim 6.2 physics fundamentals](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/physics/simulation_fundamentals.html#simulation-components)

## Choose an execution environment

- **RTX workstation:** Run Isaac Sim on a supported Windows or Linux host. [System requirements](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html)
- **Mac with a remote RTX server:** Run Isaac Sim on the server and use the macOS WebRTC client or a privately deployed browser viewer. [Livestream clients](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/manual_livestream_clients.html)
- **No local GPU:** The official Isaac Launchable runs on a billed Brev GPU instance and streams to a browser. Its preconfigured Isaac Sim version can differ from the version in this guide. [Isaac Launchable](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_advanced_cloud_setup_launchable.html) · [Brev instance costs](https://docs.nvidia.com/brev/concepts/gpu-instances)

Next, replace the plane with a measured workbench asset. [Workbench CAD to Isaac Sim](workbench-cad-to-isaac-sim.md)
