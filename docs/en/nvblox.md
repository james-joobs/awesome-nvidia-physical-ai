# nvblox

[← Catalog](../../README.md) · [한국어](../ko/nvblox.md)

Nvblox is a GPU mapping library. The core C++ library operates on geometry and poses, and the Isaac ROS package adds topics, TF and navigation integration.

![Nvblox mapping system diagram](https://media.githubusercontent.com/media/nvidia-isaac/nvblox/public/docs/images/system_diagram.png)

*Use the mapping graph to connect inputs and representations with planner-facing outputs.* [Official figure source](https://github.com/nvidia-isaac/nvblox/tree/public)

![Nvblox distance field example](https://media.githubusercontent.com/media/nvidia-isaac/nvblox/public/docs/images/esdf_example.gif)

*The distance field visualizes proximity to geometry, the quantity a planner can query.* [Official figure source](https://github.com/nvidia-isaac/nvblox/tree/public)

## How it works

Calibrated depth and a camera-to-map transform place measurements in sparse voxel blocks. A TSDF fuses observations near surfaces. A mesher can extract geometry for visualization, and an ESDF represents distances to surfaces for planning. Layer resolution and integration settings govern update cost and map detail.

## A practical workflow

Reconstruct a bench or aisle by feeding depth frames and known poses. Compare the reconstructed mesh with measured dimensions. Inspect a distance-field slice before giving it to a collision planner. Use [Isaac ROS Nvblox](isaac-ros-nvblox.md) when integrating with Nav2.

## What to verify

Check depth scale and pose direction with a single frame. Monitor stale voxels, drift, map bounds and GPU memory as the robot moves. Mesh visual quality and distance accuracy are separate checks.

## License and availability

Source is public; scope of mixed repository licenses unverified. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Nvblox library and layer examples](https://github.com/nvidia-isaac/nvblox/tree/public)
- [Related official resource · github.com](https://github.com/nvidia-isaac/nvblox)
