# Isaac Lab-Arena
[← Back to catalog](../../README.md) · [한국어](../ko/isaac-lab-arena.md)

Composable robot task environments and policy evaluation.

**Official sources:** [Repository](https://github.com/isaac-sim/IsaacLab-Arena)  
**License and scope:** Apache-2.0; Isaac Sim and other dependencies have separate terms.


## Architecture and workflow

The following is an illustrative workflow, not an official architecture or a claim of automatic integration.

**Embodiment + scene + task → compose an environment → run a policy → compare evaluation results**

## Components and official architecture

![Isaac Lab-Arena architecture overview](https://raw.githubusercontent.com/isaac-sim/IsaacLab-Arena/main/docs/images/isaac_lab_arena_arch_overview.png)

*Image source: [Official repository](https://github.com/isaac-sim/IsaacLab-Arena)*

Arena separates a robot embodiment from the scene and task so they can be composed into evaluation environments. A policy is run against a chosen configuration and the resulting metrics can be compared across task and scene variations. The official repository documents available environments and experimental agentic generation.

## Example use case

Compare a manipulation policy across robot embodiments and scene variations.

## Related technologies

Isaac Lab, Isaac Sim, SimReady.

Check version compatibility, data formats, and model and dependency terms in the official sources for your setup.
