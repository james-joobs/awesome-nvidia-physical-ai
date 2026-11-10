# Turn a workbench CAD file into an Isaac Sim scene

**English** · [한국어](../../ko/workflows/workbench-cad-to-isaac-sim.md) · [Catalog](../../../README.md#start-with-what-you-want-to-build)

Use one workbench model for two tasks. First convert a STEP file to OpenUSD and check the scene's size and collision geometry. Then either capture labeled camera frames or run a simulated pick-and-place. The conversion and both Isaac Sim baselines are documented upstream. The workbench adaptation below is a community recipe.

## What you need

| Item | Start with |
| --- | --- |
| CAD input | One STEP file with known dimensions. To make your own, create a box measuring 1,200 × 600 × 40 mm in a CAD editor and export it as `workbench.step`. This is enough to represent the tabletop. |
| Conversion | AIF Pipeline Samples at revision `4103896`, configured against a Kit/USD Composer installation with the HOOPS converter. Use the sample setup and record the Kit build it uses. |
| Simulation | Isaac Sim 6.1 documentation is the reference for this guide. Use the requirements and samples for your installed build. A supported Linux or Windows workstation with NVIDIA RTX is the starting point. |
| Additional input for pick-and-place | The URDF, gripper, and sample controller from the official manipulator tutorial. The tabletop is separate from the robot model. |

[AIF setup](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/docs/get-started/setup.md) · [Isaac Sim requirements](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html) · [Workstation installation](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_workstation.html)

## 1. Convert and validate the USD

Check out the sample revision below, then follow the [setup and Kit configuration](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/docs/get-started/quickstart.md) for your machine.

```bash
git clone https://github.com/NVIDIA-Omniverse/aif-pipeline-samples.git
cd aif-pipeline-samples
git checkout 41038967ef0a2459b128a225161f8d59beb3b424
```

From the sample repository root, put the input at `cad_source/workbench.step` and run the converter. The bundled HOOPS preset supports STEP.

```bash
mkdir -p usd_converted validation_reports
uv run aif-pipeline config show
uv run aif-pipeline convert ./cad_source/workbench.step ./usd_converted/workbench.usdc \
  --spec scripts/data/creo_spec.json
uv run aif-pipeline validate ./usd_converted/workbench.usdc ./validation_reports/
```

Open the converted asset and measure the tabletop against the CAD dimensions. For the example input, the expected physical extents are **1.2 × 0.6 × 0.04 m**, regardless of the authored USD units. Check the up axis, prim hierarchy, and missing references in the validation report. Use the sample's optimization step if the assembly needs cleanup or unit and axis normalization. Recheck the measurements after any optimization. [Official CAD-to-USD workflow](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/docs/get-started/cad-to-usd-workflow.md) · [Asset Validator](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/)

## 2. Compose a reusable workbench scene

1. In Isaac Sim, create a stage and reference the converted asset under a prim such as `/World/Workbench`. Check the dimensions and up axis again after composition. Normalize the asset first or apply a corrective transform if its units or axis differ from the scene. Save a separate `workbench_scene.usd` beside the geometry so you can keep conversion output and simulation edits separate.
2. Give the tabletop a static collision shape. For a flat surface, a box collider sized to match the tabletop is enough. Add a small dynamic cube with a collider above it and play the simulation.
3. Confirm that the cube settles on the tabletop rather than falling through, and that the tabletop stays fixed. Save the workbench scene in its initial state so each run starts from the same poses.

This applies SimReady principles to a small scene. Check the relevant SimReady profile separately when a downstream tool requires one. For a digital twin, the same USD reference can be composed into a larger layout with measured dimensions and clearances. [OpenUSD linear units](https://openusd.org/release/api/group___usd_geom_linear_units__group.html) · [Isaac Sim physics fundamentals](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/physics/simulation_fundamentals.html) · [SimReady requirements](https://docs.omniverse.nvidia.com/simready/latest/simready-faq.html)

## 3A. Generate labeled camera data

1. Run the official Replicator scene example with the bundled scene once. Then adapt the example's scene-loading step to reference the local workbench scene and place a camera with the cube in view. Keep the camera fixed for the first test.
2. Give the cube a semantic class such as `part` after any cleanup of existing labels. Capture four frames with `BasicWriter` and enable `rgb`, `distance_to_image_plane` (depth), and `semantic_segmentation`.
3. Open one RGB frame with its corresponding depth and mask. Check that the mask covers the cube and maps to `part`, and that the depth agrees with the camera placement. Only then vary the object pose or lighting.

**Keep** the USD scene, camera pose, writer configuration, and sample output. [Official scene-based Replicator example](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/replicator_tutorials/tutorial_replicator_scene_based_sdg.html)

## 3B. Run a robot pick-and-place

1. Follow the Isaac Sim manipulator tutorial from URDF import through its first successful pick-and-place with the tutorial's robot and scene.
2. Reference the converted tabletop in a copy of the tutorial scene. Align its collider to the expected work surface and remove or disable the original support if it overlaps. Adjust the robot base, pick and place poses, and reach limits relative to the new surface.
3. Reset and repeat with the same starting pose. Check that the gripper lifts the cube, avoids unintended contact with the bench, and releases the cube inside the marked target area. Record the starting poses and count successful runs.

**Keep** the task scene, robot and controller configuration, and a short result log. For camera-based perception or ROS 2 motion planning, build from the supported Isaac ROS reference workflow after the baseline works. [Official URDF-to-pick-and-place tutorial](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/robot_setup_tutorials/tutorial_manipulator_workflow.html) · [Isaac for Manipulation reference architecture](https://nvidia-isaac-ros.github.io/v/release-4.2/reference_workflows/isaac_for_manipulation/reference_architecture.html)

## Related tools and verification

- [OpenUSD](../openusd.md) composes the scene. [OpenUSD Exchange SDK](https://github.com/NVIDIA-Omniverse/usd-exchange) is useful for authoring or adapting an exchange pipeline. [SimFoundry](https://github.com/NVlabs/SimFoundry) is a separate starting point when your input is a tabletop video.
- AIF sample code is MIT. The converter, Kit/Isaac Sim distribution, and any CAD, robot, or asset files have separate terms. [AIF license](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/LICENSE) · [Isaac Sim license scope](../isaac-sim.md)
- **Verification status** · Official examples and command references checked. The combined workbench recipe has yet to be run on a supported RTX workstation.
