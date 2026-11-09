# MCAP / HDF5 / URDF / CAD

[← Catalog](../../README.md) · [한국어](../ko/mcap-hdf5-urdf-cad.md)

These formats and representations carry different Physical AI artifacts. MCAP stores time-stamped messages, HDF5 stores structured numerical data, URDF describes a robot, and CAD describes engineered geometry.

## How it works

| Artifact | What to look for | Typical consumer |
|---|---|---|
| MCAP | Schema and channel records, timestamps, encoded messages, optional indexes | Replay and inspection tools |
| HDF5 | Groups, datasets, dimensions, types and attributes | Training loader or analysis code |
| URDF | Links, joints, limits, inertial, collision and visual properties | ROS model loaders or supported simulation importers |
| CAD | Part geometry, assembly hierarchy, units and engineering tolerances | Asset preparation tools |

## A practical workflow

Record a robot run in MCAP. Align images and joint states using known clock domains. Store selected training tensors with shape and calibration metadata in HDF5. Use the URDF or asset pipeline to interpret joint names and geometry when replaying the episode.

## What to verify

Validate timestamps and schemas before conversion. Check joint order, frame conventions, units and geometry paths separately. Keep source logs so dataset transformations remain reproducible.

## License and availability

Formats and concepts are distinct from implementations. Check the licenses of each library, file, asset, conversion tool and dataset.

## Official references

- [Official technical reference](https://mcap.dev/spec)
- [HDF5 data model](https://www.hdfgroup.org/solutions/hdf5/)
- [ROS URDF parser and model](https://github.com/ros/urdfdom)
- [Related official resource · mcap.dev](https://mcap.dev/)
