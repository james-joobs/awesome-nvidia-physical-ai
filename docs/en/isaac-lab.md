# Isaac Lab

[← Catalog](../../README.md) · [한국어](../ko/isaac-lab.md)

Isaac Lab organizes batched simulation into robot learning environments. It provides task interfaces for observations, actions, rewards and resets, and delegates stepping, articulation state and sensors to the selected backend.

## Architecture

| Component | Responsibility and data boundary |
|---|---|
| `InteractiveScene` and backend | Scene configuration declares assets and sensors and organizes copies across environments. Backend presets determine the physics, rendering and scene tools available to the task. |
| `ManagerBasedRLEnv` | Managers resolve actions into actuator targets and build observations, rewards, terminations and events from task configuration. They let a task reuse terms or change a sensor without rewriting the entire environment. |
| `DirectRLEnv` | Task code supplies explicit routines for applying actions, forming observations and rewards, and resetting environments. This gives the task tighter control of its execution loop. |
| Policy runner | The learning stack consumes the batched environment interface and writes policy checkpoints. The simulator substep and policy step can run at different rates. |

Guide diagram based on the official references below.

```mermaid
flowchart LR
    task["Task terms and scene configuration"]
    env["Isaac Lab environment and scene"]
    sim["Selected simulation backend"]
    policy["Policy or training runner"]
    ckpt["Policy checkpoints and metrics"]
    task --> env
    env --> sim
    sim --> env
    env --> policy
    policy --> env
    policy --> ckpt
```

### Official figures and examples

![Isaac Lab’s official backend diagram explains where backend-specific implementations connect to the environment-facing interfaces.](https://raw.githubusercontent.com/isaac-sim/IsaacLab/main/docs/source/_static/concepts/backend-architecture-light.svg)

Isaac Lab’s official backend diagram explains where backend-specific implementations connect to the environment-facing interfaces. [Original figure and context](https://isaac-sim.github.io/IsaacLab/develop/source/concepts/backends_and_presets.html)

![Isaac Lab project visual with representative simulation tasks. The examples cover different embodiments and environment configurations.](https://raw.githubusercontent.com/isaac-sim/IsaacLab/main/docs/source/_static/isaaclab.jpg)

Isaac Lab project visual with representative simulation tasks. The examples cover different embodiments and environment configurations. [Original figure and context](https://github.com/isaac-sim/IsaacLab)

## Walkthrough

1. Use the manager-based cartpole example to map a state observation and an actuator action. Run a single environment first and inspect reset behavior and joint units.
2. For an arm reach task, replace the scene and define the target-pose observation, joint action and distance reward. Add a termination condition and reset distribution before increasing the number of environments.
3. Replay a checkpoint with fixed seeds, then vary target poses and physical parameters. Evaluate success and action smoothness across held-out conditions before a real robot trial.

## Validation

- Check the backend matrix before swapping PhysX, Newton, or another preset. Availability of sensors, actuators and constraints can differ by backend and release.
- Match observation order, normalization, joint convention and control rate when moving a policy to a new simulation or hardware runner.

## License and scope

Isaac Lab code is BSD-3-Clause. Backends, policy weights and assets have separate terms.

## Related guides

[Isaac Sim](isaac-sim.md) · [Newton](newton.md) · [Isaac Lab-Arena](isaac-lab-arena.md) · [Isaac RLPT](isaac-rlpt.md) · [Microduck](microduck.md)

## Official references

- [Isaac Lab repository](https://github.com/isaac-sim/IsaacLab)
- [Backend options and presets](https://isaac-sim.github.io/IsaacLab/develop/source/concepts/backends_and_presets.html)
- [Manager-based environment tutorial](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/create_manager_rl_env.html)
- [Newton backend interface](https://docs.nvidia.com/isaaclab/concepts/newton)
