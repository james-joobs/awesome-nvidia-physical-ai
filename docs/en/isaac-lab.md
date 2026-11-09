# Isaac Lab
[← Back to catalog](../../README.md) · [한국어](../ko/isaac-lab.md)

Robot-learning environments for reinforcement and imitation learning.

**Official sources:** [Repository](https://github.com/isaac-sim/IsaacLab)  
**License and scope:** BSD-3-Clause; backends and dependencies have separate terms.

![Isaac Lab robot learning simulation](https://raw.githubusercontent.com/isaac-sim/IsaacLab/main/docs/source/_static/isaaclab.jpg)
*Image source: [Repository](https://github.com/isaac-sim/IsaacLab)*

## Architecture and workflow

The following is an illustrative workflow, not an official architecture or a claim of automatic integration.

**Robot and task definition → observations and rewards → parallel simulation → policy training and evaluation**

## Components and official architecture

![Isaac Lab backend architecture](https://raw.githubusercontent.com/isaac-sim/IsaacLab/main/docs/source/_static/concepts/backend-architecture-light.svg)

*Image source: [Official repository](https://github.com/isaac-sim/IsaacLab)*

The task API describes robots, environments, observations, actions and learning. Backend extensions connect this interface to different physics and rendering implementations. A compatible Isaac Sim installation is needed only for workflows that use that backend; Newton-backed workflows can run without it. Choose the backend and training framework supported by the version in use.

## Example use case

Train manipulation or locomotion policies with reinforcement or imitation learning.

## Related technologies

Isaac Sim, Newton, Isaac Lab-Arena.

Check version compatibility, data formats, and model and dependency terms in the official sources for your setup.
