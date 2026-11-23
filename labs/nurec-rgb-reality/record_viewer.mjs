// Record actual RGB detections, segmentation and 3D marker interactions.
// Optional dependency: Playwright 1.60.0. No pre-rendered camera sweep is used.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const args=Object.fromEntries(process.argv.slice(2).reduce((pairs,s,i,all)=>{if(s.startsWith('--'))pairs.push([s.slice(2),all[i+1]]);return pairs;},[]));
const locale=args.language??'en',url=args.url??`http://127.0.0.1:8092/?lang=${locale}`,out=path.resolve(args.output??'nurec-viewer-recording');fs.mkdirSync(out,{recursive:true});
const modulePath=process.env.PLAYWRIGHT_MODULE;const {chromium}=await import(modulePath?(path.isAbsolute(modulePath)?pathToFileURL(modulePath).href:modulePath):'playwright');
const browser=await chromium.launch({headless:true,channel:'chrome',args:process.platform==='darwin'?['--use-angle=metal']:[]});
const context=await browser.newContext({viewport:{width:1280,height:720},deviceScaleFactor:1,recordVideo:{dir:out,size:{width:1280,height:720}}});const page=await context.newPage(),born=Date.now(),video=page.video(),events=[],errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
try{
 await page.goto(url);await page.locator('[data-rgb-load]').click();await page.waitForSelector('[data-rgb-ready=true]',{timeout:120000});await page.waitForTimeout(1000);const trimStart=(Date.now()-born)/1000;
 const root=page.locator('[data-rgb-viewer]'),stage=page.locator('[data-rgb-stage]'),box=await stage.boundingBox();
 const snapshot=async action=>events.push({action,time_seconds:(Date.now()-born)/1000-trimStart,...await root.evaluate(r=>r.rgbViewerState())});
 const drag=async(dx,dy,button='left')=>{const x=box.x+box.width*.43,y=box.y+box.height*.57;await page.mouse.move(x,y);await page.mouse.down({button});for(let i=1;i<=50;i++){await page.mouse.move(x+dx*i/50,y+dy*i/50);await page.waitForTimeout(32);}await page.mouse.up({button});await page.waitForTimeout(400);};
 const initial=await root.evaluate(r=>r.rgbViewerState());if(initial.gaussians!==450000||initial.policy?.poses!==64)throw new Error('Expected the actual NuRec model and Alpamayo prediction');if(!initial.perception||initial.perception.people_in_camera<1)throw new Error('Expected actual pedestrian detections in the selected RGB camera');
 await snapshot('initial');await page.screenshot({path:path.join(out,`nurec-rgb-reality.${locale}.jpg`),type:'jpeg',quality:90});await page.waitForTimeout(2200);
 await page.locator('[data-rgb-recognition]').click();await page.waitForTimeout(1600);await snapshot('recognition_off');
 await page.locator('[data-rgb-recognition]').click();await page.waitForTimeout(1800);await snapshot('recognition_on');
 await page.locator('[data-rgb-policy]').click();await page.waitForTimeout(1200);await snapshot('policy_off');await page.locator('[data-rgb-policy]').click();await page.waitForTimeout(1200);await snapshot('policy_on');
 await page.locator('[data-rgb-camera]').selectOption('front_camera');await page.waitForTimeout(1700);await snapshot('front_camera');
 await page.locator('[data-rgb-camera]').selectOption('left_camera');await page.waitForTimeout(1700);await snapshot('left_camera');
 await drag(-box.height*.45,0);await snapshot('orbit');await page.waitForTimeout(1300);
 await page.locator('[data-rgb-preset=overhead]').click();await page.waitForTimeout(2200);await snapshot('overhead');
 await page.locator('[data-rgb-preset=driver]').click();await page.locator('[data-rgb-camera]').selectOption('front_camera');await page.waitForTimeout(2400);await snapshot('driver');
 await page.locator('[data-rgb-preset=chase]').click();await page.locator('[data-rgb-camera]').selectOption('left_camera');await page.locator('[data-rgb-play]').click();await page.waitForTimeout(4300);await page.locator('[data-rgb-play]').click();await snapshot('perception_replay');await page.waitForTimeout(1800);
 if(events[0].camera.every((v,i)=>Math.abs(v-events.find(e=>e.action==='orbit').camera[i])<.01))throw new Error('Drag did not change camera pose');
 if(events.at(-1).frame===events[0].frame)throw new Error('Path playback did not change the estimated frame');
 if(events.find(e=>e.action==='recognition_off').perception.enabled||!events.find(e=>e.action==='recognition_on').perception.enabled)throw new Error('Recognition toggle failed');
 if(errors.length)throw new Error('Viewer errors: '+errors.join('; '));
 const duration=(Date.now()-born)/1000-trimStart;await context.close();const file=await video.path();const raw=path.join(out,`raw-nurec.${locale}.webm`);fs.renameSync(file,raw);
 fs.writeFileSync(path.join(out,`interaction.${locale}.json`),JSON.stringify({language:locale,recording:'Actual browser viewport, driven by Playwright mouse/scroll/buttons',trim_start_seconds:trimStart,content_seconds:duration,viewport:[1280,720],events,errors,raw_file:path.basename(raw)},null,2));console.log('RECORDED',locale,duration.toFixed(2),'seconds,',events.length,'interaction checks');
}finally{await browser.close();}
