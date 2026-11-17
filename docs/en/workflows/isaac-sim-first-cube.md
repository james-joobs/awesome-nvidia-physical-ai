# Your first Isaac Sim scene with one falling cube

**English** · [한국어](../../ko/workflows/isaac-sim-first-cube.md) · [Isaac Sim guide](../isaac-sim.md)

Drop the same cube twice to find out **what makes it move and what lets it touch the floor**. Start with the prepared scene, then build the same setup yourself.

## Why does the same cube pass through the floor in one run?

### USD supplies the starting state and PhysX advances it

In `cube-drop.usda`, `/World/DropBody` is a rigid body. Its translation `(0, 0, 3.5)` sets the initial cube center. With `metersPerUnit = 1`, one coordinate unit equals a meter. `upAxis = "Z"` makes the third coordinate the height. [Lab USD file](../../../assets/lessons/isaac-sim-first-cube/cube-drop.usda)

| Role | Where it is defined |
| --- | --- |
| Visible cube | Size `1` on the child prim `/World/DropBody/Cube`. |
| Moving body | The parent’s `PhysicsRigidBodyAPI`, mass, and initial pose. |
| Contact geometry | The floor collider and the child’s `PhysicsCollisionAPI` in `WithCollider`. |

### Predict its resting height before playing

The top of the floor is at Z=0. A cube one meter tall has its center half a meter above its bottom face. With the collider enabled, expect its center to settle at about **0.5 m**. Gravity still acts when the cube’s collider is disabled, but there is no cube-to-floor contact to resolve. Test that prediction by playing the two variants. [Official simulation components](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/physics/simulation_fundamentals.html#simulation-components)

## Choose an execution environment

If you have never launched the app, start with [Isaac Sim GUI and CLI setup](../onboarding/isaac-sim-tools.md). Check the [system requirements](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html) for an RTX workstation or the [WebRTC setup](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/manual_livestream_clients.html) for a Mac with a remote GPU machine. The [Isaac Launchable](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_advanced_cloud_setup_launchable.html) runs in a browser on a remote GPU. Check the provided version and [GPU charges](https://docs.nvidia.com/brev/concepts/gpu-instances) first.

## Open the practice scene

1. Download [`cube-drop.usda`](../../../assets/lessons/isaac-sim-first-cube/cube-drop.usda). The file contains the shapes the example needs.
2. In Isaac Sim, choose **File → Open**. Select **LessonCamera** from the viewport camera menu so both runs share the same view.
3. Select **World** in **Stage** and find the `collider` variant in **Property**. While stopped, choose **WithoutCollider** and press **Play**. Watch for whether the cube crosses the floor height.
4. Press **Stop**, choose **WithCollider**, and press **Play** again. Compare where the cube stops. If the scene retains the previous pose, reopen the file and select the variant before playing.

The two variants use the same starting height, floor, camera, and gravity. Only the cube’s collider changes.

## Build the scene yourself

1. Start with a new stage and add a ground plane. Create an Xform above it and put a Cube inside the Xform.
2. Apply **Rigid Body** to the parent Xform. Play once and stop.
3. Apply **Collider** to the child cube. Play again and compare. The ground plane already has a collision shape.
4. Stop and save your stage as `.usda` so you can reopen it with the same starting pose.

[Isaac Sim 6.2 physics fundamentals](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/physics/simulation_fundamentals.html#simulation-components)

## Compare the two runs

The cube should pass through the floor with **WithoutCollider** and come to rest on it with **WithCollider**. On the RTX 5090 test in Isaac Sim 6.2.0, the enabled cube’s center settled at 0.50 m above the floor after 2.5 simulated seconds.

Next, replace the plane with a measured workbench asset. [Workbench CAD to Isaac Sim](workbench-cad-to-isaac-sim.md)
