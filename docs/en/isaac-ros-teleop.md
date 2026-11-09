# Isaac ROS Teleop

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-teleop.md)

Isaac ROS Teleop connects an operator’s XR input to supported robot teleoperation bringups.

![Unitree G1 teleoperation demo](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_physical_ai/isaac_ros_unitree_g1_teleop_bringup/unitree-g1-teleop-hero.gif)

*Compare the operator’s arm motion with the humanoid motion. The video shows the application, while the bringup defines the command interfaces.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_teleop/index.html)

## How it works

In the Unitree G1 example, the operator’s XR input is streamed to the application, interpreted as motion intent and converted to robot commands through the bringup. The robot-side controller consumes commands. Camera feedback returns to the operator and lets them correct the motion. Robot-specific mappings and controls are configured with the bringup.

## A practical workflow

Start with the supported simulated robot. Compare neutral poses and slowly move one hand. Check how the controller responds when the hand leaves the tracking volume or the network drops before adapting the setup to hardware.

## What to verify

Confirm versions, mappings, calibration, network latency and any stop or reset behavior. Test command limits and communication-loss handling independently of operator feedback.

## License and availability

Apache-2.0; device software separate.

## Official references

- [Isaac ROS Teleop package documentation](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_teleop/index.html)
- [Related official resource · github.com](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_teleop)
