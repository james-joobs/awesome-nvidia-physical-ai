"""Import the calibrated WorldGen visual mesh and simulate a real wheeled AMR.

Run inside Isaac Sim 6.2, outside the WorldGen Python environment.
The visual shell is not a collider. The test floor and crate are explicit proxies.
"""
import argparse,json,math,os,time,traceback
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

p=argparse.ArgumentParser()
p.add_argument('--assets',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--scenario',choices=['probes','blocked','detour','combined'],default='detour')
p.add_argument('--room-emission',type=float,default=400.);p.add_argument('--headless',action='store_true');p.add_argument('--collision-view',action='store_true')
p.add_argument('--raw-collider',action='store_true');p.add_argument('--no-floor',action='store_true');p.add_argument('--record-handshake',action='store_true')
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
            if render:RenderingManager.render()
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
    crate=box('/World/TestCrate',config['obstacle_center'],config['obstacle_size'],orange,True)
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
            path=f'/World/Robot/Wheel{i}';local=np.array([.10,y,-.12]);wheel=xform(path,start+local);rigid(wheel,.3)
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
            if 'TestCrate' in actor0+actor1 and 'Chassis' in actor0+actor1:
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
    samples=[];waypoints=manifest['route']['detour_waypoints'];waypoint=0
    steps={'probes':180,'blocked':600,'detour':1800,'combined':2400}[a.scenario]
    start_wall=time.monotonic();start_sim=simulation.current_time;reached=False
    for step in range(steps):
        v=omega=0.
        if drives:
            position,rotation=pose(paths[0]);x,y,z=position;qx,qy,qz,qw=rotation
            yaw=math.atan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
            elapsed=simulation.current_time-start_sim
            if a.scenario=='blocked' or (a.scenario=='combined' and elapsed<4):v=.32
            elif a.scenario=='combined' and elapsed<5.6:v=-.25
            else:
                target=np.array(waypoints[waypoint]);distance=float(np.linalg.norm(target-np.array([x,y])))
                if distance<.12:
                    if waypoint<len(waypoints)-1:waypoint+=1
                    else:reached=True
                if not reached:
                    target=np.array(waypoints[waypoint]);delta=target-np.array([x,y]);error=math.atan2(math.sin(math.atan2(delta[1],delta[0])-yaw),math.cos(math.atan2(delta[1],delta[0])-yaw))
                    omega=float(np.clip(2.8*error,-1.1,1.1));v=min(.32,.9*distance)*max(0.,math.cos(error)) if abs(error)<.65 else 0.
            wheel_speeds=[(v-.26*omega)/.11,(v+.26*omega)/.11]
            for drive,speed in zip(drives,wheel_speeds):drive.GetTargetVelocityAttr().Set(math.degrees(speed))
        simulation.step(render=True)
        if step%60==0:print('SIM_STEP',step,simulation.current_time,flush=True)
        if step%6==0:
            sample={'step':step,'sim_time_s':simulation.current_time-start_sim,'wall_s':time.monotonic()-start_wall,'poses':{path:pose(path) for path in paths},'command':[v,omega],'waypoint':waypoint,'phase':('contact' if elapsed<4 else 'reverse' if elapsed<5.6 else 'detour') if a.scenario=='combined' else a.scenario}
            samples.append(sample)
        if reached and step>60:
            if samples[-1].get('goal_hold') is None:samples[-1]['goal_hold']=True
            if sum(s.get('goal_hold',False) for s in samples)>15:break
        # Preserve real simulation time in the window recording whenever the renderer keeps up.
        if not a.headless:time.sleep(max(0,(step+1)/60-(time.monotonic()-start_wall)))
    for drive in drives:drive.GetTargetVelocityAttr().Set(0)
    try: sim_version=version('isaacsim')
    except PackageNotFoundError:
        from isaacsim.core.version import get_version
        sim_version=get_version()[0]
    result={'status':'complete','scenario':a.scenario,'collision_view':a.collision_view,'no_floor':a.no_floor,'raw_collider':a.raw_collider,
        'isaacsim_version':sim_version,'physics':'live PhysX; joint velocity drives; not a USD trajectory replay',
        'control':'pose-feedback waypoint controller with initial contact and recovery' if a.scenario=='combined' else 'pose-feedback waypoint controller' if a.scenario=='detour' else 'fixed wheel commands' if drives else 'gravity probes',
        'start_sim_s':start_sim,'duration_sim_s':simulation.current_time-start_sim,'duration_wall_s':time.monotonic()-start_wall,'reached_goal':reached,
        'stage':{'up_axis':str(UsdGeom.GetStageUpAxis(stage)),'meters_per_unit':UsdGeom.GetStageMetersPerUnit(stage),'render_mesh_collision':mesh.GetPrim().HasAPI(UsdPhysics.CollisionAPI),'multitick_rendering':settings.get_as_bool('/rtx/hydra/supportMultiTickRate'),'room_emission_display_setting':a.room_emission,'proxy_floor':not a.no_floor},'raycasts':raycasts,'crate_contact_events':contacts,'samples':samples,'final_poses':{path:pose(path) for path in paths}}
    (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RUN_RESULT',json.dumps({k:v for k,v in result.items() if k not in ['samples','crate_contact_events']}),flush=True)
    failed=False
except BaseException:
    traceback.print_exc()
finally:
    if failed:(a.output/'FAILED').touch()
    app.close()
if failed:raise SystemExit(1)
