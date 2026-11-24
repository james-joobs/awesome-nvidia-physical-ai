// Optional real GPU inference through the explicitly configured local proxy.
// Public static Pages never probes localhost or pretends to run diffusion.
export function mountEnhancement({root,config,ko}) {
  if(!config.enhancement_endpoint)return;
  const endpoint=new URL(config.enhancement_endpoint,location.href);
  if(endpoint.origin!==location.origin)throw new Error('The enhancer must use the same-origin local proxy');
  const section=document.createElement('section');section.className='rgb-enhancement';
  section.innerHTML=`<h3>${ko?'현재 3D 시점을 AI로 보정하기':'Enhance the current 3D viewpoint'}</h3><p>${ko?'중앙 16:9 영역을 캡처해 실제 GPU 모델로 보냅니다. 아래는 그 시점의 생성 결과이며, 실시간 카메라 기록이나 주행 판단이 아닙니다. 인식 표식과 예측 경로는 원본 RGB 분석 결과를 보정 이후에 따로 겹칩니다.':'Capture the central 16:9 viewport and send it to the real GPU model. The result is a generated snapshot, not a camera recording or a driving decision. Detection markers and predicted paths are overlaid afterward from the original RGB analysis.'}</p><div class="rgb-enhancement-controls"><button type="button" data-enhance>${ko?'현재 시점 보정':'Enhance this view'}</button><select data-enhance-mode aria-label="${ko?'보정 방식':'Enhancement mode'}"><option value="temporal">${ko?'시간축 보정 · 이전 출력 4장':'Temporal · four previous outputs'}</option><option value="independent">${ko?'프레임별 보정':'Independent frames'}</option></select><label><input type="checkbox" data-enhance-auto> ${ko?'자동 갱신':'Update continuously'}</label><button type="button" data-enhance-reset>${ko?'이력 초기화':'Reset history'}</button></div><p data-enhance-status role="status">${ko?'3D 장면에서 시점을 고른 뒤 실행하세요.':'Choose a viewpoint in the 3D scene, then run enhancement.'}</p><div class="rgb-enhancement-pair" hidden><figure><figcaption>${ko?'보정에 넣은 실제 3D 렌더링':'Actual captured 3D render'}</figcaption><img data-enhance-input alt="${ko?'같은 시점의 보정 입력':'Matched input viewpoint'}"></figure><figure><figcaption>${ko?'Harmonizer 생성 보정':'Harmonizer generated enhancement'}</figcaption><img data-enhance-output alt="${ko?'GPU에서 생성한 보정 결과':'Generated GPU enhancement'}"></figure></div><p>Built on NVIDIA Cosmos · ${ko?'생성 영상의 지연과 3D 뷰어의 화면 갱신 속도는 서로 다릅니다.':'Generated-preview latency and the native 3D viewer refresh rate are separate measurements.'}</p>`;
  root.classList.add('rgb-has-enhancer');root.append(section);const button=section.querySelector('[data-enhance]'),auto=section.querySelector('[data-enhance-auto]'),mode=section.querySelector('[data-enhance-mode]'),status=section.querySelector('[data-enhance-status]');
  const session=crypto.randomUUID().replaceAll('-','');let busy=false,disposed=false,timer,reset=true;
  async function annotated(encoded,view){
    const image=new Image();image.src='data:image/png;base64,'+encoded;await image.decode();const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=576;const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0,1024,576);
    ctx.strokeStyle='#9ee34a';ctx.lineWidth=3;ctx.setLineDash([9,6]);ctx.beginPath();let connected=false;
    for(const point of view.path??[]){if(!point){connected=false;continue;}if(connected)ctx.lineTo(...point);else ctx.moveTo(...point);connected=true;}ctx.stroke();ctx.setLineDash([]);
    const names={person:'사람',car:'차량',truck:'트럭',bus:'버스',bicycle:'자전거',motorcycle:'이륜차'};
    for(const item of view.annotations??[]){const [x,y]=item.point,color=item.class==='person'?'#ffd369':'#56e2ed';ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,7,0,Math.PI*2);ctx.stroke();const label=ko?names[item.class]??item.class:item.class;ctx.font='600 17px Arial,sans-serif';const w=ctx.measureText(label).width+10;ctx.fillStyle='#09191be6';ctx.fillRect(Math.min(1024-w,x+9),Math.max(0,y-25),w,23);ctx.fillStyle=color;ctx.fillText(label,Math.min(1024-w,x+9)+5,Math.max(17,y-8));}
    return canvas.toDataURL('image/png');
  }
  async function run(){
    if(busy||disposed)return;busy=true;delete root.rgbEnhancementError;button.disabled=true;const born=performance.now();
    try{
      if(root.rgbViewerState().variant==='support')throw new Error(ko?'사진 형태의 복원 모델로 바꾼 뒤 실행하세요.':'Select a photographic reconstruction before enhancement.');
      status.textContent=ko?'현재 화면을 캡처하고 GPU에서 보정 중…':'Capturing the current view and enhancing on the GPU…';
      const capture=await root.rgbViewerCapture();
      const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session,mode:mode.value,reset,image:capture.image,view:capture.view})});
      if(!response.ok)throw new Error(ko?'GPU 연결을 확인하세요. 로컬 프록시와 보정 서버가 필요합니다.':'Check the GPU connection; the local proxy and enhancer must be running.');
      const result=await response.json();if(disposed)return;
      section.querySelector('[data-enhance-input]').src=await annotated(capture.image,capture.view);section.querySelector('[data-enhance-output]').src=await annotated(result.image,capture.view);section.querySelector('.rgb-enhancement-pair').hidden=false;reset=false;
      status.textContent=`${ko?'캡처':'Capture'} ${capture.view.time_seconds.toFixed(1)}s · ${capture.view.preset} · ${ko?'이전 출력':'Prior outputs'} ${result.history_frames}/4 · GPU ${result.model_ms.toFixed(0)}ms · ${ko?'전체 응답':'Round trip'} ${(performance.now()-born).toFixed(0)}ms${result.reset_reasons?.length?(ko?' · 시점 변경으로 이력 초기화':' · history reset for view change'):''}`;
      root.rgbEnhancementState={...result,round_trip_ms:performance.now()-born,image:undefined,input_view:capture.view};
    }catch(error){auto.checked=false;status.textContent=error.message;root.rgbEnhancementError=error.message;}
    finally{busy=false;button.disabled=false;if(auto.checked&&!disposed)timer=setTimeout(run,100);}
  }
  const restart=()=>{reset=true;status.textContent=ko?'다음 요청에서 이전 출력 이력을 비웁니다.':'The next request starts with empty history.';};
  const toggle=()=>{clearTimeout(timer);if(auto.checked)run();};button.addEventListener('click',run);auto.addEventListener('change',toggle);mode.addEventListener('change',restart);section.querySelector('[data-enhance-reset]').addEventListener('click',restart);
  return ()=>{disposed=true;clearTimeout(timer);button.removeEventListener('click',run);auto.removeEventListener('change',toggle);section.remove();root.classList.remove('rgb-has-enhancer');delete root.rgbEnhancementState;delete root.rgbEnhancementError;};
}
