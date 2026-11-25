// Optional real GPU inference. Static Pages never probes a private backend.
import {MotionPolicy} from './motion-policy.mjs';
export function mountEnhancement({root,config,ko}) {
  if(!config.enhancement_endpoint)return;
  const endpoint=new URL(config.enhancement_endpoint,location.href);
  if(endpoint.origin!==location.origin)throw new Error('The enhancer must use the same-origin local proxy');
  const section=document.createElement('section');section.className='rgb-enhancement';
  section.innerHTML=`<h3>${ko?'현재 3D 시점을 AI로 보정하기':'Enhance the current 3D viewpoint'}</h3><p>${ko?'실제 3D 화면을 GPU 모델로 보정합니다. 이동 중에는 빠른 AI 또는 원본 3D 미리보기를, 멈추면 고화질 보정을 선택할 수 있습니다. 인식 표식·예측 경로는 원본 RGB 분석을 따로 겹칩니다.':'Enhance the actual 3D view on the GPU. Choose fast AI or browser 3D during movement, then high-quality refinement after the camera stops. Detection markers and predicted paths are overlaid separately from original RGB analysis.'}</p><div class="rgb-enhancement-controls"><button type="button" data-enhance>${ko?'현재 시점 보정':'Enhance this view'}</button><select data-enhance-mode aria-label="${ko?'보정 방식':'Enhancement mode'}"><option value="temporal">${ko?'시간축 보정 · 이전 출력 4장':'Temporal · four previous outputs'}</option><option value="independent">${ko?'프레임별 보정':'Independent frames'}</option></select><select data-enhance-execution aria-label="${ko?'실행 방식':'Execution profile'}"><option value="exact">${ko?'화질 동일 · 연속 고화질':'Exact · continuous high quality'}</option><option value="adaptive">${ko?'AI 미리보기 → 정지 후 고화질':'Fast AI preview → HQ at rest'}</option><option value="native">${ko?'브라우저 3D → 정지 후 고화질':'Browser 3D preview → HQ at rest'}</option><option value="baseline">${ko?'최적화 전 방식':'Original baseline'}</option><option value="tuned">${ko?'추가 가속 · 미세한 수치 차이':'Tuned · small numerical differences'}</option></select><label><input type="checkbox" data-enhance-auto> ${ko?'자동 갱신':'Update continuously'}</label><button type="button" data-enhance-reset>${ko?'이력 초기화':'Reset history'}</button></div><p data-enhance-status role="status">${ko?'3D 장면에서 시점을 고른 뒤 실행하세요.':'Choose a viewpoint in the 3D scene, then run enhancement.'}</p><div class="rgb-enhancement-pair" hidden><figure><figcaption>${ko?'보정에 넣은 실제 3D 렌더링':'Actual captured 3D render'}</figcaption><canvas width="1024" height="576" data-enhance-input></canvas></figure><figure><figcaption data-enhance-caption>${ko?'Harmonizer 생성 보정':'Harmonizer generated enhancement'}</figcaption><canvas width="1024" height="576" data-enhance-output></canvas></figure></div><p>Built on NVIDIA Cosmos · ${ko?'3D 미리보기 FPS와 AI가 생성해 표시한 FPS는 서로 다른 측정값입니다.':'Browser 3D preview FPS and delivered AI generation FPS are separate measurements.'}</p>`;
  root.classList.add('rgb-has-enhancer');root.append(section);
  const get=s=>section.querySelector(s),button=get('[data-enhance]'),auto=get('[data-enhance-auto]'),mode=get('[data-enhance-mode]'),execution=get('[data-enhance-execution]'),status=get('[data-enhance-status]'),caption=get('[data-enhance-caption]');
  const session=crypto.randomUUID().replaceAll('-',''),policy=new MotionPolicy({idleMs:180});let busy=false,disposed=false,timer,reset=true,lastPaint,epoch=0;
  root.rgbEnhancementHistory=[];root.rgbPresentationHistory=[];root.rgbMotionHistory=[];
  const selected=new URLSearchParams(location.search).get('execution');if(['baseline','exact','tuned','adaptive','native'].includes(selected))execution.value=selected;
  const progressive=()=>['adaptive','native'].includes(execution.value);
  const controls=()=>{mode.disabled=progressive();if(progressive())mode.value='temporal';};controls();
  function present(kind,now,resolution){root.rgbPresentationState={kind,at_ms:now,resolution,version:policy.version};root.rgbPresentationHistory.push(root.rgbPresentationState);if(root.rgbPresentationHistory.length>3600)root.rgbPresentationHistory.shift();}
  const schedule=delay=>{clearTimeout(timer);if(auto.checked&&!disposed)timer=setTimeout(()=>run(false),delay);};
  const unsubscribe=root.rgbViewerSubscribe(({canvas,now,pose})=>{
    const changed=policy.observe(pose,now);
    if(changed){root.rgbMotionHistory.push({at_ms:now,version:policy.version});if(root.rgbMotionHistory.length>3600)root.rgbMotionHistory.shift();}
    if(auto.checked&&progressive()&&policy.moving(now)&&(execution.value==='native'||root.rgbPresentationState?.kind!=='gpu-preview')){
      const w=canvas.width,h=canvas.height,cw=Math.min(w,h*16/9),ch=cw*9/16;
      for(const target of [get('[data-enhance-input]'),get('[data-enhance-output]')])target.getContext('2d').drawImage(canvas,(w-cw)/2,(h-ch)/2,cw,ch,0,0,1024,576);
      get('.rgb-enhancement-pair').hidden=false;caption.textContent=ko?'브라우저 3D 미리보기 · AI 생성 아님':'Browser 3D preview · not AI generation';
      present('native-preview',now,[w,h]);if(!busy)status.textContent=ko?'이동 중 · 원본 3D 미리보기, 멈추면 고화질 보정':'Moving · browser 3D preview; high-quality refinement follows at rest';
    }
    if(changed&&auto.checked&&progressive()&&!busy)schedule(0);
  });
  async function annotated(encoded,view,target,baseline,mime='image/png',guard=()=>true){
    const image=new Image();image.src='data:'+mime+';base64,'+encoded;await image.decode();if(!guard())return false;const canvas=baseline?document.createElement('canvas'):target;canvas.width=1024;canvas.height=576;const ctx=canvas.getContext('2d');ctx.imageSmoothingQuality='high';ctx.drawImage(image,0,0,1024,576);
    ctx.strokeStyle='#9ee34a';ctx.lineWidth=3;ctx.setLineDash([9,6]);ctx.beginPath();let connected=false;
    for(const point of view.path??[]){if(!point){connected=false;continue;}if(connected)ctx.lineTo(...point);else ctx.moveTo(...point);connected=true;}ctx.stroke();ctx.setLineDash([]);
    const names={person:'사람',car:'차량',truck:'트럭',bus:'버스',bicycle:'자전거',motorcycle:'이륜차'};
    for(const item of view.annotations??[]){const [x,y]=item.point,color=item.class==='person'?'#ffd369':'#56e2ed';ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,7,0,Math.PI*2);ctx.stroke();const label=ko?names[item.class]??item.class:item.class;ctx.font='600 17px Arial,sans-serif';const w=ctx.measureText(label).width+10;ctx.fillStyle='#09191be6';ctx.fillRect(Math.min(1024-w,x+9),Math.max(0,y-25),w,23);ctx.fillStyle=color;ctx.fillText(label,Math.min(1024-w,x+9)+5,Math.max(17,y-8));}
    if(baseline){const encoded=new Image();encoded.src=canvas.toDataURL('image/png');await encoded.decode();target.getContext('2d').drawImage(encoded,0,0);}return true;
  }
  async function run(manual=false){
    if(busy||disposed)return;
    const profile=execution.value,isProgressive=progressive(),now=performance.now();
    const job=isProgressive?(manual?{phase:'refine',width:1024,version:policy.version}:policy.next(profile,now)):{phase:'continuous',width:1024,version:policy.version};
    if(!job||document.hidden){schedule(30);return;}
    busy=true;delete root.rgbEnhancementError;button.disabled=true;const born=performance.now();
    try{
      if(root.rgbViewerState().variant==='support')throw new Error(ko?'사진 형태의 복원 모델로 바꾼 뒤 실행하세요.':'Select a photographic reconstruction before enhancement.');
      status.textContent=job.phase==='preview'?(ko?'빠른 AI 미리보기 생성 중…':'Generating fast AI preview…'):(ko?'현재 화면을 GPU에서 고화질로 보정 중…':'Enhancing the current view at full quality…');
      const capture=await root.rgbViewerCapture({asynchronous:profile!=='baseline',width:job.width}),captured=performance.now(),requestEpoch=epoch;
      const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session,mode:mode.value,execution:isProgressive?'adaptive':profile,...(isProgressive?{phase:job.phase}:{}),reset,image:capture.image,view:capture.view})});
      if(!response.ok)throw new Error(ko?'GPU 연결을 확인하세요. 로컬 프록시와 보정 서버가 필요합니다.':'Check the local GPU service and viewer proxy.');
      const result=await response.json();if(disposed)return;const received=performance.now(),current=root.rgbViewerState(),delta=current.camera.map((v,i)=>v-capture.view.camera[i]),direction=current.target.map((v,i)=>v-current.camera[i]),norm=Math.hypot(...direction),dot=direction.reduce((n,v,i)=>n+v*capture.view.forward[i]/norm,0);
      const obsolete=profile!==execution.value||current.variant!==capture.view.variant||Math.hypot(...delta)>.75||dot<Math.cos(12*Math.PI/180)||(isProgressive&&job.phase==='refine'&&job.version!==policy.version);
      if(profile!=='baseline'&&obsolete){status.textContent=ko?'시점이 바뀌어 지난 보정은 건너뜁니다.':'Skipping an obsolete viewpoint result.';root.rgbEnhancementHistory.push({...result,image:undefined,workflow:profile,discarded_stale:true,round_trip_ms:performance.now()-born,input_view:capture.view});return;}
      const guard=()=>!disposed&&requestEpoch===epoch&&profile===execution.value&&!(isProgressive&&job.phase==='refine'&&job.version!==policy.version);const a=await annotated(capture.image,capture.view,get('[data-enhance-input]'),profile==='baseline','image/png',guard);const b=await annotated(result.image,capture.view,get('[data-enhance-output]'),profile==='baseline',result.image_mime??'image/png',guard);if(!a||!b){root.rgbEnhancementHistory.push({...result,image:undefined,workflow:profile,discarded_stale:true,round_trip_ms:performance.now()-born,input_view:capture.view});return;}get('.rgb-enhancement-pair').hidden=false;
      if(requestEpoch===epoch)reset=false;
      await new Promise(requestAnimationFrame);if(!guard()){root.rgbEnhancementHistory.push({...result,image:undefined,workflow:profile,discarded_stale:true,round_trip_ms:performance.now()-born,input_view:capture.view});return;}const painted=performance.now(),interval=lastPaint?painted-lastPaint:null;lastPaint=painted;
      const kind=job.phase==='preview'?'gpu-preview':'hq';present(kind,painted,result.resolution);if(isProgressive&&kind==='hq')policy.acceptRefinement(job.version);
      caption.textContent=kind==='gpu-preview'?(ko?'빠른 AI 미리보기 · 512×288':'Fast AI preview · 512×288'):(ko?'고화질 AI 보정 · 1024×576':'High-quality AI refinement · 1024×576');
      root.rgbEnhancementState={...result,workflow:profile,round_trip_ms:painted-born,capture_ms:captured-born,response_ms:received-captured,paint_ms:painted-received,completed_at_ms:painted,update_interval_ms:interval,view_version:job.version,image:undefined,input_view:capture.view,native_frame_stats:current.frame_stats};
      root.rgbEnhancementLastCapture=capture;root.rgbEnhancementLastImage={image:result.image,mime:result.image_mime,resolution:result.resolution,sequence:result.sequence};
      status.textContent=`${caption.textContent} · GPU ${result.model_ms.toFixed(0)}ms · ${ko?'전체 응답':'Capture → paint'} ${(painted-born).toFixed(0)}ms · ${ko?'참조':'History'} ${result.history_frames}/4${result.reused_reference_slots?(ko?' · 정지 화면 참조 초기화':' · stationary reference warm start'):''} · ${isProgressive&&kind==='hq'?(ko?'고화질 완료 · GPU 대기':'HQ ready · GPU idle'):`AI ${interval?(1000/interval).toFixed(1):'—'} fps`} · 3D ${current.frame_stats?.fps?.toFixed(1)??'—'} fps`;
      root.rgbEnhancementHistory.push(root.rgbEnhancementState);if(root.rgbEnhancementHistory.length>240)root.rgbEnhancementHistory.shift();
    }catch(error){auto.checked=false;status.textContent=error.message;root.rgbEnhancementError=error.message;}
    finally{busy=false;button.disabled=false;schedule(progressive()?20:execution.value==='baseline'?100:0);}
  }
  const restart=()=>{reset=true;epoch++;lastPaint=undefined;policy.refined=-1;controls();status.textContent=ko?'다음 요청에서 보정 이력을 초기화합니다.':'The next request resets enhancement history.';};
  const toggle=()=>{clearTimeout(timer);if(auto.checked)run(false);},click=()=>run(true);
  button.addEventListener('click',click);auto.addEventListener('change',toggle);mode.addEventListener('change',restart);execution.addEventListener('change',restart);get('[data-enhance-reset]').addEventListener('click',restart);
  return ()=>{disposed=true;clearTimeout(timer);unsubscribe();button.removeEventListener('click',click);auto.removeEventListener('change',toggle);section.remove();root.classList.remove('rgb-has-enhancer');for(const key of ['rgbEnhancementState','rgbEnhancementError','rgbEnhancementHistory','rgbPresentationHistory','rgbMotionHistory','rgbPresentationState','rgbEnhancementLastCapture','rgbEnhancementLastImage'])delete root[key];};
}
