# MoGe

[← All projects](../../README.md) · [한국어](../ko/moge.md) · [Official source](https://github.com/microsoft/MoGe) · [Documentation / related project](https://github.com/microsoft/MoGe)

A Microsoft research model family for estimating 3D geometry from a single image.

**Availability and terms:** Verify code and checkpoint licenses separately for each model version and its dependencies.

## Architecture and workflow

```mermaid
flowchart LR
    A["RGB image"] --> B["geometry model"] --> C["depth / point map"] --> D["geometry review"]
```

*Conceptual illustration for this guide; refer to official sources for supported implementations.*

Run the selected checkpoint on an image, inspect predicted depth or point maps, and export supported geometry outputs. Available outputs depend on model version.

## Use cases

Reconstruct approximate scene geometry or provide spatial cues for downstream visual reasoning.

## Connections

Outputs can contribute to video-to-data or reconstruction workflows; a single-image estimate should be checked for scale and geometry errors.

## Official references

- [Project source](https://github.com/microsoft/MoGe)
- [Documentation / related project](https://github.com/microsoft/MoGe)
