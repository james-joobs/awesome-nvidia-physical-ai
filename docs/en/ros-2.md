# ROS 2

[← All projects](../../README.md) · [한국어](../ko/ros-2.md) · [Official source](https://docs.ros.org/en/rolling/) · [Documentation / related project](https://docs.ros.org/en/rolling/)

A collection of software libraries and tools for building distributed robot applications.

**Availability and terms:** ROS 2 package and distribution licenses vary; check each dependency and any binary runtime.

## Architecture and workflow

```mermaid
flowchart LR
    A["Sensors / nodes"] --> B["topics and services"] --> C["robot processing"] --> D["commands"]
```

*Conceptual illustration for this guide; refer to official sources for supported implementations.*

Create nodes for sensing and control, exchange messages through ROS interfaces, inspect the system, and connect to robot or simulated devices.

## Use cases

Integrate a robot camera, localization, mapping and motion-control stack.

## Connections

Isaac ROS provides GPU-accelerated ROS 2 packages; Isaac Sim offers ROS integration. Middleware messages and device interfaces must be configured appropriately.

## Official references

- [Project source](https://docs.ros.org/en/rolling/)
- [Documentation / related project](https://docs.ros.org/en/rolling/)
