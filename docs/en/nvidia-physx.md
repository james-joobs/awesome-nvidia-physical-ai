# NVIDIA PhysX

[← All projects](../../README.md) · [한국어](../ko/nvidia-physx.md) · [Official source](https://github.com/NVIDIA-Omniverse/PhysX) · [Documentation](https://nvidia-omniverse.github.io/PhysX/physx/5.4.0/docs/RigidBodyDynamics.html)

A physics simulation SDK for rigid bodies, collisions, constraints, and articulated systems.

**License:** BSD-3-Clause for the PhysX SDK; check additional components separately. Check the exact release, assets, models, and dependencies before use.



## Architecture

A scene contains simulation objects and is stepped forward in time. PhysX also offers GPU rigid-body capabilities on supported configurations.

```mermaid
flowchart LR
    A["Bodies and shapes"] --> B["collision and constraints"] --> C["physics step"] --> D["updated states"]
```

*Conceptual workflow created for this guide; consult the official documentation for implementation details.*

## Workflow

Create a scene with shapes, rigid bodies, joints and material properties; advance time; use the resulting states and contacts in an application.

## Use cases

Simulate robotic arms and object interactions, test collision behavior, or build interactive 3D environments.

## Connections

Isaac Sim uses physics simulation in an OpenUSD-based environment. PhysX is the solver/SDK layer, while OpenUSD describes the scene.

## Official references

- [Project repository](https://github.com/NVIDIA-Omniverse/PhysX)
- [Documentation](https://nvidia-omniverse.github.io/PhysX/physx/5.4.0/docs/RigidBodyDynamics.html)
