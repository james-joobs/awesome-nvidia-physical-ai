"""Blender: export the credited Volvo as a small, actual 3D mesh for the viewer.

Open the author's .blend with --disable-autoexec, then run this script with
-- --output /path/to/volvo-s90.glb. Source model license is CC BY 4.0.
"""
import argparse,json,sys
from pathlib import Path
import bpy
from mathutils import Matrix
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.parent.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
# The actual exterior, wheels and visible interior are retained. Small interior
# trim is omitted; heavy texture graphs are replaced with simple PBR materials.
color_groups={
 'paint':((.63,.69,.74,1),.5,.25),
 'glass':((.09,.16,.20,.38),.1,.15),
 'chrome':((.65,.68,.72,1),.85,.18),
 'rubber':((.016,.020,.025,1),.0,.75),
 'tan':((.42,.28,.15,1),.0,.8),
 'red':((.45,.018,.025,1),.1,.25),
 'dark':((.055,.065,.075,1),.1,.55)}
materials={}
for name,(color,metal,rough) in color_groups.items():
 m=bpy.data.materials.new('Viewer '+name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=color;n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;n.inputs['Alpha'].default_value=color[3]
 if name=='glass':m.surface_render_method='DITHERED'
 materials[name]=m
T=Matrix(((0,-1,0,0),(1,0,0,0),(0,0,1,-.02234119),(0,0,0,1)))
selected=[]
for o in list(scene.objects):
 if o.type!='MESH':continue
 # Remove invisible floor trim and tiny interior controls; no substitute body.
 if any(k in o.name.lower() for k in ['carpet','gas/brake','ceilingconsole','glovebox','shifterknob','knobs','seatbelt','speedoscreen','speedoglass','infotainment','stalks','steeringcolumn']):continue
 o.hide_render=False;o.hide_set(False);o.matrix_world=T@o.matrix_world
 for slot in o.material_slots:
  n=slot.material.name.lower() if slot.material else ''
  group='paint' if 'paint' in n else 'glass' if 'glass' in n or 'crystal' in n else 'chrome' if any(k in n for k in ['chrome','rims','metal','disc','tailpipes']) else 'rubber' if any(k in n for k in ['rubber','tire']) else 'tan' if any(k in n for k in ['seat','doorpanel','dashboard','centerconsole','shell','steeringwheel']) else 'red' if 'taillight' in n else 'dark'
  slot.material=materials[group]
 # Real evaluated geometry, including mirrors and existing part modifiers.
 for m in o.modifiers:
  if m.type=='SUBSURF':m.levels=0;m.render_levels=0
 if len(o.data.polygons)>1500:
  d=o.modifiers.new('Viewer decimation','DECIMATE');d.ratio=.20
 selected.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in selected:o.select_set(True)
bpy.context.view_layer.objects.active=selected[0]
bpy.ops.export_scene.gltf(filepath=str(a.output),use_selection=True,export_format='GLB',export_apply=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
(a.output.with_suffix('.license.txt')).write_text('Volvo S90 Recharge (Free) by lazercar, CC BY 4.0. Geometry simplified, PBR materials and coordinate alignment modified.\nhttps://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9\nhttps://creativecommons.org/licenses/by/4.0/\nNo manufacturer endorsement.\n')
print('EXPORTED_VIEWER_CAR',a.output.stat().st_size,'bytes',flush=True)
