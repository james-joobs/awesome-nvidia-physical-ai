// Record the real optional local GPU preview, including actual mouse changes.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const args=Object.fromEntries(process.argv.slice(2).reduce((r,s,i,a)=>{if(s.startsWith('--'))r.push([s.slice(2),a[i+1]]);return r;},[]));
const lang=args.language??'en',out=path.resolve(args.output??'temporal-recording');fs.mkdirSync(out,{recursive:true});
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE?pathToFileURL(process.env.PLAYWRIGHT_MODULE).href:'playwright');
const browser=await chromium.launch({channel:'chrome',headless:true,args:process.platform==='darwin'?['--use-angle=metal']:[]});
const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:out,size:{width:1440,height:1000}}});
const page=await context.newPage(),video=page.video(),born=Date.now(),errors=[],events=[];page.on('pageerror',e=>errors.push(String(e)));
try{
 await page.goto(args.url??`http://127.0.0.1:8092/?lang=${lang}`);await page.locator('[data-rgb-load]').click();await page.waitForFunction(()=>document.querySelector('[data-rgb-viewer]').dataset.rgbReady==='true',null,{timeout:120000});await page.waitForTimeout(1600);
 if(!await page.locator('[data-enhance]').count())throw Error('Start the viewer with its explicit --enhancer-url option');
 const trim=(Date.now()-born)/1000;
 async function capture(action){const last=await page.evaluate(()=>document.querySelector('[data-rgb-viewer]').rgbEnhancementState?.sequence??0);await page.locator('[data-enhance]').click();await page.waitForFunction(n=>{const r=document.querySelector('[data-rgb-viewer]');return r.rgbEnhancementState?.sequence>n||r.rgbEnhancementError;},last,{timeout:90000});const result=await page.evaluate(()=>{const r=document.querySelector('[data-rgb-viewer]');if(r.rgbEnhancementError)throw Error(r.rgbEnhancementError);return r.rgbEnhancementState;});events.push({action,video_time:(Date.now()-born)/1000-trim,...result});return result;}
 await capture('initial');await page.waitForTimeout(1600);
 for(let i=0;i<5;i++)await capture('build_actual_history');
 if(events.at(-1).history_frames!==4)throw Error('Actual four-output context did not initialize');
 await page.screenshot({path:path.join(out,`live.${lang}.jpg`),type:'jpeg',quality:90});
 const box=await page.locator('[data-rgb-stage] > canvas').boundingBox();
 for(let i=0;i<6;i++){const x=box.x+box.width*.5,y=box.y+box.height*.48;await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+box.width*.004,y,{steps:8});await page.mouse.up();await page.waitForTimeout(160);await capture('small_mouse_orbit');}
 if(!events.some(e=>e.action==='small_mouse_orbit'&&e.history_frames===4))throw Error('Small camera changes never retained temporal context');
 await page.locator('[data-rgb-preset=driver]').click();const changed=await capture('driver_view_resets_history');if(!changed.history_reset)throw Error('Preset jump retained stale context');await page.waitForTimeout(2200);
 await page.locator('[data-enhance-mode]').selectOption('independent');await capture('independent_mode');await page.waitForTimeout(1600);
 await page.locator('[data-rgb-preset=chase]').click();await page.locator('[data-enhance-mode]').selectOption('temporal');for(let i=0;i<5;i++)await capture('chase_temporal');await page.waitForTimeout(1600);
 const finish=(Date.now()-born)/1000;await page.setViewportSize({width:390,height:844});await page.waitForTimeout(400);const mobile=await page.evaluate(()=>({viewport:innerWidth,width:document.documentElement.scrollWidth}));await page.screenshot({path:path.join(out,`mobile.${lang}.png`),fullPage:true});if(mobile.width>mobile.viewport||errors.length)throw Error(JSON.stringify({mobile,errors}));
 await context.close();fs.renameSync(await video.path(),path.join(out,`raw.${lang}.webm`));fs.writeFileSync(path.join(out,`recording.${lang}.json`),JSON.stringify({language:lang,viewport:[1440,1000],trim_start_seconds:trim,content_seconds:finish-trim,events,mobile,errors,method:'Actual local browser and actual GPU outputs. No simulated inference or pre-rendered camera substitution.'},null,2));console.log('PASS',lang,(finish-trim).toFixed(1),'seconds',events.length,'actual responses');
}finally{await browser.close();}
