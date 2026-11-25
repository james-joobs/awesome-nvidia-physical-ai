// Frame-local RGB-D surfaces from actual Aether / DA3 outputs. MIT adapter.
// These are depth meshes, not a WorldVAE latent or a new Gaussian checkpoint.
import * as T from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { SparkRenderer, SplatMesh } from '@sparkjsdev/spark';

export async function mountJointViewer(root) {
  const ko=root.dataset.locale==='ko',base=root.dataset.jointRoot.replace(/\/$/,'')+'/';
  const get=async url=>{const r=await fetch(url);if(!r.ok)throw new Error(`HTTP ${r.status}`);return r;};
  const manifest=await(await get(base+'scene.json')).json();
  const stage=root.querySelector('[data-joint-stage]'),status=root.querySelector('[data-joint-status]');
  const select=root.querySelector('[data-joint-model]'),slider=root.querySelector('[data-joint-frame]');
  const rgb=root.querySelector('[data-joint-rgb]'),depthCanvas=root.querySelector('[data-joint-depth]');
  const info=root.querySelector('[data-joint-values]'),time=root.querySelector('[data-joint-time]'),play=root.querySelector('[data-joint-play]');
  const renderer=new T.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor(0xdce1e5);renderer.outputColorSpace=T.SRGBColorSpace;
  stage.append(renderer.domElement);renderer.domElement.setAttribute('aria-label',ko?'프레임별 RGB·깊이·카메라 3D 비교':'Frame-local RGB, depth and camera 3D comparison');
  const scene=new T.Scene(),camera=new T.PerspectiveCamera(64,1,.03,250);camera.up.set(0,0,1);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.maxDistance=50;controls.minDistance=.3;controls.maxPolarAngle=Math.PI*.88;
  scene.add(new T.HemisphereLight(0xffffff,0x69727d,2));
  const sun=new T.DirectionalLight(0xffffff,2);sun.position.set(-5,-8,12);scene.add(sun);
  const surfaces=Array.from({length:6},()=>{const mesh=new T.Mesh(new T.BufferGeometry(),new T.MeshBasicMaterial({side:T.DoubleSide}));mesh.frustumCulled=false;mesh.visible=false;scene.add(mesh);return mesh;});
  const marker=new T.Mesh(new T.SphereGeometry(.1,16,12),new T.MeshBasicMaterial({color:0xff3465,depthTest:false}));marker.renderOrder=100;marker.visible=false;scene.add(marker);
  const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync(base+'../nurec-rgb-reality/'+manifest.vehicle.file);
  const car=new T.Group();gltf.scene.rotation.x=Math.PI/2;gltf.scene.scale.setScalar(manifest.vehicle.scale);car.add(gltf.scene);scene.add(car);
  let index=8,model=manifest.models.find(m=>m.id===manifest.default),preset='chase',playing=false,clock=0,dead=false,revision=0,baseline=null,spark=null;
  const sourceSelect=root.querySelector('[data-joint-camera]');
  const activeCamera=()=>model?.views_per_frame===6?Number(sourceSelect.value):0;
  const activeView=()=>index*(model?.views_per_frame??1)+activeCamera();
  const updateCameraOptions=()=>{sourceSelect.closest('label').hidden=model?.views_per_frame!==6;};
  const buffers=new Map(),textures=new Map(),history=[];
  const modelLabel=m=>ko?({calibrated:'DA3-BASE · RGB 카메라 보조 입력',surround:'DA3-BASE · 주변 RGB 6개',da3:'DA3-BASE · 전방 RGB',aether:'AetherV1 · 전방 RGB'}[m.id]??m.label):m.label;
  let imageLoads=0;const imageQueue=[];
  async function loadTexture(url){
    if(imageLoads>=4)await new Promise(resolve=>imageQueue.push(resolve));
    else imageLoads++;
    try{
      let lastError;
      for(let attempt=0;attempt<2;attempt++){
        try{const tex=await new T.TextureLoader().loadAsync(url);tex.colorSpace=T.SRGBColorSpace;return tex;}
        catch(error){lastError=error;if(dead)break;}
      }
      throw lastError;
    }finally{const next=imageQueue.shift();if(next)next();else imageLoads--;}
  }
  async function loadModel(m){
    if(buffers.has(m.id))return;
    const bytes=await(await get(base+m.depth_file)).arrayBuffer();
    if(bytes.byteLength!==m.depth_bytes)throw new Error('Incomplete depth buffer');
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
    if(hash!==m.depth_sha256)throw new Error('Depth checksum mismatch');
    buffers.set(m.id,new Uint16Array(bytes));
  }
  async function texture(url){
    if(!textures.has(url))textures.set(url,loadTexture(url).catch(error=>{textures.delete(url);throw error;}));
    return textures.get(url);
  }
  const frameData=()=>manifest.frames[index];
  function setPreset(name){
    preset=name;const f=frameData(),yaw=f.yaw_radians;
    car.position.set(...f.ground_position);car.rotation.z=yaw;car.visible=name!=='input';
    if(name==='input'){
      const pose=model?model.camera_to_world[activeView()]:null;
      const R=pose?pose.slice(0,3).map(r=>r.slice(0,3)):f.camera_rotation_opencv;
      camera.position.set(...(pose?pose.slice(0,3).map(r=>r[3]):f.camera_position));
      controls.target.copy(camera.position).add(new T.Vector3(R[0][2],R[1][2],R[2][2]).multiplyScalar(8));
      // Roll agrees with the actual input camera; free views return to Z-up.
      camera.up.set(-R[0][1],-R[1][1],-R[2][1]);
      camera.fov=model?2*Math.atan(model.source_shape[1]/(2*model.intrinsics[activeView()][1][1]))*180/Math.PI:39;
    }else{
      camera.up.set(0,0,1);const offsets={chase:[-3.6,-2.4,2],side:[1.5,-4,2.0],overhead:[3,0,8]};
      const v=new T.Vector3(...offsets[name]).applyAxisAngle(new T.Vector3(0,0,1),yaw);
      camera.position.set(...f.camera_position).add(v);controls.target.set(...f.camera_position).add(new T.Vector3(5,0,-.15).applyAxisAngle(new T.Vector3(0,0,1),yaw));camera.fov=64;
    }
    camera.updateProjectionMatrix();controls.update();root.dataset.jointPreset=name;
    root.querySelectorAll('[data-joint-preset]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.jointPreset===name)));
  }
  function point(x,y,d,view=activeView()){
    const K=model.intrinsics[view],C=model.camera_to_world[view],u=x*model.stride+model.ray_pixel_offset,v=y*model.stride+model.ray_pixel_offset;
    const q=[(u-K[0][2])*d/K[0][0],(v-K[1][2])*d/K[1][1],d];
    return C.slice(0,3).map(r=>r[0]*q[0]+r[1]*q[1]+r[2]*q[2]+r[3]);
  }
  async function setFrame(value,{move=false}={}){
    index=Number(value);slider.value=String(index);time.textContent=`${frameData().time_seconds.toFixed(1)} s · ${index+1}/17`;marker.visible=false;
    car.position.set(...frameData().ground_position);car.rotation.z=frameData().yaw_radians;
    const thisRevision=++revision;
    if(model){
      const [w,h]=model.grid,n=w*h,view=activeView(),depth=buffers.get(model.id).subarray(view*n,(view+1)*n);
      let totalTriangles=0;surfaces.forEach(s=>s.visible=false);
      const textureJobs=[];
      for(let slot=0;slot<model.views_per_frame;slot++){
      const v=index*model.views_per_frame+slot,values=buffers.get(model.id).subarray(v*n,(v+1)*n),mesh=surfaces[slot];
      if(mesh.geometry.getAttribute('position')?.count!==n||mesh.userData.model!==model.id){
        mesh.geometry.dispose();mesh.geometry=new T.BufferGeometry();
        mesh.userData.model=model.id;
        mesh.geometry.setAttribute('position',new T.BufferAttribute(new Float32Array(n*3),3).setUsage(T.DynamicDrawUsage));
        const uv=new Float32Array(n*2);for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x;uv[i*2]=(x*model.stride+.5)/model.source_shape[2];uv[i*2+1]=1-(y*model.stride+.5)/model.source_shape[1];}
        mesh.geometry.setAttribute('uv',new T.BufferAttribute(uv,2));
        mesh.geometry.setIndex(new T.BufferAttribute(new Uint32Array((w-1)*(h-1)*6),1).setUsage(T.DynamicDrawUsage));
      }
      const geometry=mesh.geometry,positions=geometry.getAttribute('position').array,indices=geometry.getIndex().array,K=model.intrinsics[v],C=model.camera_to_world[v];let count=0;
      for(let y=0;y<h;y++)for(let x=0;x<w;x++){
        const i=y*w+x,d=values[i]/65535*model.depth_max;
        const X=(x*model.stride+model.ray_pixel_offset-K[0][2])*d/K[0][0],Y=(y*model.stride+model.ray_pixel_offset-K[1][2])*d/K[1][1];
        positions[i*3]=C[0][0]*X+C[0][1]*Y+C[0][2]*d+C[0][3];positions[i*3+1]=C[1][0]*X+C[1][1]*Y+C[1][2]*d+C[1][3];positions[i*3+2]=C[2][0]*X+C[2][1]*Y+C[2][2]*d+C[2][3];
      }
      const triangle=(a,b,c)=>{const za=values[a],zb=values[b],zc=values[c],lo=Math.min(za,zb,zc),hi=Math.max(za,zb,zc);if(lo>0&&hi/lo<1.1){indices[count++]=a;indices[count++]=b;indices[count++]=c;}};
      for(let y=0;y<h-1;y++)for(let x=0;x<w-1;x++){const i=y*w+x;triangle(i,i+w,i+1);triangle(i+1,i+w,i+w+1);}
      geometry.getAttribute('position').needsUpdate=true;geometry.getIndex().needsUpdate=true;geometry.setDrawRange(0,count);
      totalTriangles+=count/3;
      textureJobs.push(texture(base+model.rgb[v]).then(tex=>{if(!dead&&thisRevision===revision){mesh.material.map=tex;mesh.material.needsUpdate=true;mesh.visible=true;}}));
      }
      rgb.src=base+model.rgb[view];
      depthCanvas.width=w;depthCanvas.height=h;const ctx=depthCanvas.getContext('2d'),im=ctx.createImageData(w,h);
      for(let i=0;i<n;i++){const d=depth[i]/65535*model.depth_max,t=Math.min(1,Math.log1p(d)/Math.log1p(40)),off=i*4;im.data[off]=depth[i]?Math.round(255*(1-t)):220;im.data[off+1]=depth[i]?Math.round(210*(1-t*t)):225;im.data[off+2]=depth[i]?Math.round(80+175*t):229;im.data[off+3]=255;}ctx.putImageData(im,0,0);
      try{await Promise.all(textureJobs);}catch(error){if(dead||thisRevision!==revision)return;throw error;}if(dead||thisRevision!==revision)return;
      const keep=new Set(model.rgb.slice(index*model.views_per_frame,(index+1)*model.views_per_frame).map(x=>base+x));
      for(const [url,promise] of textures){if(textures.size<=24)break;if(!keep.has(url)){textures.delete(url);void promise.then(t=>t.dispose()).catch(()=>{});}}
      if(baseline)baseline.visible=false;
      status.textContent=ko?`${modelLabel(model)} · 프레임별 깊이 메시 · 관측 RGB 색상 · 보이지 않은 영역은 비워둡니다.`:`${model.label} · per-frame depth mesh · observed RGB texture · unseen areas remain empty.`;
      root.dataset.jointTriangles=String(totalTriangles);
    }else{
      surfaces.forEach(s=>s.visible=false);if(baseline)baseline.visible=true;
      const observed=manifest.models[0];rgb.src=base+observed.rgb[index];depthCanvas.getContext('2d').clearRect(0,0,depthCanvas.width,depthCanvas.height);
      status.textContent=ko?'기존 NuRec: 모든 시간의 RGB로 학습한 정적 Gaussian 장면입니다. 주변 차량의 잔상이 남을 수 있습니다.':'Existing NuRec: one static Gaussian scene trained over time. Moving traffic can leave ghosts.';
    }
    if(move||preset==='input')setPreset(preset);root.dataset.jointFrame=String(index);
  }
  await loadModel(model);await setFrame(index);setPreset('chase');
  const resize=new ResizeObserver(()=>{camera.aspect=stage.clientWidth/stage.clientHeight;camera.updateProjectionMatrix();renderer.setSize(stage.clientWidth,stage.clientHeight);});resize.observe(stage);
  let visible=true;const observer=new IntersectionObserver(([e])=>visible=e.isIntersecting);observer.observe(stage);
  const updateError=error=>{if(!dead){status.textContent=ko?'이 프레임의 RGB를 불러오지 못했습니다. 다른 프레임을 선택해 다시 시도하세요.':'Could not load this RGB frame. Select another frame to retry.';console.error(error);}};
  let last=performance.now();renderer.setAnimationLoop(()=>{const now=performance.now(),dt=Math.min((now-last)/1000,.1);last=now;if(dead||!visible||document.hidden)return;controls.update();renderer.render(scene,camera);history.push(now);if(history.length>240)history.shift();if(playing){clock+=dt;if(clock>=.3){clock=0;void setFrame((index+1)%17,{move:true}).catch(updateError);}}});
  const onModel=async()=>{
    select.disabled=true;playing=false;play.textContent=ko?'재생':'Play';status.textContent=ko?'실제 모델 출력을 불러오는 중…':'Loading actual model outputs…';
    const previous=model;
    try{
      if(select.value==='nurec'){
        if(!baseline){spark=new SparkRenderer({renderer});scene.add(spark);baseline=new SplatMesh({url:base+'../nurec-rgb-reality/guided.spz'});await baseline.initialized;scene.add(baseline);}
        model=null;
      }else{const next=manifest.models.find(m=>m.id===select.value);await loadModel(next);model=next;}
      updateCameraOptions();await setFrame(index);root.dataset.jointModel=model?.id??'nurec';
    }catch(e){model=previous;select.value=previous?.id??'nurec';status.textContent=ko?'출력을 열지 못했습니다. 이전 장면을 유지합니다.':'Could not open these outputs. Previous scene retained.';console.error(e);}
    finally{select.disabled=false;}
  };
  const onFrame=()=>{playing=false;play.textContent=ko?'재생':'Play';void setFrame(slider.value,{move:true}).catch(updateError);};
  const onPlay=()=>{playing=!playing;clock=0;play.textContent=playing?(ko?'일시 정지':'Pause'):(ko?'재생':'Play');};
  const onPixel=e=>{
    if(!model)return;const b=rgb.getBoundingClientRect(),[w,h]=model.grid,x=Math.min(w-1,Math.max(0,Math.floor((e.clientX-b.left)/b.width*w))),y=Math.min(h-1,Math.max(0,Math.floor((e.clientY-b.top)/b.height*h)));
    const value=buffers.get(model.id)[activeView()*w*h+y*w+x],d=value/65535*model.depth_max;
    if(!value){info.textContent=ko?'이 픽셀은 신뢰도·거리 필터에서 제외됐습니다.':'This pixel was excluded by the confidence/range display filter.';marker.visible=false;return;}
    const xyz=point(x,y,d);marker.position.set(...xyz);marker.visible=true;
    info.textContent=`RGB (${x*model.stride}, ${y*model.stride}) → Z ${d.toFixed(3)} → XYZ [${xyz.map(v=>v.toFixed(3)).join(', ')}] · ${ko?'상대 단위':'relative units'}`;
  };
  const handlers=[];root.querySelectorAll('[data-joint-preset]').forEach(b=>{const fn=()=>setPreset(b.dataset.jointPreset);b.addEventListener('click',fn);handlers.push([b,fn]);});
  const onSource=()=>void setFrame(index,{move:true}).catch(updateError);sourceSelect.addEventListener('change',onSource);updateCameraOptions();select.value=model.id;
  select.addEventListener('change',onModel);slider.addEventListener('input',onFrame);play.addEventListener('click',onPlay);rgb.addEventListener('click',onPixel);
  root.querySelectorAll('[data-joint-model],[data-joint-frame],[data-joint-play],[data-joint-preset]').forEach(e=>e.disabled=false);
  root.dataset.jointReady='true';root.dataset.jointModel=model.id;
  root.jointViewerState=()=>({model:model?.id??'nurec',frame:index,preset,camera:camera.position.toArray(),target:controls.target.toArray(),triangles:Number(root.dataset.jointTriangles),fps:history.length>1?(history.length-1)*1000/(history.at(-1)-history[0]):null});
  return()=>{dead=true;revision++;renderer.setAnimationLoop(null);resize.disconnect();observer.disconnect();controls.dispose();surfaces.forEach(s=>{s.geometry.dispose();s.material.dispose();});marker.geometry.dispose();marker.material.dispose();baseline?.dispose();spark?.dispose();gltf.scene.traverse(o=>{o.geometry?.dispose();if(o.material)for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose();});for(const promise of textures.values())void promise.then(t=>t.dispose()).catch(()=>{});select.removeEventListener('change',onModel);sourceSelect.removeEventListener('change',onSource);slider.removeEventListener('input',onFrame);play.removeEventListener('click',onPlay);rgb.removeEventListener('click',onPixel);handlers.forEach(([b,fn])=>b.removeEventListener('click',fn));renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();delete root.jointViewerState;};
}
