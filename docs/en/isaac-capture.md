# Isaac Capture (formerly Isaac Teleop)
[← Back to catalog](../../README.md) · [한국어](../ko/isaac-capture.md)

Teleoperation and egocentric capture, recording, and retargeting.

**Official sources:** [Repository](https://github.com/NVIDIA/IsaacCapture)  
**License and scope:** Apache-2.0 by default; EgoPost uses OpenMDW-1.1, while CloudXR and some optional packages have separate proprietary terms.

![Isaac Capture architecture diagram](https://media.githubusercontent.com/media/NVIDIA/IsaacCapture/main/docs/source/_static/isaac-capture-architecture.png)
*Image source: [Repository](https://github.com/NVIDIA/IsaacCapture)*

## Architecture and workflow

The following is an illustrative workflow, not an official architecture or a claim of automatic integration.

**Input device → retargeting → simulated or real robot → record and replay demonstrations**

## Components and official architecture

![Isaac Teleop architecture](https://raw.githubusercontent.com/NVIDIA/IsaacCapture/main/docs/source/_static/isaac-teleop-architecture.svg)

*Image source: [Official repository](https://github.com/NVIDIA/IsaacCapture)*

The shared core provides device plugins, retargeters and recording utilities. Isaac Teleop runs robot-in-the-loop capture; the separate Ego Pipeline captures egocentric observations and reconstructs hand and camera poses. Retargeting maps human input into a robot control representation, subject to device and embodiment support.

## Example use case

Record teleoperated robot demonstrations; the Ego Pipeline also captures egocentric human data without a robot.

## Related technologies

Isaac Lab, LeRobot, Isaac GR00T.

Check version compatibility, data formats, and model and dependency terms in the official sources for your setup.
