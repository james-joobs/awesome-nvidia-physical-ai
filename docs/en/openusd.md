# OpenUSD

[← All projects](../../README.md) · [한국어](../ko/openusd.md) · [Official source](https://github.com/PixarAnimationStudios/OpenUSD) · [Documentation](https://openusd.org/release/intro.html)

A framework for describing, composing, and exchanging complex 3D scenes and assets.

**License:** Modified BSD-style license for the implementation; standards and trademarks are separate. Check the exact release, assets, models, and dependencies before use.



## Architecture

A stage represents the composed scene graph; layers and composition arcs let teams assemble and override scene data without flattening every contribution.

```mermaid
flowchart LR
    A["Assets and layers"] --> B["composition"] --> C["USD stage"] --> D["compatible applications"]
```

*Conceptual workflow created for this guide; consult the official documentation for implementation details.*

## Workflow

Author reusable assets and layers; compose references and overrides into a stage; exchange the resulting scene with compatible applications.

## Use cases

Organize reusable robot and factory assets, exchange scenes between 3D tools, and assemble simulation environments.

## Connections

SimReady defines conventions for simulation-ready assets; Omniverse and Isaac Sim use OpenUSD-based scene workflows. USD describes scenes and does not itself provide a physics solver.

## Official references

- [Project repository](https://github.com/PixarAnimationStudios/OpenUSD)
- [Documentation](https://openusd.org/release/intro.html)
