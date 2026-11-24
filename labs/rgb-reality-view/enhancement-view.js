// Optional real GPU inference through the explicitly configured local proxy.
// Public static Pages never probes localhost or pretends to run diffusion.
export function mountEnhancement({root,config,ko}) {
  if(!config.enhancement_endpoint)return;
  const endpoint=new URL(config.enhancement_endpoint,location.href);
  if(endpoint.origin!==location.origin)throw new Error('The enhancer must use the same-origin local proxy');
  const section=document.createElement('section');section.className='rgb-enhancement';
  section.innerHTML=`<h3>${ko?'현재 3D 시점을 AI로 보정하기':'Enhance the current 3D viewpoint'}</h3><p>${ko?'중앙 16:9 영역을 캡처해 실제 GPU 모델로 보냅니다. 아래는 그 시점의 생성 결과이며, 실시간 카메라 기록이나 주행 판단이 아닙니다. 인식 표식과 예측 경로는 원본 RGB 분석 결과를 보정 이후에 따로 겹칩니다.':'Capture the central 16:9 viewport and send it to the real GPU model. The result is a generated snapshot, not a camera recording or a driving decision. Detection markers and predicted paths are overlaid afterward from the original RGB analysis.'}</p><div class="rgb-enhancement-controls"><button type="button" data-enhance>${ko?'현재 시점 보정':'Enhance this view'}</button><select data-enhance-mode aria-label="${ko?'보정 방식':'Enhancement mode'}"><option value="temporal">${ko?'시간축 보정 · 이전 출력 4장':'Temporal · four previous outputs'}</option><option value="independent">${ko?'프레임별 보정':'Independent frames'}</option></select><select data-enhance-execution aria-label="${ko?'실행 방식':'Execution profile'}"><option value="exact">${ko?'화질 동일 · 기본':'Exact pixels · default'}</option><option value="baseline">${ko?'기존 방식':'Original baseline'}</option><option value="tuned">${ko?'추가 가속 · 미세한 수치 차이':'Tuned · small numerical differences'}</option></select><label><input type="checkbox" data-enhance-auto> ${ko?'자동 갱신':'Update continuously'}</label><button type="button" data-enhance-reset>${ko?'이력 초기화':'Reset history'}</button></div><p data-enhance-status role="status">${ko?'3D 장면에서 시점을 고른 뒤 실행하세요.':'Choose a viewpoint in the 3D scene, then run enhancement.'}</p><div class="rgb-enhancement-pair" hidden><figure><figcaption>${ko?'보정에 넣은 실제 3D 렌더링':'Actual captured 3D render'}</figcaption><canvas width="1024" height="576" data-enhance-input aria-label="${ko?'같은 시점의 보정 입력':'Matched input viewpoint'}"></canvas></figure><figure><figcaption>${ko?'Harmonizer 생성 보정':'Harmonizer generated enhancement'}</figcaption><canvas width="1024" height="576" data-enhance-output aria-label="${ko?'GPU에서 생성한 보정 결과':'Generated GPU enhancement'}"></canvas></figure></div><p>Built on NVIDIA Cosmos · ${ko?'생성 영상의 지연과 3D 뷰어의 화면 갱신 속도는 서로 다릅니다.':'Generated-preview latency and the native 3D viewer refresh rate are separate measurements.'}</p>`;
  root.classList.add('rgb-has-enhancer');root.append(section);const button=section.querySelector('[data-enhance]'),auto=section.querySelector('[data-enhance-auto]'),mode=section.querySelector('[data-enhance-mode]'),execution=section.querySelector('[data-enhance-execution]'),status=section.querySelector('[data-enhance-status]');
  const session=crypto.randomUUID().replaceAll('-','');let busy=false,disposed=false,timer,reset=true,lastPaint,epoch=0;root.rgbEnhancementHistory=[];
  const selected=new URLSearchParams(location.search).get('execution');if(['baseline','exact','tuned'].includes(selected))execution.value=selected;
  async function annotated(encoded,view,target,baseline,mime='image/png'){
    const image=new Image();image.src='data:'+mime+';base64,'+encoded;await image.decode();const canvas=baseline?document.createElement('canvas'):target;canvas.width=1024;canvas.height=576;const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0,1024,576);
    ctx.strokeStyle='#9ee34a';ctx.lineWidth=3;ctx.setLineDash([9,6]);ctx.beginPath();let connected=false;
    for(const point of view.path??[]){if(!point){connected=false;continue;}if(connected)ctx.lineTo(...point);else ctx.moveTo(...point);connected=true;}ctx.stroke();ctx.setLineDash([]);
    const names={person:'사람',car:'차량',truck:'트럭',bus:'버스',bicycle:'자전거',motorcycle:'이륜차'};
    for(const item of view.annotations??[]){const [x,y]=item.point,color=item.class==='person'?'#ffd369':'#56e2ed';ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,7,0,Math.PI*2);ctx.stroke();const label=ko?names[item.class]??item.class:item.class;ctx.font='600 17px Arial,sans-serif';const w=ctx.measureText(label).width+10;ctx.fillStyle='#09191be6';ctx.fillRect(Math.min(1024-w,x+9),Math.max(0,y-25),w,23);ctx.fillStyle=color;ctx.fillText(label,Math.min(1024-w,x+9)+5,Math.max(17,y-8));}
    if(baseline){const encoded=new Image();encoded.src=canvas.toDataURL('image/png');await encoded.decode();target.getContext('2d').drawImage(encoded,0,0);}
  }
  async function run(){
    if(busy||disposed)return;busy=true;delete root.rgbEnhancementError;button.disabled=true;const born=performance.now();
    try{
      if(root.rgbViewerState().variant==='support')throw new Error(ko?'사진 형태의 복원 모델로 바꾼 뒤 실행하세요.':'Select a photographic reconstruction before enhancement.');
      status.textContent=ko?'현재 화면을 캡처하고 GPU에서 보정 중…':'Capturing the current view and enhancing on the GPU…';
      const profile=execution.value;const capture=await root.rgbViewerCapture({asynchronous:profile!=='baseline'});const captured=performance.now();
      const requestEpoch=epoch;const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session,mode:mode.value,execution:profile,reset,image:capture.image,view:capture.view})});
      if(!response.ok)throw new Error(ko?'GPU 연결을 확인하세요. 로컬 프록시와 보정 서버가 필요합니다.':'Check the GPU connection; the local proxy and enhancer must be running.');
      const result=await response.json();if(disposed)return;const received=performance.now();
      if(profile!=='baseline'){
        const current=root.rgbViewerState(),delta=current.camera.map((v,i)=>v-capture.view.camera[i]);const direction=current.target.map((v,i)=>v-current.camera[i]);const norm=Math.hypot(...direction);const dot=direction.reduce((n,v,i)=>n+v*capture.view.forward[i]/norm,0);
        if(profile!==execution.value||current.variant!==capture.view.variant||Math.hypot(...delta)>.75||dot<Math.cos(12*Math.PI/180)){
          status.textContent=ko?'시점이 크게 바뀌어 지난 결과를 건너뛰고 최신 화면을 요청합니다.':'View changed: skipping an obsolete result and requesting the latest camera.';
          root.rgbEnhancementHistory.push({...result,image:undefined,discarded_stale:true,round_trip_ms:performance.now()-born,input_view:capture.view});return;
        }
      }
      await annotated(capture.image,capture.view,section.querySelector('[data-enhance-input]'),profile==='baseline');await annotated(result.image,capture.view,section.querySelector('[data-enhance-output]'),profile==='baseline',result.image_mime??'image/png');section.querySelector('.rgb-enhancement-pair').hidden=false;if(requestEpoch===epoch)reset=false;
      status.textContent=`${ko?'캡처':'Capture'} ${capture.view.time_seconds.toFixed(1)}s · ${capture.view.preset} · ${ko?'이전 출력':'Prior outputs'} ${result.history_frames}/4 · GPU ${result.model_ms.toFixed(0)}ms · ${ko?'전체 응답':'Round trip'} ${(performance.now()-born).toFixed(0)}ms${result.reset_reasons?.length?(ko?' · 시점 변경으로 이력 초기화':' · history reset for view change'):''}`;
      await new Promise(requestAnimationFrame);const painted=performance.now();const interval=lastPaint?painted-lastPaint:null;lastPaint=painted;
      root.rgbEnhancementState={...result,round_trip_ms:painted-born,capture_ms:captured-born,response_ms:received-captured,paint_ms:painted-received,completed_at_ms:painted,update_interval_ms:interval,image:undefined,input_view:capture.view,native_frame_stats:root.rgbViewerState().frame_stats};
      const hz=interval?1000/interval:0;const native=root.rgbEnhancementState.native_frame_stats?.fps;status.textContent+=` · ${profile} · AI ${hz.toFixed(1)} fps · 3D ${native?.toFixed(1)??'—'} fps`;
      root.rgbEnhancementHistory.push(root.rgbEnhancementState);if(root.rgbEnhancementHistory.length>240)root.rgbEnhancementHistory.shift();
    }catch(error){auto.checked=false;status.textContent=error.message;root.rgbEnhancementError=error.message;}
    finally{busy=false;button.disabled=false;if(auto.checked&&!disposed)timer=setTimeout(run,execution.value==='baseline'?100:0);}
  }
  const restart=()=>{reset=true;epoch++;lastPaint=undefined;status.textContent=ko?'다음 요청에서 이전 출력 이력을 비웁니다.':'The next request starts with empty history.';};
  const toggle=()=>{clearTimeout(timer);if(auto.checked)run();};button.addEventListener('click',run);auto.addEventListener('change',toggle);mode.addEventListener('change',restart);execution.addEventListener('change',restart);section.querySelector('[data-enhance-reset]').addEventListener('click',restart);
  return ()=>{disposed=true;clearTimeout(timer);button.removeEventListener('click',run);auto.removeEventListener('change',toggle);section.remove();root.classList.remove('rgb-has-enhancer');delete root.rgbEnhancementState;delete root.rgbEnhancementError;delete root.rgbEnhancementHistory;};
}
