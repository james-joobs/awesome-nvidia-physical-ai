// Display actual predicted poses in the same relative scene frame. No actuation.
import * as T from 'three';
export async function mountPolicy({root,scene,base,config,ko}){
  if(!config.policy_file)return {setFrame(){},state:()=>null,dispose(){}};
  const response=await fetch(base+config.policy_file);if(!response.ok)throw new Error('Missing policy predictions');const data=await response.json();
  const row=document.createElement('div');row.className='rgb-policy-tools';const button=document.createElement('button');button.type='button';button.dataset.rgbPolicy='';button.setAttribute('aria-pressed','true');button.textContent=ko?'Alpamayo 경로 켜짐':'Alpamayo path on';const label=document.createElement('span');label.dataset.rgbPolicyStatus='';row.append(button,label);root.querySelector('.rgb-toolbar').after(row);
  const material=new T.LineDashedMaterial({color:0x9ee34a,dashSize:.33,gapSize:.12,transparent:true,opacity:.95,depthTest:false,depthWrite:false});let geometry=new T.BufferGeometry(),line=new T.Line(geometry,material);scene.add(line);let enabled=true,active=null,index=config.default_frame;
  function setFrame(i){index=i;const t=config.frames[i].time_seconds;active=data.keyframes.filter(k=>k.t0_seconds<=t+1e-5).at(-1)??null;
    line.visible=enabled&&Boolean(active);geometry.dispose();const points=active?active.world_xyz_relative_units.map(p=>new T.Vector3(p[0],p[1],p[2]+.04)):[];geometry=new T.BufferGeometry().setFromPoints(points);line.geometry=geometry;line.computeLineDistances();label.textContent=active?(ko?`${active.t0_seconds.toFixed(1)}초 입력 → 미래 자세 64개 · 높이 ${active.assumed_camera_height_m}m 가정 · 예측만 표시`:`Input ${active.t0_seconds.toFixed(1)} s → 64 predicted poses · ${active.assumed_camera_height_m} m height assumption · no control`):(ko?'첫 예측은 2.1초부터 표시합니다.':'Predictions start at 2.1 s.');root.dataset.rgbPolicyReady='true';
  }
  const toggle=()=>{enabled=!enabled;line.visible=enabled&&Boolean(active);button.setAttribute('aria-pressed',String(enabled));button.textContent=enabled?(ko?'Alpamayo 경로 켜짐':'Alpamayo path on'):(ko?'Alpamayo 경로 꺼짐':'Alpamayo path off');};button.addEventListener('click',toggle);setFrame(index);
  return {setFrame,state:()=>({enabled,frame:index,t0_seconds:active?.t0_seconds??null,poses:active?.world_xyz_relative_units.length??0}),dispose(){button.removeEventListener('click',toggle);row.remove();scene.remove(line);geometry.dispose();material.dispose();}};
}
