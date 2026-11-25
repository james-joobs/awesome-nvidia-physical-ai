// Record real browser pointer/slider interactions; no offline render FPS claim.
// Install Playwright, or set PLAYWRIGHT_MODULE to its importable module path.
import fs from 'node:fs/promises';
import path from 'node:path';
const args=process.argv.slice(2),arg=(name,fallback)=>{const i=args.indexOf(name);return i<0?fallback:args[i+1];};
const url=arg('--url'),out=arg('--out');if(!url||!out)throw new Error('--url and fresh --out required');
await fs.mkdir(out,{recursive:false});
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE??'playwright');
const browser=await chromium.launch({channel:'chrome',headless:true,args:process.platform==='darwin'?['--use-angle=metal']:[]});
const context=await browser.newContext({viewport:{width:1440,height:1080},deviceScaleFactor:1,recordVideo:{dir:out,size:{width:1440,height:1080}}});
const page=await context.newPage(),errors=[],trace=[];
page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${new URL(r.url()).pathname}`);});
await page.goto(url);const root=page.locator('[data-joint-viewer]');await root.locator('[data-joint-load]').click();
await page.waitForFunction(()=>document.querySelector('[data-joint-viewer]')?.dataset.jointReady==='true',{},{timeout:90000});
const select=root.locator('[data-joint-model]');
for(const id of ['nurec','aether','da3','surround','calibrated']){
  await select.selectOption(id);await page.waitForFunction(id=>document.querySelector('[data-joint-viewer]')?.dataset.jointModel===id,id,{timeout:60000});
}
await root.locator('[data-joint-preset="chase"]').click();
await page.evaluate(()=>{const r=document.querySelector('[data-joint-viewer]').getBoundingClientRect();window.scrollTo(0,window.scrollY+r.top-95);});
await page.waitForTimeout(1000);
const started=Date.now();
const note=async label=>trace.push({seconds:(Date.now()-started)/1000,label,...await root.evaluate(e=>e.jointViewerState())});
for(const id of ['nurec','aether','da3','surround','calibrated']){
  await select.selectOption(id);await page.waitForFunction(id=>document.querySelector('[data-joint-viewer]')?.dataset.jointModel===id,id);await page.waitForTimeout(1600);await note(id);
  await root.locator('[data-joint-stage]').screenshot({path:path.join(out,`${id}-chase.png`)});
}
const canvas=root.locator('[data-joint-stage] canvas').first(),box=await canvas.boundingBox();
await page.mouse.move(box.x+box.width*.53,box.y+box.height*.52);await page.mouse.down();
for(let i=1;i<=40;i++){await page.mouse.move(box.x+box.width*.53+i*5,box.y+box.height*.52+Math.sin(i/15)*24);await page.waitForTimeout(45);}
await page.mouse.up();await page.waitForTimeout(700);await note('actual-pointer-orbit');
await root.locator('[data-joint-preset="input"]').click();await root.locator('[data-joint-camera]').selectOption('0');await page.waitForTimeout(1300);await note('rear-camera');
await root.locator('[data-joint-camera]').selectOption('1');await root.locator('[data-joint-preset="chase"]').click();
await root.locator('[data-joint-play]').click();await page.waitForTimeout(5800);await root.locator('[data-joint-play]').click();await note('time-playback');
const slider=root.locator('[data-joint-frame]');await slider.focus();await page.keyboard.press('Home');for(let i=0;i<8;i++)await page.keyboard.press('ArrowRight');await page.waitForTimeout(500);
const image=await root.locator('[data-joint-rgb]').boundingBox();await page.mouse.click(image.x+image.width*.5,image.y+image.height*.83);await page.waitForTimeout(1600);await note('pixel-depth-world-correspondence');
const ended=Date.now();await root.screenshot({path:path.join(out,'viewer.png')});
const video=page.video();await context.close();const raw=await video.path();await browser.close();
await fs.writeFile(path.join(out,'interaction.json'),JSON.stringify({schema:1,mode:'actual browser pointer, keyboard and native inline recording',no_playback_speedup:true,recording_start_wall_ms:started,recording_end_wall_ms:ended,clip_duration_seconds:(ended-started)/1000,video_file:path.basename(raw),trace,errors},null,2)+'\n');
console.log(JSON.stringify({out,seconds:(ended-started)/1000,errors}));
