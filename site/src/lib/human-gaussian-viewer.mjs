import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {SparkRenderer,ExtSplats,SplatMesh} from '@sparkjsdev/spark';
import {TemporalGaussians} from './human-gaussian-temporal.mjs';
import {SomaSkinnedGaussians} from './human-gaussian-soma.mjs';
import {humanGaussianCopy} from './human-gaussian-markup.mjs';

const finite = (value,name) => {if(!Number.isFinite(value))throw Error(`Invalid ${name}`);return value;};
function createAssets({manifestUrl}){
  if(!manifestUrl)throw Error('No published 3D example is configured');
  const manifestBase=new URL(manifestUrl,location.href).href;
  const url=(path,base=manifestBase)=>new URL(path,base).href;
  return {manifestBase,url,
    directory(path,base=manifestBase){return url(path.endsWith('/')?path:path+'/',base);},
    async json(path,base=manifestBase,signal){const response=await fetch(url(path,base),{signal,cache:'no-cache'});if(!response.ok)throw Error(`Cannot read ${path}: ${response.status}`);return response.json();},
    async bytes(path,base=manifestBase,signal,identity=''){
      let target=url(path,base);if(identity){const u=new URL(target);u.searchParams.set('v',identity.slice(0,16));target=u.href;}
      const response=await fetch(target,{signal});if(!response.ok)throw Error(`Cannot read ${path}: ${response.status}`);
      let buffer=await response.arrayBuffer();const head=new Uint8Array(buffer,0,Math.min(2,buffer.byteLength));
      // A static host may already apply Content-Encoding. Inspect the magic.
      if(head[0]===0x1f&&head[1]===0x8b){if(!globalThis.DecompressionStream)throw Error('This browser cannot decode gzip model data');buffer=await new Response(new Blob([buffer]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();}
      return buffer;
    },
  };
}
function validateManifest(manifest){
  finite(manifest.duration,'duration');finite(manifest.fps,'fps');
  if(manifest.schema!==1||manifest.duration<=0||manifest.duration>600||manifest.fps<=0||manifest.fps>120||!Array.isArray(manifest.segments)||!manifest.segments.length||manifest.segments.length>200)throw Error('Unsupported Gaussian manifest');
  let previous=-1;for(const segment of manifest.segments){if(!Number.isFinite(segment.start)||segment.start<0||segment.start<=previous||!segment.root||!Number.isFinite(segment.duration)||segment.duration<=0)throw Error('Invalid segment timeline');previous=segment.start;}
  if(manifest.segments[0].start!==0)throw Error('The first segment must start at zero');return manifest;
}
function safeLink(value){try{const url=new URL(value);return /^https?:$/.test(url.protocol)?url.href:null;}catch{return null;}}

/** Mount one isolated comparison. Assets are fetched only after explicit action. */
export async function mountHumanGaussianViewer(root,{manifestUrl=root.dataset.manifest}={}){
  const ko=root.dataset.locale==='ko',copy=humanGaussianCopy[ko?'ko':'en'];
  const q=name=>root.querySelector(`[data-hg-${name}]`),source=q('source'),stage=q('stage'),pair=q('pair'),status=q('status'),cover=q('cover');
  const initial={sourceHidden:source.hidden,youtubeHidden:q('youtube')?.hidden,sourcePoster:source.getAttribute('poster'),sourceEmptyHidden:q('source-empty').hidden,texts:Object.fromEntries(['source-title','source-badge','model-title','model-badge','notice','help'].map(name=>[name,q(name)?.textContent??''])),credit:[...q('credit').childNodes].map(node=>node.cloneNode(true))};
  if(q('poster'))q('poster').hidden=true;source.removeAttribute('poster');
  const assets=createAssets({manifestUrl});let abort=new AbortController(),disposed=false,revision=0;
  const state={ready:false,buffering:false,playing:true,seconds:0,segment:-1,orbit:false,errors:[],renderedFrames:0,prefetch:null,lastLoadTimings:null};
  const listeners=[];const listen=(el,event,fn,options)=>{el.addEventListener(event,fn,options);listeners.push(()=>el.removeEventListener(event,fn,options));};
  let mesh,packed,modifier,meta,fields,motion,variance,sh,indices,weights,matrices,nextCache=null;
  let renderer,controls,spark,resize,scene,camera,grid,manifest;const inverse=new THREE.Matrix4(),localCamera=new THREE.Vector3();
  const text=(name,value)=>{const node=q(name);if(node)node.textContent=value;};
  const loading=busy=>{stage.setAttribute('aria-busy',String(busy));if(busy)root.dataset.loading='true';else delete root.dataset.loading;q('load').hidden=false;q('load').disabled=busy;text('load-label',busy?copy.loading:copy.load);};
  const fail=error=>{if(error?.name==='AbortError'||disposed)return;state.errors.push(String(error));state.ready=false;play(false);delete root.dataset.ready;q('controls').hidden=true;status.textContent=copy.loadError;cover.hidden=false;text('cover-message',copy.loadError);loading(false);text('load-label',copy.retry);if(!mesh&&q('poster'))q('poster').hidden=false;root.dispatchEvent(new CustomEvent('hg-error',{detail:String(error)}));console.error('Human Gaussian viewer:',error);};
  let currentFit=1;
  const fitFactor=aspect=>{const config=manifest?.camera??meta?.camera??{};const ratio=config.framing_aspect??(config.source_width&&config.source_height?config.source_width/config.source_height:source.videoWidth&&source.videoHeight?source.videoWidth/source.videoHeight:9/16);return Math.max(1,ratio/aspect);};
  const cleanupModel=()=>{if(mesh){scene.remove(mesh);mesh.dispose();mesh=null;}if(packed?.dispose)packed.dispose();packed=null;if(modifier?.dispose)modifier.dispose();else if(modifier?.uniform?.value){for(const name of ['motion','variance','sh'])modifier.uniform.value[name]?.dispose?.();}modifier=null;fields=motion=variance=sh=indices=weights=matrices=null;};
  function view(name='front'){
    state.orbit=false;q('orbit').setAttribute('aria-pressed','false');
    if(!camera)return;const config=manifest.camera??meta?.camera??{},target=config.target??[0,.85,0],position=config.position;const fit=fitFactor(camera.aspect);currentFit=fit;const distance=(config.distance??(position?Math.hypot(position[0]-target[0],position[2]-target[2]):2.8))*fit,heightOffset=(position?position[1]-target[1]:.08)*fit;
    camera.fov=config.fov??42;camera.updateProjectionMatrix();
    const directions={front:[0,heightOffset,distance],left:[-distance,heightOffset,0],right:[distance,heightOffset,0],back:[0,heightOffset,-distance]};camera.position.fromArray(target).add(new THREE.Vector3().fromArray(directions[name]??directions.front));controls.target.fromArray(target);controls.update();
    text('view-label',copy[name]??copy.front);
    root.querySelectorAll('[data-hg-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.hgView===name)));
  }
  function fitView(){
    if(!camera)return;state.orbit=false;q('orbit').setAttribute('aria-pressed','false');
    const config=manifest.camera??meta?.camera??{},target=new THREE.Vector3().fromArray(config.target??[0,.85,0]),position=config.position;
    const offset=camera.position.clone().sub(controls.target),angle=Math.atan2(offset.x,offset.z),fit=fitFactor(camera.aspect);
    const distance=(config.distance??(position?Math.hypot(position[0]-target.x,position[2]-target.z):2.8))*fit;
    camera.position.copy(target).add(new THREE.Vector3(Math.sin(angle)*distance,(position?position[1]-target.y:.08)*fit,Math.cos(angle)*distance));controls.target.copy(target);
    camera.fov=config.fov??42;camera.updateProjectionMatrix();currentFit=fit;controls.update();
  }
  function play(value){
    state.playing=value;text('play',value?copy.pause:copy.play);
    if(value&&!state.buffering&&source.src)source.play().catch(error=>{if(error.name==='NotAllowedError'&&!disposed){state.playing=false;text('play',copy.play);status.textContent=ko?'재생 버튼을 눌러 두 화면을 시작하세요.':'Press Play to start both panels.';}});else source.pause();
  }
  const alignSource=()=>{if(disposed||!source.src)return;if(source.readyState>=1&&Math.abs(source.currentTime-state.seconds)>.025){try{source.currentTime=state.seconds;}catch{}}};
  listen(source,'loadedmetadata',()=>{alignSource();if(state.playing&&!state.buffering)play(true);});
  listen(source,'loadeddata',alignSource);
  const segmentAt=seconds=>{let index=0;for(let i=1;i<manifest.segments.length;i++){if(manifest.segments[i].start<=seconds)index=i;else break;}return index;};
  const yieldBrowser=()=>new Promise(resolve=>setTimeout(resolve,0));
  async function prepareSegment(index,signal){
    const began=performance.now();
      const segment=manifest.segments[index],base=assets.directory(segment.root),nextMeta=await assets.json(segment.meta??'meta.json',base,signal);
      const count=nextMeta.gaussians;if(!Number.isSafeInteger(count)||count<1||count>5_000_000||!Number.isInteger(nextMeta.frames)||nextMeta.frames<1)throw Error('Invalid Gaussian count or frame count');
      const isRig=nextMeta.representation==='soma-skinned-gaussians';
      const read=async(name,Type)=>{const record=nextMeta.files?.[name];const buffer=await assets.bytes(name,base,signal,record?.raw_sha256);if(record?.raw_bytes&&record.raw_bytes!==buffer.byteLength)throw Error(`Unexpected byte length: ${name}`);return new Type(buffer);};
      let payload;
      if(isRig){
        if(!Number.isInteger(nextMeta.bones)||nextMeta.bones<1||nextMeta.bones>512||![4,8].includes(nextMeta.influences??8))throw Error('Invalid SOMA skinning dimensions');
        payload=await Promise.all([read('gaussians.f32.gz',Float32Array),read('bone-indices.u16.gz',Uint16Array),read('bone-weights.f32.gz',Float32Array),read('bone-matrices.f32.gz',Float32Array)]);
        if(payload[1].length!==count*(nextMeta.influences??8)||payload[2].length!==payload[1].length||payload[3].length!==nextMeta.frames*nextMeta.bones*16)throw Error('SOMA skinning array dimensions differ');
      }else{
        payload=await Promise.all([read('gaussians.f32.gz',Float32Array),read('motion.f32.gz',Float32Array),read('variance.f32.gz',Float32Array),read('sh.f16.gz',Uint16Array)]);
        if(payload[1].length!==count*4||payload[2].length!==count*4||payload[3].length!==count*48)throw Error('Conditional 4D array dimensions differ');
      }
      if(payload[0].length!==count*14)throw Error('Gaussian field dimensions differ');
      if(signal.aborted)throw new DOMException('Aborted','AbortError');
      const fetched=performance.now(),nextFields=payload[0];
      const v=new THREE.Vector3(),s=new THREE.Vector3(),r=new THREE.Quaternion(),color=new THREE.Color();const candidatePacked=new ExtSplats({maxSplats:count});
      try{
        let i=0;
        while(i<count){
          const deadline=performance.now()+8;
          do{
            const limit=Math.min(count,i+256);
            for(;i<limit;i++){
              const p=i*14;for(let k=0;k<14;k++)if(!Number.isFinite(nextFields[p+k]))throw Error('Nonfinite Gaussian fields');
              v.fromArray(nextFields,p);s.fromArray(nextFields,p+3);r.fromArray(nextFields,p+6);color.setRGB(nextFields[p+11],nextFields[p+12],nextFields[p+13]);candidatePacked.pushSplat(v,s,r,nextFields[p+10],color);
            }
          }while(i<count&&performance.now()<deadline);
          if(signal.aborted)throw new DOMException('Aborted','AbortError');
          if(i<count)await yieldBrowser();
        }
        candidatePacked.initialize({extArrays:candidatePacked.extArrays,numSplats:count});
        return {segment,nextMeta,count,isRig,payload,candidatePacked,timings:{fetchDecodeMs:fetched-began,packMs:performance.now()-fetched}};
      }catch(error){candidatePacked.dispose?.();throw error;}
  }
  function cancelPrefetch(){
    if(!nextCache)return;const previous=nextCache;nextCache=null;previous.controller.abort();
    previous.promise.then(value=>{if(!previous.consumed)value.candidatePacked.dispose?.();},()=>{});state.prefetch=null;
  }
  function prefetchNext(index){
    if(disposed||manifest.segments.length<2)return;
    const next=(index+1)%manifest.segments.length;if(nextCache?.index===next)return;cancelPrefetch();
    const entry={index:next,controller:new AbortController(),consumed:false,promise:null};
    state.prefetch={segment:next,ready:false};
    entry.promise=prepareSegment(next,entry.controller.signal).then(value=>{if(!disposed&&nextCache===entry)state.prefetch={segment:next,ready:true,timings:value.timings};return value;});
    entry.promise.catch(error=>{if(!disposed&&nextCache===entry&&error.name!=='AbortError')state.prefetch={segment:next,ready:false,error:String(error)};});
    nextCache=entry;
  }
  async function openSegment(index){
    if(disposed)return;
    if(index===state.segment&&state.ready){if(state.buffering){revision++;abort.abort();state.buffering=false;cover.hidden=true;loading(false);play(state.playing);prefetchNext(index);}return;}
    const token=++revision;abort.abort();abort=new AbortController();const signal=abort.signal;
    state.buffering=true;source.pause();cover.hidden=false;loading(true);
    const message=ko?`${index+1}/${manifest.segments.length} 구간 준비 중…`:`Preparing motion segment ${index+1}/${manifest.segments.length}…`;
    text('cover-message',message);status.textContent=message;
    try{
      const started=performance.now();let prepared,usedPrefetch=false;
      if(nextCache?.index===index){
        const cached=nextCache;nextCache=null;cached.consumed=true;state.prefetch=null;signal.addEventListener('abort',()=>cached.controller.abort(),{once:true});
        try{prepared=await cached.promise;usedPrefetch=true;}catch(error){if(signal.aborted)throw error;prepared=await prepareSegment(index,signal);}
      }else{cancelPrefetch();prepared=await prepareSegment(index,signal);}
      const {segment,nextMeta,count,isRig,payload,candidatePacked}=prepared,nextFields=payload[0];
      if(token!==revision||disposed){candidatePacked.dispose?.();return;}
      const candidateMesh=new SplatMesh({extSplats:candidatePacked,covSplats:true,enableLod:false,raycastable:false});await candidateMesh.initialized;
      if(token!==revision||disposed){candidateMesh.dispose();candidatePacked.dispose?.();return;}
      cleanupModel();meta=nextMeta;fields=nextFields;packed=candidatePacked;mesh=candidateMesh;
      if(isRig){[fields,indices,weights,matrices]=payload;modifier=new SomaSkinnedGaussians(meta,indices,weights,matrices);}else{[fields,motion,variance,sh]=payload;modifier=new TemporalGaussians(meta,motion,variance,sh);}
      mesh.objectModifier=modifier.modifier;mesh.updateGenerator();mesh.position.fromArray(segment.translation??[0,0,0]);mesh.quaternion.fromArray(segment.rotation??[0,0,0,1]);mesh.updateMatrixWorld(true);inverse.copy(mesh.matrixWorld).invert();scene.add(mesh);
      const firstModel=state.segment<0;state.segment=index;state.ready=true;state.buffering=false;cover.hidden=true;loading(false);root.dataset.ready='true';q('controls').hidden=false;
      text('source-title',(ko?manifest.source?.title_ko:undefined)??manifest.source?.title??(isRig?(ko?'SOMA 합성 RGB · 제어 샘플':'SOMA synthetic RGB · control'):copy.observed));
      text('source-badge',manifest.source?.youtube_id?'YOUTUBE':manifest.sample_kind==='soma-synthetic-control'?(ko?'합성 렌더':'SYNTHETIC RENDER'):copy.observedBadge);text('model-title',isRig?(manifest.sample_kind==='soma-synthetic-control'?(ko?'SOMA 리깅 Gaussian 제어 샘플':'SOMA rigged Gaussian control'):(ko?'SOMA 리깅 인체 Gaussians':'SOMA-skinned human Gaussians')):copy.reconstructed);text('model-badge',manifest.sample_kind==='soma-synthetic-control'?(ko?'알려진 리깅':'KNOWN RIG'):copy.inferredBadge);
      text('notice',manifest.sample_kind==='soma-synthetic-control'?(ko?'SOMA의 공식 예제 동작을 Gaussian으로 표시한 합성 샘플입니다.':'A synthetic Gaussian sample driven by SOMA’s official example motion.'):copy.notice);
      status.textContent=ko?'3D 준비 완료':'3D ready';
      alignSource();
      state.lastLoadTimings={segment:index,usedPrefetch,blockingMs:performance.now()-started,...prepared.timings};
      if(firstModel)view('front');play(state.playing);prefetchNext(index);root.dispatchEvent(new CustomEvent('hg-ready',{detail:{segment:index,meta,manifest}}));
    }catch(error){if(token===revision){state.buffering=false;play(false);fail(error);}}
  }
  function seek(seconds){
    if(!manifest)return;state.seconds=Math.max(0,Math.min(manifest.duration-1/manifest.fps,seconds));if(source.src&&source.readyState>=1)source.currentTime=state.seconds;
    const wanted=segmentAt(state.seconds);if(wanted!==state.segment)void openSegment(wanted);
  }
  try{
    manifest=validateManifest(await assets.json(assets.manifestBase,undefined,abort.signal));
    q('seek').max=String(Math.max(0,Math.ceil(manifest.duration*manifest.fps)-1));
    if(manifest.source?.url){source.src=assets.url(manifest.source.url);source.hidden=false;if(q('youtube'))q('youtube').hidden=true;q('source-empty').hidden=true;text('help',copy.help);}
    const credit=q('credit');credit.replaceChildren();
    const citation=safeLink(manifest.source?.attribution_url);
    if(citation){const a=document.createElement('a');a.href=citation;a.textContent=manifest.source?.credit??copy.sourceCredit;a.target='_blank';a.rel='noopener noreferrer';credit.append(a);}
    else if(manifest.source?.credit)credit.textContent=manifest.source.credit;
    if(manifest.source?.license){const span=document.createElement('span');span.textContent=manifest.source.license;credit.append(document.createTextNode(' · '),span);}
    renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true,powerPreference:'low-power'});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setClearColor(0xf3f4f5);renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('aria-label',ko?'회전 가능한 인체 Gaussian 모델':'Orbitable human Gaussian model');stage.append(renderer.domElement);
    scene=new THREE.Scene();scene.background=new THREE.Color(0xf3f4f5);camera=new THREE.PerspectiveCamera(42,1,.01,50);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.12;controls.minDistance=.5;controls.maxDistance=8;controls.maxPolarAngle=Math.PI*.6;controls.rotateSpeed=.5;controls.listenToKeyEvents(renderer.domElement);
    spark=new SparkRenderer({renderer,enableLod:false,accumExtSplats:true,covSplats:true,preUpdate:true,blurAmount:.15});scene.add(spark);
    resize=new ResizeObserver(()=>{if(!stage.clientWidth||!stage.clientHeight)return;renderer.setSize(stage.clientWidth,stage.clientHeight,false);camera.aspect=stage.clientWidth/stage.clientHeight;const fit=fitFactor(camera.aspect);const offset=camera.position.clone().sub(controls.target).multiplyScalar(fit/currentFit);camera.position.copy(controls.target).add(offset);currentFit=fit;camera.updateProjectionMatrix();});resize.observe(stage);view('front');
    const freeView=()=>{text('view-label',ko?'자유 시점':'Free view');root.querySelectorAll('[data-hg-view]').forEach(button=>button.setAttribute('aria-pressed','false'));};
    listen(controls,'start',()=>{state.orbit=false;q('orbit').setAttribute('aria-pressed','false');freeView();});
    listen(q('play'),'click',()=>play(!state.playing));listen(q('seek'),'input',event=>seek(Number(event.target.value)/manifest.fps));listen(q('orbit'),'click',()=>{state.orbit=!state.orbit;q('orbit').setAttribute('aria-pressed',String(state.orbit));freeView();});listen(q('fit'),'click',fitView);
    for(const button of root.querySelectorAll('[data-hg-view]'))listen(button,'click',()=>view(button.dataset.hgView));
    listen(renderer.domElement,'keydown',event=>{if(event.code==='Space'){event.preventDefault();play(!state.playing);}});
    listen(source,'ended',()=>{seek(0);if(state.playing&&!state.buffering)source.play().catch(()=>{});});
    let previous=performance.now();renderer.setAnimationLoop(now=>{
      const dt=Math.min(.05,(now-previous)/1000);previous=now;if(disposed||document.hidden)return;
      if(state.ready&&!state.buffering){
        if(state.playing){if(source.src){if(!source.paused&&!source.seeking&&source.readyState>=2)state.seconds=source.currentTime;}else state.seconds+=dt;if(state.seconds>=manifest.duration){state.seconds=0;if(source.src)source.currentTime=0;}}
        const wanted=segmentAt(state.seconds);if(wanted!==state.segment&&pair.dataset.mode!=='source'){void openSegment(wanted);}else{
          if(state.orbit){const offset=camera.position.clone().sub(controls.target);offset.applyAxisAngle(new THREE.Vector3(0,1,0),dt*.4);camera.position.copy(controls.target).add(offset);text('view-label',ko?'자동 회전':'Auto orbit');}
          controls.update();localCamera.copy(camera.position).applyMatrix4(inverse);modifier.update(state.seconds-manifest.segments[state.segment].start+(manifest.segments[state.segment].time_offset??0),localCamera);mesh.needsUpdate=true;state.renderedFrames++;
          q('seek').value=String(Math.min(Number(q('seek').max),Math.round(state.seconds*manifest.fps)));text('time',`${state.seconds.toFixed(2)} / ${manifest.duration.toFixed(2)} s`);
        }
      }
      if(pair.dataset.mode!=='source')renderer.render(scene,camera);
    });
    await openSegment(0);
    if(state.ready)root.querySelectorAll('[data-hg-play],[data-hg-seek],[data-hg-view],[data-hg-orbit],[data-hg-fit],[data-hg-close]').forEach(button=>button.disabled=false);
  }catch(error){fail(error);}
  const api={state,get manifest(){return manifest;},get meta(){return meta;},get fields(){return fields;},get motion(){return motion;},get variance(){return variance;},get indices(){return indices;},get weights(){return weights;},get matrices(){return matrices;},get camera(){return camera;},get renderer(){return renderer;},seek,play,view,
    sample(index,seconds){if(!meta)return null;if(meta.representation==='soma-skinned-gaussians'){
      const frame=Math.min(meta.frames-1,Math.max(0,seconds*meta.fps)),f0=Math.floor(frame),f1=Math.min(f0+1,meta.frames-1),blend=frame-f0,p=Array.from(fields.subarray(index*14,index*14+3)),out=[0,0,0],influences=meta.influences??8;
      for(let j=0;j<influences;j++){const bone=indices[index*influences+j],weight=weights[index*influences+j];for(let k=0;k<3;k++){let a=0,b=0;for(let c=0;c<4;c++){const coordinate=c===3?1:p[c];a+=matrices[((f0*meta.bones+bone)*4+k)*4+c]*coordinate;b+=matrices[((f1*meta.bones+bone)*4+k)*4+c]*coordinate;}out[k]+=weight*(a*(1-blend)+b*blend);}}
      return {position:out,opacity:fields[index*14+10]};
    }const dt=seconds-motion[index*4+3];return {position:[0,1,2].map(k=>fields[index*14+k]+motion[index*4+k]*dt),opacity:fields[index*14+10]*Math.exp(-.5*dt*dt*variance[index*4])};},
    dispose(){if(disposed)return;disposed=true;state.ready=false;state.buffering=false;state.playing=false;abort.abort();cancelPrefetch();for(const remove of listeners)remove();renderer?.setAnimationLoop(null);resize?.disconnect();controls?.dispose();cleanupModel();grid?.geometry.dispose();grid?.material.dispose();spark?.dispose();renderer?.dispose();renderer?.forceContextLoss();renderer?.domElement.remove();source.pause();source.removeAttribute('src');source.hidden=initial.sourceHidden;if(q('youtube'))q('youtube').hidden=initial.youtubeHidden;if(initial.sourcePoster)source.setAttribute('poster',initial.sourcePoster);else source.removeAttribute('poster');source.load();q('source-empty').hidden=initial.sourceEmptyHidden;if(q('poster'))q('poster').hidden=false;for(const [name,value] of Object.entries(initial.texts))text(name,value);q('credit').replaceChildren(...initial.credit.map(node=>node.cloneNode(true)));text('view-label',copy.front);q('orbit').setAttribute('aria-pressed','false');root.querySelectorAll('[data-hg-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.hgView==='front')));delete root.dataset.ready;q('controls').hidden=true;cover.hidden=false;text('cover-message',copy.loadHint);loading(false);root.querySelectorAll('[data-hg-play],[data-hg-seek],[data-hg-view],[data-hg-orbit],[data-hg-fit],[data-hg-close]').forEach(button=>button.disabled=true);text('status',ko?'비교 화면을 닫았습니다.':'Comparison closed.');},
  };
  root.humanGaussian=api;return api;
}
