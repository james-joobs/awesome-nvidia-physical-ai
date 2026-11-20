"""Dynamic-obstacle navigation in the WorldGen scene.

Scene setup derives from the worldgen-navigation lab (commit 44d2fba).
The Navigator receives scan endpoints and ego pose, never obstacle transforms.

Run inside Isaac Sim 6.2, outside the WorldGen Python environment.
The visual shell is not a collider. The test floor and crate are explicit proxies.
"""
import argparse,json,math,os,time,traceback
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

p=argparse.ArgumentParser()
p.add_argument('--assets',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--scenario',choices=['gate','cart'],default='gate')
p.add_argument('--room-emission',type=float,default=400.);p.add_argument('--headless',action='store_true');p.add_argument('--collision-view',action='store_true')
p.add_argument('--raw-collider',action='store_true');p.add_argument('--no-floor',action='store_true');p.add_argument('--record-handshake',action='store_true')
p.add_argument('--controller',choices=['static','dynamic'],default='dynamic')
p.add_argument('--dropout-start',type=float,default=-1.)
p.add_argument('--dropout-seconds',type=float,default=0.)
p.add_argument('--sensor-off',action='store_true')
p.add_argument('--max-seconds',type=float,default=32.)
p.add_argument('--hold-seconds',type=float,default=2.)
a,kit_args=p.parse_known_args();a.assets=a.assets.resolve();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
(a.output/'FAILED').unlink(missing_ok=True)
from isaacsim import SimulationApp
app=SimulationApp({'headless':a.headless,'width':1280,'height':720,'window_width':1440,'window_height':900,
    'renderer':'RaytracedLighting','anti_aliasing':2,'fast_shutdown':True})
failed=True
try:
    import numpy as np
    import carb,omni.usd,omni.physx
    from pxr import Gf,Sdf,UsdGeom,UsdShade,UsdLux,UsdPhysics,PhysxSchema,PhysicsSchemaTools
    from isaacsim.core.simulation_manager import SimulationManager
    import isaacsim.core.experimental.utils.stage as stage_utils
    from isaacsim.core.rendering_manager import RenderingManager, ViewportManager
    from omni.kit.viewport.utility import get_active_viewport
    settings=carb.settings.get_settings()
    settings.set_bool('/physics/updateToUsd',True)
    settings.set_bool('/rtx/hydra/readTransformsFromFabricInRenderDelegate',False)
    settings.set_bool('/persistent/app/viewport/Viewport/Viewport0/scene/cameras/visible',False)
    stage_utils.create_new_stage()
    class SimulationLoop:
        @property
        def current_time(self):return SimulationManager.get_simulation_time()
        def initialize(self):
            SimulationManager.setup_simulation(dt=1/60)
            SimulationManager.initialize_physics()
            RenderingManager.set_dt(1/60)
        def step(self,render=True):
            SimulationManager.step()
            if render and not a.headless:RenderingManager.render()
    simulation=SimulationLoop()
    stage=omni.usd.get_context().get_stage();UsdGeom.SetStageUpAxis(stage,'Z');UsdGeom.SetStageMetersPerUnit(stage,1.)
    root=UsdGeom.Xform.Define(stage,'/World');stage.SetDefaultPrim(root.GetPrim())
    manifest=json.loads((a.assets/'calibration.json').read_text())
    config=manifest['physics_proxy'];robot_cfg=manifest['robot']
    def xform(path,pos):
        obj=UsdGeom.Xform.Define(stage,path);obj.AddTranslateOp().Set(Gf.Vec3d(*pos));return obj
    def material(name,rgb,emission=0):
        mat=UsdShade.Material.Define(stage,'/World/Looks/'+name);shader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Surface'))
        shader.CreateIdAttr('UsdPreviewSurface');shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*rgb))
        shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.65)
        shader.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*(np.array(rgb)*emission)))
        mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface');return mat
    def bind(obj,mat):UsdShade.MaterialBindingAPI.Apply(obj.GetPrim()).Bind(mat)
    green=material('RobotGreen',(.30,.65,.025),.15);dark=material('Rubber',(.045,.05,.055),.05)
    steel=material('Steel',(.35,.39,.42));orange=material('TestCrate',(.96,.34,.025),.1);gray=material('ProxyFloor',(.33,.40,.42),.1)
    blue=material('Probe',(.03,.35,.95),.2);white=material('Ruler',(.94,.94,.85),.3)
    def physics_material(name,friction):
        mat=UsdShade.Material.Define(stage,'/World/Looks/'+name);api=UsdPhysics.MaterialAPI.Apply(mat.GetPrim())
        api.CreateStaticFrictionAttr(friction);api.CreateDynamicFrictionAttr(friction);api.CreateRestitutionAttr(0.)
        return mat
    traction=physics_material('Traction',.9);caster_mat=physics_material('Caster',.015)
    def box(path,pos,size,mat,collision=False):
        o=UsdGeom.Cube.Define(stage,path);o.CreateSizeAttr(1.);o.AddTranslateOp().Set(Gf.Vec3d(*pos));o.AddScaleOp().Set(Gf.Vec3d(*size));bind(o,mat)
        if collision:UsdPhysics.CollisionAPI.Apply(o.GetPrim())
        return o
    def rigid(obj,mass):
        UsdPhysics.RigidBodyAPI.Apply(obj.GetPrim());UsdPhysics.MassAPI.Apply(obj.GetPrim()).CreateMassAttr(mass)
    # The render mesh is a decimation of the generated RGB-distance shell.
    mesh_data=np.load(a.assets/'room-mesh.npz');mesh=UsdGeom.Mesh.Define(stage,'/World/GeneratedRoom')
    mesh.CreatePointsAttr(mesh_data['points']);mesh.CreateFaceVertexCountsAttr([3]*len(mesh_data['indices']));mesh.CreateFaceVertexIndicesAttr(mesh_data['indices'].reshape(-1))
    mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True)
    UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('st',Sdf.ValueTypeNames.TexCoord2fArray,UsdGeom.Tokens.vertex).Set(mesh_data['uv'])
    mesh.CreateExtentAttr([Gf.Vec3f(*mesh_data['points'].min(0).tolist()),Gf.Vec3f(*mesh_data['points'].max(0).tolist())])
    # Native OmniPBR avoids the PreviewSurface texture-graph translation on RTX.
    room_mat=UsdShade.Material.Define(stage,'/World/Looks/Room')
    room_shader=UsdShade.Shader.Define(stage,'/World/Looks/Room/Shader')
    room_shader.CreateIdAttr('OmniPBR')
    room_shader.GetImplementationSourceAttr().Set(UsdShade.Tokens.sourceAsset)
    room_shader.SetSourceAsset(Sdf.AssetPath('OmniPBR.mdl'),'mdl')
    room_shader.SetSourceAssetSubIdentifier('OmniPBR','mdl')
    out=room_shader.CreateOutput('out',Sdf.ValueTypeNames.Token)
    room_mat.CreateSurfaceOutput('mdl').ConnectToSource(out)
    for name in ['diffuse_texture','emissive_color_texture']:
        room_shader.CreateInput(name,Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath(str(a.assets/'panorama.jpg')))
    room_shader.CreateInput('project_uvw',Sdf.ValueTypeNames.Bool).Set(False)
    room_shader.CreateInput('texture_scale',Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(1,1))
    room_shader.CreateInput('diffuse_color_constant',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(1))
    room_shader.CreateInput('reflection_roughness_constant',Sdf.ValueTypeNames.Float).Set(1.)
    room_shader.CreateInput('enable_emission',Sdf.ValueTypeNames.Bool).Set(True)
    room_shader.CreateInput('emissive_color',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(1))
    room_shader.CreateInput('emissive_intensity',Sdf.ValueTypeNames.Float).Set(a.room_emission)
    bind(mesh,room_mat)
    if a.raw_collider:
        UsdPhysics.CollisionAPI.Apply(mesh.GetPrim())
        UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr('none')
    if a.collision_view:mesh.CreateVisibilityAttr('invisible')
    if not a.no_floor:
        floor=box('/World/ProxyFloor',config['floor_center'],config['floor_size'],gray,True)
        UsdShade.MaterialBindingAPI.Apply(floor.GetPrim()).Bind(traction,materialPurpose='physics')
        if not a.collision_view:floor.CreateVisibilityAttr('invisible')
    import actors
    obstacle_paths=['/World/MovingObstacle']
    purple=material('MovingObstacle',(.65,.025,.38),.22)
    moving=xform('/World/MovingObstacle',actors.position(a.scenario,0.));rigid(moving,50.)
    UsdPhysics.RigidBodyAPI(moving.GetPrim()).CreateKinematicEnabledAttr(True)
    actor_collider=box('/World/MovingObstacle/Geometry',(0,0,0),actors.size(a.scenario),purple,True)
    actor_collider.CreateVisibilityAttr('invisible')
    # The compatibility renderer needs an explicit visual mirror for targets
    # driven through the physics tensor API. It follows measured solver state.
    display=xform('/World/MovingDisplay',actors.position(a.scenario,0.))
    display_translate=UsdGeom.Xformable(display).GetOrderedXformOps()[0]
    box('/World/MovingDisplay/Geometry',(0,0,0),actors.size(a.scenario),purple)
    if a.scenario=='cart':
        crate=box('/World/TestCrate',config['obstacle_center'],config['obstacle_size'],orange,True)
        obstacle_paths.append('/World/TestCrate')
    # One metre, in the chosen simulation scale, rather than a claim about the generated simulation.
    box('/World/OneMetreBar',(0,.95,.06),(1,.015,.01),white)
    for x in np.linspace(-.5,.5,11):box(f'/World/Tick{int(round((x+.5)*10))}',(float(x),.95,.065),(.01,.06 if abs(x)>.49 else .035,.01),white)
    paths=[];drives=[]
    if a.scenario=='probes':
        for i,(x,y) in enumerate([(-1,-.7),(-1,.7),(1,-.7),(1,.7)]):
            obj=xform(f'/World/Probe{i}',(x,y,.75));rigid(obj,.1)
            if not a.headless:PhysxSchema.PhysxRigidBodyAPI.Apply(obj.GetPrim()).CreateDisableGravityAttr(True)
            box(str(obj.GetPath())+'/Geometry',(0,0,0),(.1,.1,.1),blue,True);paths.append(str(obj.GetPath()))
    else:
        robot=xform('/World/Robot',(0,0,0));UsdPhysics.ArticulationRootAPI.Apply(robot.GetPrim())
        PhysxSchema.PhysxArticulationAPI.Apply(robot.GetPrim()).CreateEnabledSelfCollisionsAttr(False)
        start=np.array(manifest['route']['start']);chassis=xform('/World/Robot/Chassis',start);rigid(chassis,8.)
        PhysxSchema.PhysxContactReportAPI.Apply(chassis.GetPrim()).CreateThresholdAttr(0)
        box('/World/Robot/Chassis/Body',(0,0,0),robot_cfg['body_size'],green,True)
        box('/World/Robot/Chassis/Top',(0,0,.13),(.38,.30,.08),steel)
        box('/World/Robot/Chassis/Front',(.28,0,.035),(.012,.22,.04),white)
        caster=UsdGeom.Sphere.Define(stage,'/World/Robot/Chassis/Caster');caster.CreateRadiusAttr(.05);caster.AddTranslateOp().Set(Gf.Vec3d(-.21,0,-.18));bind(caster,dark)
        UsdPhysics.CollisionAPI.Apply(caster.GetPrim());UsdShade.MaterialBindingAPI.Apply(caster.GetPrim()).Bind(caster_mat,materialPurpose='physics')
        for i,y in enumerate([.26,-.26]):
            path=f'/World/Robot/Wheel{i}';local=np.array([.10,y,-.12]);wheel=xform(path,start+local);rigid(wheel,.3);PhysxSchema.PhysxContactReportAPI.Apply(wheel.GetPrim()).CreateThresholdAttr(0)
            cylinder=UsdGeom.Cylinder.Define(stage,path+'/Tyre');cylinder.CreateAxisAttr('Y');cylinder.CreateRadiusAttr(.11);cylinder.CreateHeightAttr(.06);bind(cylinder,dark)
            UsdPhysics.CollisionAPI.Apply(cylinder.GetPrim());UsdShade.MaterialBindingAPI.Apply(cylinder.GetPrim()).Bind(traction,materialPurpose='physics')
            for j in range(3):
                spoke=box(path+f'/Spoke{j}',(0,(-.031 if y<0 else .031),0),(.16,.006,.015),white)
                spoke.AddRotateYOp().Set(j*60.)
            joint=UsdPhysics.RevoluteJoint.Define(stage,f'/World/Robot/Joint{i}');joint.CreateAxisAttr('Y')
            joint.CreateBody0Rel().SetTargets([chassis.GetPath()]);joint.CreateBody1Rel().SetTargets([wheel.GetPath()])
            joint.CreateLocalPos0Attr(Gf.Vec3f(*local));joint.CreateLocalPos1Attr(Gf.Vec3f(0))
            drive=UsdPhysics.DriveAPI.Apply(joint.GetPrim(),'angular');drive.CreateTypeAttr('force');drive.CreateStiffnessAttr(0);drive.CreateDampingAttr(20);drive.CreateMaxForceAttr(6);drive.CreateTargetVelocityAttr(0)
            drives.append(drive)
        paths=['/World/Robot/Chassis']
    from isaacsim.sensors.experimental.physics import Raycast,RaycastSensor
    if a.controller=='dynamic':
        from navigation import Navigator
    else:
        from static_navigation import Navigator
    angles=np.linspace(-math.pi,math.pi,180,endpoint=False)
    scanner=RaycastSensor(Raycast.create('/World/Robot/Chassis/RangeSensor',
        ray_origins=[[0.,0.,0.]]*len(angles),ray_directions=[[math.cos(t),math.sin(t),0.] for t in angles],
        min_range=.05,max_range=2.5,output_frame='WORLD',translations=[[0.,0.,.25]]))
    cap=UsdGeom.Cylinder.Define(stage,'/World/Robot/Chassis/SensorCap');cap.CreateAxisAttr('Z');cap.CreateRadiusAttr(.06);cap.CreateHeightAttr(.04);cap.AddTranslateOp().Set(Gf.Vec3d(0,0,.24));bind(cap,blue)
    cyan=material('LiveSensor',(.015,.8,.85),.7)
    def curve(path,mat,width):
        c=UsdGeom.BasisCurves.Define(stage,path);c.CreateTypeAttr('linear');c.CreateWidthsAttr([width]);c.SetWidthsInterpolation('constant');bind(c,mat);c.CreateVisibilityAttr('invisible');return c
    scan_lines=curve('/World/LiveScan',blue,.006);path_line=curve('/World/PlannedPath',cyan,.012)
    map_points=UsdGeom.Points.Define(stage,'/World/ObservedMap');map_points.CreateWidthsAttr([.035]);map_points.SetWidthsInterpolation('constant');bind(map_points,orange);map_points.CreateVisibilityAttr('invisible')
    goal_marker=UsdGeom.Cylinder.Define(stage,'/World/Goal');goal_marker.CreateRadiusAttr(.12);goal_marker.CreateHeightAttr(.015);goal_marker.AddTranslateOp().Set(Gf.Vec3d(1.3,0,.055));bind(goal_marker,green)
    timing={'sensor_s':0.,'planner_s':0.,'draw_s':0.,'step_s':0.}
    navigator=Navigator();scan_log=[];last_scan_time=-1e9;front_min=2.5
    # Save the source scene before stepping. The exported state can be inspected in the GUI.
    def aim(camera,eye,target):
        matrix=Gf.Matrix4d(1).SetLookAt(Gf.Vec3d(*eye),Gf.Vec3d(*target),Gf.Vec3d(0,0,1)).GetInverse()
        UsdGeom.Xformable(camera).AddTransformOp().Set(matrix)
    camera=UsdGeom.Camera.Define(stage,'/World/FilmCamera');camera.GetPrim().ApplyAPI('OmniSensorAPI');aim(camera,(0,-1.8,1.35),(0,.6,.45));camera.CreateFocalLengthAttr(11);camera.CreateHorizontalApertureAttr(36);camera.CreateClippingRangeAttr(Gf.Vec2f(.03,120))
    dome=UsdLux.DomeLight.Define(stage,'/World/Dome');dome.CreateIntensityAttr(450)
    key=UsdLux.SphereLight.Define(stage,'/World/Light');key.AddTranslateOp().Set(Gf.Vec3d(-.3,-.5,2.1));key.CreateIntensityAttr(1800);key.CreateRadiusAttr(.7)
    stage.Export(str(a.output/'scene.usdc'))
    portable=Sdf.Layer.FindOrOpen(str(a.output/'scene.usdc'))
    for name in ['diffuse_texture','emissive_color_texture']:
        portable.GetAttributeAtPath('/World/Looks/Room/Shader.inputs:'+name).default=Sdf.AssetPath(os.path.relpath(a.assets/'panorama.jpg',a.output))
    portable.Save()
    simulation.initialize()
    if not a.headless:
        viewport=get_active_viewport();ViewportManager.set_camera(camera)
        import asyncio
        from omni.kit.viewport.utility import capture_viewport_to_file
        from PIL import Image
        for _ in range(8):
            simulation.step()
        capture=capture_viewport_to_file(viewport,str(a.output/'initial-rgb.png'))
        async def wait_for_frame():
            return await asyncio.wait_for(capture.wait_for_result(),timeout=120)
        app.run_coroutine(wait_for_frame())
        image_deadline=time.monotonic()+10
        while True:
            try:
                with Image.open(a.output/'initial-rgb.png') as frame:
                    pixels=np.array(frame)
                break
            except (FileNotFoundError,OSError):
                if time.monotonic()>image_deadline:raise
                RenderingManager.render();time.sleep(.02)
        (a.output/'initial-rgb.png').chmod(0o644)
        assert pixels.ndim==3 and pixels[:,:,:3].mean()>5,'Native viewport remained black'
        print('RENDER_CHECK',pixels.shape,float(pixels[:,:,:3].mean()),flush=True)
    if a.scenario=='probes':
        for _ in range(40):RenderingManager.render()
    else:
        for _ in range(40):simulation.step(render=True)
    inspector=omni.physx.get_physx_interface()
    import omni.physics.tensors as tensors
    tensor_sim=tensors.create_simulation_view('numpy',stage_id=stage_utils.get_stage_id(stage))
    actor_view=tensor_sim.create_rigid_body_view('/World/MovingObstacle')
    assert actor_view.count==1
    actor_indices=np.array([0],dtype=np.uint32)
    def pose(path):
        v=inspector.get_rigidbody_transformation(path);assert v['ret_val'],path
        return list(v['position']),list(v['rotation'])
    raycasts={}
    for name,xy in [('floor_left',[-1,-1]),('floor_right',[1,-1]),('crate',[0,0])]:
        hit=omni.physx.get_physx_scene_query_interface().raycast_closest((xy[0],xy[1],2.),(0.,0.,-1.),5.)
        raycasts[name]={'hit':bool(hit['hit']),'collider':str(hit.get('collision','')),'position':list(hit.get('position',[]))}
    contacts=[]
    def on_contact(headers,data):
        for header in headers:
            actor0=str(PhysicsSchemaTools.intToSdfPath(header.actor0));actor1=str(PhysicsSchemaTools.intToSdfPath(header.actor1))
            if any(path in actor0+actor1 for path in obstacle_paths) and 'Robot' in actor0+actor1:
                contacts.append({'actor0':actor0,'actor1':actor1,'type':int(header.type),'time':simulation.current_time})
    subscription=omni.physx.get_physx_simulation_interface().subscribe_contact_report_events(on_contact)
    if a.record_handshake:
        (a.output/'ready.json').write_text(json.dumps({'camera':str(camera.GetPath()),'application':'Isaac Sim 6.2 native window'}))
        deadline=time.monotonic()+60
        while not (a.output/'record-go').exists():
            if time.monotonic()>deadline:raise TimeoutError('Native recorder did not start')
            RenderingManager.render()
        if a.scenario!='probes':
            for _ in range(45):simulation.step(render=True)
        print('NATIVE_GUI_RECORDING_STARTED',flush=True)
    if a.scenario=='probes' and not a.headless:
        for path in paths:PhysxSchema.PhysxRigidBodyAPI.Get(stage,path).GetDisableGravityAttr().Set(False)
    paths.append('/World/MovingObstacle')
    samples=[];phase_events=[];cleared_total=expired_total=0
    steps=int(a.max_seconds*60)
    start_wall=time.monotonic();start_sim=simulation.current_time;reached=False;goal_time=None;phase='starting'
    for step in range(steps):
        position,rotation=pose(paths[0]);x,y,z=position;qx,qy,qz,qw=rotation
        yaw=math.atan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
        elapsed=simulation.current_time-start_sim
        actor_target=np.array([actors.position(a.scenario,elapsed)+[0.,0.,0.,1.]],dtype=np.float32)
        actor_view.set_kinematic_targets(actor_target,actor_indices)
        dropout=a.dropout_start<=elapsed<a.dropout_start+a.dropout_seconds
        if step%6==0 and not a.sensor_off and not dropout:
            tick=time.perf_counter()
            frame=scanner.get_data()
            depths=np.asarray(frame['depths']).reshape(-1).astype(float).tolist()
            endpoints=np.asarray(frame['hit_positions']).reshape(-1,3).astype(float).tolist()
            reading_time=float(frame['time'])
            assert len(depths)==180 and all(math.isfinite(q) for q in depths),'Invalid range scan'
            last_scan_time=reading_time
            # hit prim paths and scene objects are deliberately not passed to the planner.
            timing['sensor_s']+=time.perf_counter()-tick;tick=time.perf_counter()
            navigator.update((x,y,yaw),depths,endpoints,reading_time)
            stats=getattr(navigator,'stats',{'cleared':0,'expired':0,'occupied':len(navigator.hits)})
            cleared_total+=stats['cleared'];expired_total+=stats['expired']
            timing['planner_s']+=time.perf_counter()-tick;tick=time.perf_counter()
            forward=[d for t,d in zip(angles,depths) if abs(t)<math.radians(25)]
            front_min=min(forward)
            scan_log.append({'sim_time_s':elapsed,'sensor_time_s':reading_time,'pose_xyyaw':[x,y,yaw],
                'depths_m':depths,'hit_positions_world':endpoints,'front_min_m':front_min,
                'planned_path_xy':navigator.path,'occupied_cells':len(navigator.hits),'map_update':stats})
            sensor_origin=[x,y,z+.25]
            line_points=[]
            for d,pt in zip(depths,endpoints):
                if .05<=d<2.499:line_points.extend([sensor_origin,pt])
            if line_points:
                scan_lines.CreatePointsAttr([Gf.Vec3f(*pt) for pt in line_points]);scan_lines.CreateCurveVertexCountsAttr([2]*(len(line_points)//2));scan_lines.CreateVisibilityAttr('inherited')
            else:scan_lines.CreateVisibilityAttr('invisible')
            path_points=[Gf.Vec3f(q[0],q[1],.075) for q in navigator.path]
            if len(path_points)>1:
                path_line.CreatePointsAttr(path_points);path_line.CreateCurveVertexCountsAttr([len(path_points)]);path_line.CreateVisibilityAttr('inherited')
            else:path_line.CreateVisibilityAttr('invisible')
            cells=[Gf.Vec3f(*navigator.point(cell),.48) for cell in navigator.hits]
            if cells:
                map_points.CreatePointsAttr(cells);map_points.CreateExtentAttr([Gf.Vec3f(*[min(p[i] for p in cells)-.02 for i in range(3)]),Gf.Vec3f(*[max(p[i] for p in cells)+.02 for i in range(3)])]);map_points.CreateVisibilityAttr('inherited')
            else:map_points.CreateVisibilityAttr('invisible')
            timing['draw_s']+=time.perf_counter()-tick
        v=omega=0.
        sensor_age=simulation.current_time-last_scan_time
        v,omega,phase=navigator.command((x,y,yaw),front_min,sensor_age)
        reached=phase=='goal'
        if not phase_events or phase_events[-1]['phase']!=phase:
            phase_events.append({'time_s':elapsed,'phase':phase,'position_xyz':position,'front_min_m':front_min})
        for drive,speed in zip(drives,[(v-.26*omega)/.11,(v+.26*omega)/.11]):
            drive.GetTargetVelocityAttr().Set(math.degrees(speed))
        tick=time.perf_counter();simulation.step(render=False)
        actual_actor_position=pose('/World/MovingObstacle')[0]
        display_translate.Set(Gf.Vec3d(*actual_actor_position))
        if not a.headless:RenderingManager.render()
        timing['step_s']+=time.perf_counter()-tick
        if step%60==0:print('SIM_STEP',step,phase,front_min,position,flush=True)
        if step%6==0:
            samples.append({'step':step,'sim_time_s':simulation.current_time-start_sim,'wall_s':time.monotonic()-start_wall,
                'poses':{path:pose(path) for path in paths},'command':[v,omega],'waypoint':None,'dropout_injected':dropout,'obstacle_target_xyz':actor_target[0,:3].tolist(),'render_position_xyz':list(display_translate.Get()),
                'phase':phase,'front_min_m':front_min,'sensor_age_s':simulation.current_time-last_scan_time if last_scan_time>0 else None})
        if reached:
            if goal_time is None:goal_time=elapsed
            if elapsed-goal_time>=a.hold_seconds:break
        if not a.headless:time.sleep(max(0,(step+1)/60-(time.monotonic()-start_wall)))
    for drive in drives:drive.GetTargetVelocityAttr().Set(0)
    try: sim_version=version('isaacsim')
    except PackageNotFoundError:
        from isaacsim.core.version import get_version
        sim_version=get_version()[0]
    result={'status':'complete','scenario':a.scenario,'controller':a.controller,'sensor_off':a.sensor_off,'collision_view':a.collision_view,'no_floor':a.no_floor,'raw_collider':a.raw_collider,
        'isaacsim_version':sim_version,'physics':'live PhysX; joint velocity drives; not a USD trajectory replay',
        'control':'range sensor → refreshed occupancy → A* → stop supervisor → physical wheel drives' if a.controller=='dynamic' else 'previous static accumulating-map sensor controller',
        'moving_actor':{'type':'PhysX kinematic rigid body driven by set_kinematic_targets','size':actors.size(a.scenario),'schedule_passed_to_controller':False,'display':'non-colliding visual prim synchronized from actual PhysX pose every physics step','motion':'gate enters 2–3.8 s, withdraws 8–9.8 s' if a.scenario=='gate' else 'box enters the lower passage 2–4 s, then remains'},
        'dropout':{'start_s':a.dropout_start,'duration_s':a.dropout_seconds},'map_cleared_total':cleared_total,'map_expired_total':expired_total,
        'timing':timing,'sensor':{'class':'isaacsim.sensors.experimental.physics.RaycastSensor','rays':180,'max_range_m':2.5,'height_above_chassis_m':.25,'controller_read_hz':10,'scan_frames':len(scan_log),'replans':navigator.replans},
        'navigation':{'obstacle_transforms_as_input':False,'known_floor_bounds':navigator.bounds,'inflation_radius_m':navigator.radius,'grid_resolution_m':navigator.resolution,'goal_xy':navigator.goal,'body_goal_xy':[1.3,0.],
            'control_reference':'axle midpoint 0.10 m ahead of chassis' if a.controller=='dynamic' else 'chassis center',
            'desired_final_heading_rad':0. if a.controller=='dynamic' else None,'pose_source':'simulator ground truth; not SLAM or wheel odometry'},
        'phase_events':phase_events,'goal_reached_s':goal_time,'start_sim_s':start_sim,'duration_sim_s':simulation.current_time-start_sim,'duration_wall_s':time.monotonic()-start_wall,'reached_goal':reached,
        'stage':{'up_axis':str(UsdGeom.GetStageUpAxis(stage)),'meters_per_unit':UsdGeom.GetStageMetersPerUnit(stage),'render_mesh_collision':mesh.GetPrim().HasAPI(UsdPhysics.CollisionAPI),'multitick_rendering':settings.get_as_bool('/rtx/hydra/supportMultiTickRate'),'room_emission_display_setting':a.room_emission,'proxy_floor':not a.no_floor},'raycasts':raycasts,'crate_contact_events':contacts,'samples':samples,'final_poses':{path:pose(path) for path in paths}}
    (a.output/'scans.json').write_text(json.dumps(scan_log,separators=(',',':'))+'\n')
    (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RUN_RESULT',json.dumps({k:v for k,v in result.items() if k not in ['samples','crate_contact_events']}),flush=True)
    failed=False
except BaseException:
    traceback.print_exc()
finally:
    if failed:(a.output/'FAILED').touch()
    app.close()
if failed:raise SystemExit(1)
