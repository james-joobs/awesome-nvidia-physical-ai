// Real detector output on source RGB + approximate contacts in the reconstructed world.
// This overlay is diagnostic; it does not supply vehicle controls or metric depth.
import * as T from 'three';
const COLORS={person:'#ffd369',car:'#56e2ed',truck:'#56e2ed',bus:'#56e2ed',bicycle:'#ba9cff',motorcycle:'#ba9cff'};
const NAMES={person:'사람',car:'차량',truck:'트럭',bus:'버스',bicycle:'자전거',motorcycle:'이륜차'};
const CAMERA_NAMES={front_camera:['Front','정면'],front_left_camera:['Front left','왼쪽 앞'],front_right_camera:['Front right','오른쪽 앞'],left_camera:['Left','왼쪽'],right_camera:['Right','오른쪽'],back_camera:['Rear','후면']};

export async function mountPerception({root,stage,scene,base,ko,config}) {
  if(!config.perception_file)return {setFrame(){},state:()=>null,dispose(){}};
  const response=await fetch(base+config.perception_file);if(!response.ok)throw new Error('Missing RGB perception outputs');const data=await response.json();
  const visuals=document.createElement('div');visuals.className='rgb-visuals';stage.before(visuals);visuals.append(stage);
  const panel=document.createElement('aside');panel.className='rgb-perception';panel.setAttribute('aria-label',ko?'실제 RGB 객체 인식 결과':'Actual RGB object detections');
  const heading=document.createElement('div');heading.className='rgb-perception-heading';const title=document.createElement('strong');title.textContent=ko?'카메라 인식':'Camera perception';
  const select=document.createElement('select');select.dataset.rgbCamera='';select.setAttribute('aria-label',ko?'인식 결과 카메라':'Detection camera');
  for(const name of data.camera_names){const o=document.createElement('option');o.value=name;o.textContent=(CAMERA_NAMES[name]??[name,name])[ko?1:0];select.append(o);}select.value=data.default_camera;
  heading.append(title,select);const canvas=document.createElement('canvas');canvas.dataset.rgbDetections='';canvas.setAttribute('aria-label',ko?'원본 RGB 위의 예측 마스크와 검출 박스':'Predicted masks and bounding boxes on original RGB');
  const count=document.createElement('p');count.className='rgb-perception-count';count.dataset.rgbCounts='';const note=document.createElement('small');note.textContent=ko?'실제 RGB · 예측 마스크·박스':'Actual RGB · predicted masks and boxes';
  panel.append(heading,canvas,count,note);visuals.append(panel);
  const toolbar=document.createElement('div');toolbar.className='rgb-perception-tools';const toggle=document.createElement('button');toggle.type='button';toggle.dataset.rgbRecognition='';toggle.setAttribute('aria-pressed','true');toggle.textContent=ko?'인식 표시 켜짐':'Recognition on';
  const explanation=document.createElement('span');explanation.textContent=ko?'3D 표시는 RGB 도로면 기반 위치 추정 · 상대 단위':'3D markers: RGB road-plane estimates · relative units';toolbar.append(toggle,explanation);visuals.after(toolbar);
  const layer=new T.Group();scene.add(layer);let index=config.default_frame,enabled=true,serial=0,disposed=false,shown=0,viewCount=0;const sprites=[],meshes=[];const cached=new Map();
  const ringGeometry=new T.RingGeometry(.17,.22,32),poleGeometry=new T.BufferGeometry().setFromPoints([new T.Vector3(0,0,.03),new T.Vector3(0,0,.7)]);
  const getImage=path=>{if(!cached.has(path)){cached.set(path,new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(new Error('Missing RGB preview'));image.src=base+path;}));}return cached.get(path);};
  function clear(){while(layer.children.length)layer.remove(layer.children[0]);for(const s of sprites){s.material.map.dispose();s.material.dispose();}sprites.length=0;for(const m of meshes)m.dispose();meshes.length=0;}
  function tag(text,color){const c=document.createElement('canvas');c.width=224;c.height=46;const ctx=c.getContext('2d');ctx.fillStyle='#09191be6';ctx.beginPath();ctx.roundRect(0,0,224,46,8);ctx.fill();ctx.font='600 23px Arial,"Noto Sans KR",sans-serif';ctx.fillStyle=color;ctx.textAlign='center';ctx.fillText(text,112,31);const texture=new T.CanvasTexture(c);texture.colorSpace=T.SRGBColorSpace;const sprite=new T.Sprite(new T.SpriteMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false,sizeAttenuation:false}));sprite.scale.set(.22,.06,1);sprites.push(sprite);return sprite;}
  function drawMarkers(frame){clear();const ego=config.frames[index].ground_position;const objects=frame.objects.map(o=>({...o,distance:Math.hypot(o.ground_position[0]-ego[0],o.ground_position[1]-ego[1])})).filter(o=>o.distance<22).sort((a,b)=>a.distance-b.distance).slice(0,24);shown=objects.length;
    objects.forEach((o,i)=>{const color=COLORS[o.class]??'#56e2ed',group=new T.Group();group.position.set(...o.ground_position);const ringMaterial=new T.MeshBasicMaterial({color,transparent:true,opacity:.9,side:T.DoubleSide,depthTest:false,depthWrite:false});meshes.push(ringMaterial);const ring=new T.Mesh(ringGeometry,ringMaterial);ring.position.z=.025;group.add(ring);const lineMaterial=new T.LineBasicMaterial({color,transparent:true,opacity:.8,depthTest:false,depthWrite:false});meshes.push(lineMaterial);group.add(new T.Line(poleGeometry,lineMaterial));if(o.cameras.includes(select.value)&&(i<12||o.class==='person')){const label=tag(`${ko?NAMES[o.class]:o.class.toUpperCase()}`,color);label.position.z=.85;group.add(label);}layer.add(group);});layer.visible=enabled;
  }
  function maskCanvas(mask,color){const c=document.createElement('canvas');[c.width,c.height]=mask.size;const ctx=c.getContext('2d'),im=ctx.createImageData(c.width,c.height);const rgb=new T.Color(color);let pos=0;mask.counts.forEach((n,i)=>{for(let j=0;j<n;j++,pos++){if(i%2){const k=pos*4;im.data[k]=Math.round(rgb.r*255);im.data[k+1]=Math.round(rgb.g*255);im.data[k+2]=Math.round(rgb.b*255);im.data[k+3]=102;}}});ctx.putImageData(im,0,0);return c;}
  async function drawRgb(frame){const key=select.value,view=frame.views[key];if(!view)return;const ticket=++serial;viewCount=view.detections.length;const tally={};for(const d of view.detections)tally[d.class]=(tally[d.class]??0)+1;count.textContent=Object.entries(tally).map(([name,n])=>`${ko?NAMES[name]:name} ${n}`).join(' · ')||(ko?'이 프레임에서 기준 이상 검출 없음':'No detections above threshold in this frame');
    const image=await getImage(view.image);if(disposed||ticket!==serial)return;const [w,h]=view.image_size;canvas.width=640;canvas.height=Math.round(640*h/w);const ctx=canvas.getContext('2d');ctx.scale(640/w,640/w);ctx.drawImage(image,0,0,w,h);
    if(enabled){
      for(const d of view.detections){const color=COLORS[d.class]??'#56e2ed';ctx.drawImage(maskCanvas(d.mask,color),...d.mask.origin,...d.mask.extent);const [x0,y0,x1,y1]=d.bbox;ctx.strokeStyle=color;ctx.lineWidth=2.7;ctx.strokeRect(x0,y0,x1-x0,y1-y0);}
      const people=view.detections.filter(d=>d.class==='person'),vehicles=view.detections.filter(d=>d.class!=='person').sort((a,b)=>(b.bbox[2]-b.bbox[0])*(b.bbox[3]-b.bbox[1])-(a.bbox[2]-a.bbox[0])*(a.bbox[3]-a.bbox[1])).slice(0,3),placed=[];
      for(const d of [...people,...vehicles]){const color=COLORS[d.class]??'#56e2ed',[x0,y0,x1]=d.bbox;const text=`${ko?NAMES[d.class]:d.class} ${(d.score*100).toFixed(1)}%`;ctx.font='600 27px Arial,"Noto Sans KR",sans-serif';const tw=ctx.measureText(text).width+12;let x=Math.max(0,Math.min(w-tw,x0)),y=Math.max(31,y0);
        for(let tries=0;tries<12&&placed.some(p=>x<p.x+p.w+5&&x+tw>p.x-5&&y-31<p.y+5&&y>p.y-31-5);tries++){y-=36;if(y<32){y=Math.max(31,y0);x=Math.min(w-tw,x+tw+6);}}
        placed.push({x,y,w:tw});ctx.strokeStyle=color;ctx.lineWidth=1.4;ctx.beginPath();ctx.moveTo(x+tw/2,y);ctx.lineTo((x0+x1)/2,y0);ctx.stroke();ctx.fillStyle='#081819ec';ctx.fillRect(x,y-31,tw,33);ctx.fillStyle=color;ctx.fillText(text,x+6,y-7);
      }
    }
    root.dataset.rgbPerceptionFrame=String(index);root.dataset.rgbPerceptionReady='true';
  }
  const onCamera=()=>{drawMarkers(data.frames[index]);drawRgb(data.frames[index]).catch(e=>{count.textContent=ko?'RGB 프레임을 불러오지 못했습니다.':'Could not load the RGB frame.';console.error(e);});};select.addEventListener('change',onCamera);
  const onToggle=()=>{enabled=!enabled;layer.visible=enabled;toggle.setAttribute('aria-pressed',String(enabled));toggle.textContent=enabled?(ko?'인식 표시 켜짐':'Recognition on'):(ko?'인식 표시 꺼짐':'Recognition off');onCamera();};toggle.addEventListener('click',onToggle);
  async function setFrame(i){index=i;const frame=data.frames[i];drawMarkers(frame);await drawRgb(frame);}
  await setFrame(index);
  return {setFrame:i=>{setFrame(i).catch(console.error);},state:()=>({enabled,frame:index,camera:select.value,detections_in_camera:viewCount,markers:shown,people_in_camera:data.frames[index].views[select.value]?.detections.filter(d=>d.class==='person').length??0}),dispose(){disposed=true;serial++;select.removeEventListener('change',onCamera);toggle.removeEventListener('click',onToggle);clear();scene.remove(layer);ringGeometry.dispose();poleGeometry.dispose();cached.clear();toolbar.remove();panel.remove();}};
}
