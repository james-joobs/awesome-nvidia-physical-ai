# AutoData
[← Back to catalog](../../README.md) · [한국어](../ko/autodata.md)

Expands a small set of demonstrations into trajectories across varied task conditions.

**Official sources:** [Repository](https://github.com/isaac-sim/AutoData)  
**License and scope:** Apache-2.0; Isaac Sim and specific cuRobo components have separate terms.

![AutoData demonstration generation](https://media.githubusercontent.com/media/isaac-sim/AutoData/main/docs/images/autodata.gif)
*Image source: [Repository](https://github.com/isaac-sim/AutoData)*

## Architecture and workflow

The following is an illustrative workflow, not an official architecture or a claim of automatic integration.

**Seed demonstrations → vary task and scene conditions → synthesize trajectories → review and train**

## Components and official architecture

![AutoData system architecture](https://raw.githubusercontent.com/isaac-sim/AutoData/main/docs/images/System_Architecture.svg)

*Image source: [Official repository](https://github.com/isaac-sim/AutoData)*

AutoData starts from a small collection of demonstrations and generates additional robot trajectories under varied task conditions. Simulation and planning dependencies determine which environments and robot configurations can be used. Inspect generated trajectories and success criteria before adding them to a training set.

## Example use case

Expand a small set of demonstrations into varied robot manipulation data.

## Related technologies

Isaac Sim, cuRobo, Isaac Lab.

Check version compatibility, data formats, and model and dependency terms in the official sources for your setup.
