"""Create the pilot's STEP file and tessellate the re-imported solids."""
import argparse
import json
from pathlib import Path

import cadquery as cq
from cadquery import exporters, importers

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
folder = parser.parse_args().output
folder.mkdir(parents=True, exist_ok=True)
def box(w, d, h, x, y, z, bevel=0):
    part = cq.Workplane("XY").box(w, d, h)
    if bevel:
        part = part.edges("|Z").fillet(bevel)
    return part.val().translate((x, y, z))

parts = [
    box(1200, 600, 40, 0, 0, 780, 9),
    box(1000, 510, 22, 0, 0, 124, 6),
]
parts.extend(box(48, 48, 758, x, y, 379, 4) for x in (-516,516) for y in (-224,224))
parts.extend(box(1032, 29, 41, 0, y, 721, 4) for y in (-224,224))
parts.extend(box(29, 448, 41, x, 0, 721, 4) for x in (-516,516))
step = folder / "workbench.step"
exporters.export(cq.Compound.makeCompound(parts), str(step))

solids = importers.importStep(str(step)).solids().vals()
assert len(solids) == len(parts)
top = max(solids, key=lambda solid: solid.Center().z)
size = top.BoundingBox()
assert abs(size.xlen-1200) < 0.01 and abs(size.ylen-600) < 0.01 and abs(size.zlen-40) < 0.01
result = []
for number, solid in enumerate(solids):
    name = "Tabletop" if solid is top else "Shelf" if abs(solid.Center().z-124)<1 else f"Frame_{number:02d}"
    vertices, triangles = solid.tessellate(0.7)
    result.append({"name":name, "points":[[u/1000 for u in v.toTuple()] for v in vertices],
                   "indices":[index for face in triangles for index in face]})
(folder/"cad_meshes.json").write_text(json.dumps(result))
print(f"STEP round trip: {len(solids)} solids")
print(f"Measured tabletop (mm): {size.xlen:.2f} x {size.ylen:.2f} x {size.zlen:.2f}")
print(f"STEP: {step.name} | tessellated points: {sum(len(m['points']) for m in result)}")
