# From a CAD workbench to sensor data

## How it works

CadQuery creates and reopens a STEP assembly. The re-imported solids are tessellated in meters and used to author an OpenUSD workbench. PhysX drops a cube onto the tabletop. Replicator produces color, depth and segmentation from the inspection camera. The point-cloud code back-projects depth from the masked cube pixels into world coordinates. [Workstation stage](../../../labs/scene-to-data/workbench_scene.usda) · [Point-cloud replay](../../../labs/scene-to-data/rgbd-surface.usda)

## Run it

You can run the point-cloud measurement anywhere with Python, NumPy and `usd-core`. Download the [four camera captures](../../../labs/scene-to-data/replicator-data.zip) and extract them beside `workbench_scene.usda` in your run directory.

```sh
mkdir -p ./runs/cad
cp labs/scene-to-data/workbench_scene.usda ./runs/cad/
unzip labs/scene-to-data/replicator-data.zip -d ./runs/cad
python labs/scene-to-data/backproject.py ./runs/cad ./runs/point-cloud
```

For new renders, run the first line in a CadQuery environment and the second with Isaac Sim 6.2 on a machine with an RTX GPU and a display. The third line checks the new captures.

```sh
python labs/scene-to-data/make_step.py ./runs/cad-new
python labs/scene-to-data/workbench_final_take.py ./runs/cad-new/cad_meshes.json ./runs/cad-new
python labs/scene-to-data/backproject.py ./runs/cad-new ./runs/point-cloud-new
```

The [Replicator lab](replicator-outputs.md) covers the separate twelve-frame randomization shown in this grid.

## Check the result

The STEP round trip checks a 1,200 × 600 × 40 mm tabletop. In our run the cube center stopped at 0.8615 m. The four recorded point clouds recovered relative X displacement with a maximum error of about 5.3 mm. It compares the visible surface to the first frame, so the measurement describes movement of the surface rather than absolute cube-center position. [Recorded measurements](../../../labs/scene-to-data/recorded.json)
