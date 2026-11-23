// RGB-only reconstruction viewer. MIT; upstream model/vehicle licenses separate.
import * as T from 'three';
import { SparkRenderer, SplatMesh } from '@sparkjsdev/spark';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

export async function mountRgbViewer(root) {
  const ko=root.dataset.locale==='ko', base=root.dataset.root.replace(/\/$/,'')+'/';
  const stage=root.querySelector('[data-rgb-stage]'), status=root.querySelector('[data-rgb-status]');
  const config=await fetch(base+'cameras.json').then(r=>{if(!r.ok)throw new Error('Missing camera reconstruction');return r.json();});
  const renderer=new T.WebGLRenderer({antialias:false,alpha:false,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor('#ccd3d9');renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
  const canvas=renderer.domElement;canvas.tabIndex=0;canvas.setAttribute('aria-label',ko?'RGB로 복원한 도로와 Volvo의 3D 장면':'3D road reconstructed from RGB, with a Volvo reference');stage.append(canvas);
  const scene=new T.Scene(),referenceScene=new T.Scene();renderer.autoClear=false;
  const pmrem=new T.PMREMGenerator(renderer),room=new RoomEnvironment();const environment=pmrem.fromScene(room,.04);referenceScene.environment=environment.texture;room.dispose();pmrem.dispose();
  referenceScene.add(new T.HemisphereLight(0xe4f0ff,0x66645d,2.5));
  const sun=new T.DirectionalLight(0xfff7eb,3.1);sun.position.set(-3,-4,9);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-8;sun.shadow.camera.right=8;sun.shadow.camera.top=8;sun.shadow.camera.bottom=-8;sun.shadow.normalBias=.025;referenceScene.add(sun);referenceScene.add(sun.target);
  const shadow=new T.Mesh(new T.PlaneGeometry(150,150),new T.ShadowMaterial({opacity:.16,depthWrite:false}));shadow.receiveShadow=true;shadow.position.z=-.015;referenceScene.add(shadow);
  const camera=new T.PerspectiveCamera(64,16/9,.025,250);camera.up.set(0,0,1);
  const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.dampingFactor=.12;controls.minDistance=1.2;controls.maxDistance=24;controls.maxPolarAngle=Math.PI*.49;controls.screenSpacePanning=true;
  const spark=new SparkRenderer({renderer});scene.add(spark);
  const splats=new SplatMesh({url:base+'road.spz'});scene.add(splats);
  new T.Matrix4().set(...config.world_to_viewer.flat()).decompose(splats.position,splats.quaternion,splats.scale);
  const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync(base+config.vehicle.file);
  const car=new T.Group();const vehicle=gltf.scene;vehicle.rotation.x=Math.PI/2;vehicle.scale.setScalar(config.vehicle.scale);car.add(vehicle);referenceScene.add(car);
  vehicle.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=false;}});
  const slider=root.querySelector('[data-rgb-frame]'), play=root.querySelector('[data-rgb-play]'), frameLabel=root.querySelector('[data-rgb-time]');
  slider.max=String(config.frames.length-1);slider.value=String(config.default_frame);let index=config.default_frame,playing=false,clock=0,view='chase',visible=true,disposed=false;
  const offset=new T.Vector3(-4.3,-3.1,2.8), lastGround=new T.Vector3(), carTarget=new T.Vector3();
  const framePosition=(frame)=>new T.Vector3(...frame.ground_position);
  function setFrame(value,{initial=false}={}) {
    index=Math.max(0,Math.min(config.frames.length-1,Number(value)));const frame=config.frames[index];const p=framePosition(frame);const delta=p.clone().sub(lastGround);car.position.copy(p);car.rotation.z=frame.yaw_radians;carTarget.copy(p).add(new T.Vector3(0,0,.43));
    if(!initial){camera.position.add(delta);controls.target.add(delta);}lastGround.copy(p);slider.value=String(index);frameLabel.textContent=`${frame.time_seconds.toFixed(1)} s · ${index+1}/${config.frames.length}`;
    shadow.position.set(p.x,p.y,-.015);sun.position.copy(p).add(new T.Vector3(-3,-4,9));sun.target.position.copy(p);
    if(view==='driver')setPreset('driver');root.dataset.frame=String(index);
  }
  function setPreset(name) {
    view=name;car.visible=name!=='driver';const frame=config.frames[index];const yaw=frame.yaw_radians;const q=new T.Quaternion().setFromAxisAngle(new T.Vector3(0,0,1),yaw);
    if(name==='driver'){
      camera.position.set(...frame.camera_position);const R=frame.camera_rotation_opencv;
      const forward=new T.Vector3(R[0][2],R[1][2],R[2][2]);controls.target.copy(camera.position).addScaledVector(forward,5);camera.fov=2*Math.atan(frame.image_size[1]/(2*frame.K[1][1]))*180/Math.PI;
    }else {
      const offsets={chase:[-3.4,-2.6,2.2],rear:[-5.2,0,1.8],side:[0,-5.2,2.0],overhead:[-.4,0,6.5]};offset.set(...(offsets[name]||offsets.chase)).applyQuaternion(q);camera.position.copy(carTarget).add(offset);controls.target.copy(carTarget);camera.fov=64;
    }
    camera.updateProjectionMatrix();controls.update();root.dataset.view=name;
    root.querySelectorAll('[data-rgb-preset]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.rgbPreset===name)));
  }
  setFrame(index,{initial:true});setPreset('chase');
  const onInput=()=>{playing=false;play.textContent=ko?'경로 재생':'Play path';setFrame(slider.value);};slider.addEventListener('input',onInput);
  const onPlay=()=>{playing=!playing;clock=0;play.textContent=playing?(ko?'일시 정지':'Pause'):(ko?'경로 재생':'Play path');};play.addEventListener('click',onPlay);
  const presetHandlers=[];root.querySelectorAll('[data-rgb-preset]').forEach(b=>{const handler=()=>setPreset(b.dataset.rgbPreset);b.addEventListener('click',handler);presetHandlers.push([b,handler]);});
  // Real pointer events drive OrbitControls. A small cursor ring also makes
  // recorded tutorials readable; it never changes the camera or rendered scene.
  const cursor=root.querySelector('[data-rgb-cursor]');
  const pointer=e=>{if(cursor){const b=stage.getBoundingClientRect();cursor.style.transform=`translate(${e.clientX-b.left}px,${e.clientY-b.top}px)`;cursor.hidden=false;}};
  const leave=()=>{if(cursor)cursor.hidden=true;};canvas.addEventListener('pointermove',pointer);canvas.addEventListener('pointerleave',leave);
  const orbit=()=>{if(view==='driver'){view='free';root.dataset.view='free';}};controls.addEventListener('start',orbit);
  const resize=new ResizeObserver(()=>{camera.aspect=stage.clientWidth/stage.clientHeight;camera.updateProjectionMatrix();renderer.setSize(stage.clientWidth,stage.clientHeight);});resize.observe(stage);
  const observer=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;});observer.observe(stage);
  let last=performance.now();renderer.setAnimationLoop(()=>{const now=performance.now(),dt=Math.min((now-last)/1000,.08);last=now;if(disposed||!visible||document.hidden)return;
    if(playing){clock+=dt;const step=config.frames[Math.min(index+1,config.frames.length-1)].time_seconds-config.frames[index].time_seconds||.3;if(clock>=step){clock=0;setFrame((index+1)%config.frames.length);}}
    controls.update();renderer.clear();renderer.render(scene,camera);renderer.clearDepth();renderer.render(referenceScene,camera);
  });
  await splats.initialized;root.dataset.rgbReady='true';status.textContent=ko?'드래그해서 회전하고 휠로 확대해 보세요. 입력은 RGB 사진뿐입니다.':'Drag to orbit and scroll to zoom. Reconstruction inputs are RGB images only.';
  root.querySelectorAll('[data-rgb-frame],[data-rgb-play],[data-rgb-preset]').forEach(el=>el.disabled=false);
  // Read-only debug state supports automated interaction checks without replacing
  // real pointer/scroll events with a pre-rendered video or camera animation.
  root.rgbViewerState=()=>({frame:index,view,camera:camera.position.toArray(),target:controls.target.toArray(),gaussians:splats.packedSplats?.numSplats??null});
  return ()=>{disposed=true;renderer.setAnimationLoop(null);resize.disconnect();observer.disconnect();slider.removeEventListener('input',onInput);play.removeEventListener('click',onPlay);presetHandlers.forEach(([b,h])=>b.removeEventListener('click',h));canvas.removeEventListener('pointermove',pointer);canvas.removeEventListener('pointerleave',leave);controls.removeEventListener('start',orbit);controls.dispose();splats.dispose();spark.dispose();vehicle.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose();}});environment.dispose();shadow.geometry.dispose();shadow.material.dispose();renderer.dispose();renderer.forceContextLoss();canvas.remove();delete root.dataset.rgbReady;delete root.rgbViewerState;};
}
