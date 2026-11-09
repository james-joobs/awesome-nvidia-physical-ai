# cuRobo
[← Back to catalog](../../README.md) · [한국어](../ko/curobo.md)

GPU-accelerated inverse kinematics and robot motion planning.

**Official sources:** [Repository](https://github.com/NVlabs/curobo)  
**License and scope:** Repository: Apache-2.0; check terms for specific components distributed with AutoData.

![cuRobo robot collision geometry](https://raw.githubusercontent.com/NVlabs/curobo/main/docs/images/franka_spheres.png)
*Image source: [Repository](https://github.com/NVlabs/curobo)*

## Architecture and workflow

The following is an illustrative workflow, not an official architecture or a claim of automatic integration.

**Robot model + collision geometry + target pose → inverse kinematics and motion planning → collision-checked trajectory**

## Example use case

Plan a robot arm path around obstacles toward a target pose.

## Related technologies

Isaac Sim, AutoData, Isaac ROS.

Check version compatibility, data formats, and model and dependency terms in the official sources for your setup.
