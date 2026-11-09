# SMPL

[← All projects](../../README.md) · [한국어](../ko/smpl.md) · [Official source](https://smpl.is.tue.mpg.de/) · [Documentation / related project](https://smpl.is.tue.mpg.de/license.html)

A parametric model family for representing human body shape and pose in 3D.

**Availability and terms:** Model data, code, derivatives, research and commercial use may have different terms; consult the exact model license and access conditions.

## Architecture and workflow

```mermaid
flowchart LR
    A["Body shape + pose parameters"] --> B["body model"] --> C["3D mesh"] --> D["downstream analysis"]
```

*Conceptual illustration for this guide; refer to official sources for supported implementations.*

Obtain the applicable model and terms, estimate or supply shape and pose parameters, then generate and inspect the body mesh.

## Use cases

Human motion analysis, animation, and reconstruction research.

## Connections

Body meshes can inform motion capture or retargeting workflows; coordinate systems and embodiment mapping must be handled explicitly.

## Official references

- [Project source](https://smpl.is.tue.mpg.de/)
- [Documentation / related project](https://smpl.is.tue.mpg.de/license.html)
