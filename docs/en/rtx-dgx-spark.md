# RTX / DGX Spark

[← Catalog](../../README.md) · [한국어](../ko/rtx-dgx-spark.md)

RTX spans GPU products used for rendering and accelerated compute. DGX Spark is a standalone system with a GB10 Grace Blackwell processor and unified memory. They occupy different hardware roles in Physical AI development.

![DGX Spark GB10 package](https://www.nvidia.com/content/nvidiaGDC/us/en_US/products/workstations/dgx-spark/_jcr_content/root/responsivegrid/nv_container_5347712/nv_image.coreimg.png/1792558737455/nvidia-gb10-grace-blackwell-superchip-2x.png)

*NVIDIA’s product illustration identifies the GB10 hardware. Software compatibility is documented separately.* [Official figure source](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)

## How it works

An RTX workstation can run compatible simulator and rendering workloads. On DGX Spark, the Arm CPU and Blackwell GPU share system memory, and the software stack is provided as a system image. In either case the application, runtime and model must support the target architecture. A model checkpoint may transfer across machines, while a compiled engine or container image can require rebuilding.

## A practical workflow

Develop a perception model on a supported local system, evaluate its output on fixed test data, and then export the checkpoint or portable graph for target hardware. Measure the deployed pipeline on that target instead of extrapolating from the development machine.

## What to verify

Check instruction architecture, memory capacity and pressure, supported packages and CUDA/runtime versions. For simulator work, check the simulator’s official platform matrix before selecting hardware.

## License and availability

Hardware products, not open-source projects. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Architecture and workflow documentation](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)
- [Related official resource · www.nvidia.com](https://www.nvidia.com/en-us/geforce/graphics-cards/)
