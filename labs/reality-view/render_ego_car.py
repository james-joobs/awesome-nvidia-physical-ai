"""Render the credited Volvo asset into calibrated transparent pinhole layers.

Blender invocation (disable embedded scripts before opening third-party files):
blender --background --disable-autoexec /path/to/Volvo-S90.blend \
  --python render_ego_car.py -- --textures /path/to/textures \
  --views /path/to/ego-views.json --output /path/to/vehicle-layers

A view has id, width, height, a 3x3 K matrix and a 4x4 camera_to_rig
(OpenCV: right/down/forward). Rig axes are forward/left/up in meters.
This is a visual reference mesh, not an OEM physics or driving model.
"""
import argparse,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
p=argparse.ArgumentParser();p.add_argument('--textures',type=Path,required=True);p.add_argument('--views',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ground-plane',type=Path);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);args.output.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;images={f.name:f for f in args.textures.rglob('*') if f.is_file()}
for im in bpy.data.images:
 if im.source=='FILE':
  name=Path(im.filepath.replace('\\','/')).name
  if name in images:
   im.filepath=str(images[name])
   try:im.colorspace_settings.name='Non-Color' if any(s in name.lower() for s in ['normal','roughness','height','metallic']) else 'sRGB'
   except TypeError:pass
paint=bpy.data.materials.get('Car Paint')
if paint:
 paint.use_nodes=True;paint.node_tree.nodes.clear();shader=paint.node_tree.nodes.new('ShaderNodeBsdfPrincipled');shader.inputs['Base Color'].default_value=(.62,.68,.73,1);shader.inputs['Metallic'].default_value=.45;shader.inputs['Roughness'].default_value=.28;shader.inputs['Coat Weight'].default_value=.7;out=paint.node_tree.nodes.new('ShaderNodeOutputMaterial');paint.node_tree.links.new(shader.outputs['BSDF'],out.inputs['Surface'])
T=Matrix(((0,-1,0,.8),(1,0,0,0),(0,0,1,-.02234119),(0,0,0,1)))
ground=Matrix.Identity(4)
if args.ground_plane:
 g=json.loads(args.ground_plane.read_text());a,b,z=g['forward_slope'],g['left_slope'],g['height_at_rig_m'];n=Vector((-a,-b,1)).normalized();forward=Vector((1,0,a)).normalized();left=n.cross(forward).normalized();ground=Matrix((forward,left,n)).transposed().to_4x4();ground.translation=Vector((0,0,z));T=ground@T
for o in scene.objects:
 if o.type=='MESH':
  o.hide_render=False;o.hide_set(False);o.matrix_world=T@o.matrix_world
  for m in o.modifiers:
   if m.type=='SUBSURF':m.render_levels=min(1,m.render_levels)
# Shadow catcher contributes only contact shadows on the measured road plane.
bpy.ops.mesh.primitive_plane_add(size=100);plane=bpy.context.object;plane.name='Road shadow catcher';plane.matrix_world=ground;plane.is_shadow_catcher=True
scene.world=bpy.data.worlds.new('Ego daylight');scene.world.use_nodes=True;nodes=scene.world.node_tree.nodes;nodes.clear();bg=nodes.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.45;sky=nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_disc=False;sky.sun_elevation=math.radians(40);sky.sun_rotation=math.radians(130);wo=nodes.new('ShaderNodeOutputWorld');scene.world.node_tree.links.new(sky.outputs['Color'],bg.inputs['Color']);scene.world.node_tree.links.new(bg.outputs[0],wo.inputs[0])
for name,loc,power in [('softbox',(-3,-4,7),700),('fill',(4,5,6),500)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=5;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((.8,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=10;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
camdata=bpy.data.cameras.new('Ego pinhole');cam=bpy.data.objects.new('Ego camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='PERSP';camdata.sensor_fit='HORIZONTAL';camdata.sensor_width=36;camdata.clip_start=.01;camdata.clip_end=100
for view in json.loads(args.views.read_text())['views']:
 width,height=view['width'],view['height'];K=view['K']
 if abs(K[0][1])+abs(K[1][0])>1e-6:raise ValueError('Skewed intrinsics are not supported')
 if Path(view['id']).name!=view['id']:raise ValueError('View id must be a filename stem')
 scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.pixel_aspect_x=1;scene.render.pixel_aspect_y=K[0][0]/K[1][1];camdata.lens=K[0][0]*36/width;camdata.shift_x=(width/2-K[0][2])/width;camdata.shift_y=(K[1][2]-height/2)/width
 cam.matrix_world=Matrix(view['camera_to_rig'])@Matrix.Diagonal((1,-1,-1,1));plane.hide_render=False;scene.render.filepath=str(args.output/f"{view['id']}-shadowed.png");bpy.ops.render.render(write_still=True)
 plane.hide_render=True;scene.render.filepath=str(args.output/f"{view['id']}-car.png");bpy.ops.render.render(write_still=True)
(args.output/'vehicle-attribution.txt').write_text('Volvo S90 Recharge (Free) by lazercar, CC BY 4.0. Paint, orientation and rendering modified.\nhttps://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9\nhttps://creativecommons.org/licenses/by/4.0/\n')
