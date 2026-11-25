#!/usr/bin/env python3
"""Reproducible local human-Gaussian stages; never download source videos.

GPU stages require explicitly configured external runtimes. A missing runtime
is an error, not a simulated successful run. Output and model caches are private
by default. See README.md and SOURCES.md before configuring assets.
"""
from __future__ import annotations
import argparse,contextlib,fcntl,gzip,hashlib,http.server,json,math,os,shutil,struct,subprocess,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
PINS={'gem':'4aef1452e5df171deff4f293c08e643eb450981e','four_d_anyone':'1b5c707cfe7c7fda19d08f37a10e1c444c3299ef','moge':'74fbce054ebed49800de42d0ad0e83495065719a','soma':'01ab5b5c0876058bd27d34b1607d74b2e55e0cf4'}
REPOS={'gem':'https://github.com/NVlabs/GEM-X.git','four_d_anyone':'https://github.com/ant-research/4DAnyone.git','moge':'https://github.com/microsoft/MoGe.git','soma':'https://github.com/NVlabs/SOMA-X.git'}
STAGES=('setup','prepare','rig','multiview','train','refine','extend','render','package','check','serve')
FRESH_STAGES={'views-base','seed20k','clean-seed','views-offset','hires','original-roi','roi','moge-infer','moge-align','geometry','clean-final'}

class PrerequisiteError(RuntimeError):pass

def write(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temp.replace(path)
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(8<<20),b''):h.update(block)
 return h.hexdigest()
def safe(base,relative):
 if not isinstance(relative,str) or '://' in relative:raise ValueError('Package file paths must be relative')
 target=(base/relative).resolve()
 if not target.is_relative_to(base.resolve()):raise ValueError('Package path escapes its root')
 return target

def template(root):
 return {'schema':1,'ffmpeg':shutil.which('ffmpeg') or 'ffmpeg','cuda_home':'/usr/local/cuda-12.9','cuda_arch':'12.0','gpu_lock':str(root/'.gpu.lock'),'python':{name:str(root/f'envs/{name}/bin/python') for name in ['gem','reconstruction','moge','control_export','control_render']},'sources':{name:str(root/'deps'/name) for name in PINS},'sam2_source':str(root/'deps/sam2'),'assets':{'soma':str(root/'assets/soma'),'sam2_checkpoint':str(root/'models/sam2.1_hiera_large.pt'),'gem_config':str(root/'gem-motion.yaml')},'models':str(root/'models'),'interval_steps':6000,'seed_train_steps':20000,'hires_steps':6000,'roi_steps':3000,'geometry_steps':1500}

class Runner:
 def __init__(self,args):
  self.args=args;self.root=args.root.expanduser().resolve();self.root.mkdir(parents=True,exist_ok=True);self.config_path=(args.config or self.root/'runtime.json').expanduser().resolve();self.config=json.loads(self.config_path.read_text()) if self.config_path.exists() else template(self.root);self.work=self.root/'multiview-prior';self.ref=self.work/'refinement';self.package=args.package_dir.expanduser().resolve() if args.package_dir else self.root/'package'
  public=HERE.parents[1]/'site/public'
  if self.root.is_relative_to(public):raise PrerequisiteError('Runtime/output root must stay outside site/public; reconstruction inputs and models are private by default.')
  if args.mode=='reconstruction' and args.stage=='package' and self.package.is_relative_to(public):raise PrerequisiteError('Monocular package creates private local outputs; choose a destination outside site/public.')
 def path(self,group,key=None):
  value=self.config[group][key] if key else self.config[group];p=Path(value).expanduser();return p if p.is_absolute() else self.root/p
 def python(self,name):
  p=self.path('python',name)
  if not p.is_file():raise PrerequisiteError(f'Missing {name} Python: configure python.{name} in {self.config_path}. See {HERE/"README.md"} for isolated installation commands.')
  return str(p)
 def ffmpeg(self):
  value=self.config.get('ffmpeg','ffmpeg');found=shutil.which(value)
  if not found and Path(value).is_file():found=value
  if not found:raise PrerequisiteError('FFmpeg was not found. Install FFmpeg and set runtime.json ffmpeg to its executable.')
  return str(Path(found).resolve())
 def env(self):
  env=os.environ.copy();cuda=self.config.get('cuda_home')
  if cuda:env['CUDA_HOME']=cuda;env['PATH']=str(Path(cuda)/'bin')+os.pathsep+env.get('PATH','')
  env['TORCH_CUDA_ARCH_LIST']=self.config.get('cuda_arch','12.0');env['MAX_JOBS']='2';env['PYTHONPATH']=os.pathsep.join([*(str(Path(x).expanduser()) for x in self.config.get('extra_python_paths',[])),*(str(self.path('sources',key)) for key in PINS),str(self.path('sam2_source')),env.get('PYTHONPATH','')]);return env
 def run(self,argv,**kwargs):
  command=[str(x) for x in argv];print(json.dumps({'command':command}),flush=True);subprocess.run(command,check=True,env=self.env(),**kwargs)
 def script(self,python,name,*args):self.run([self.python(python),HERE/name,*args])
 def render_dir(self):
  # A full-length extension must not replace a previously rendered short lab.
  models=self.root/'models.json'
  return self.root/'renders'/hashlib.sha256(models.read_bytes()+(HERE/'render_sequence.py').read_bytes()).hexdigest()[:16] if models.is_file() else self.root/'renders'
 def verify_models(self):
  self.need(self.root/'models.json');models=json.loads((self.root/'models.json').read_text())
  for item in models['segments']:
   path=safe(self.root,item['model']);self.need(path)
   if item.get('sha256') and sha(path)!=item['sha256']:raise PrerequisiteError('A selected checkpoint changed. Preserve the run and inspect its model inventory.')
  return models
 def journal_path(self):
  key=f'{self.args.mode}-{self.args.stage}'
  if self.args.mode=='reconstruction' and self.args.stage in ['render','package'] and (self.root/'models.json').is_file():key+='-'+sha(self.root/'models.json')[:16]
  if self.args.mode=='reconstruction' and self.args.stage in ['render','package']:key+='-'+sha(HERE/'render_sequence.py')[:10]
  if self.args.stage=='package':key+='-'+hashlib.sha256(str(self.package).encode()).hexdigest()[:12]
  return self.root/'stages'/(key+'.json')
 def need(self,*files):
  missing=[str(p) for p in files if not Path(p).exists()]
  if missing:raise PrerequisiteError('Missing prerequisite outputs/assets:\n'+'\n'.join(missing)+'\nRun the preceding stage or configure the required official asset; see SOURCES.md.')
 def link(self,destination,source):
  destination=Path(destination);source=Path(source).resolve();self.need(source);destination.parent.mkdir(parents=True,exist_ok=True)
  if destination.exists() or destination.is_symlink():
   if destination.resolve()!=source:raise PrerequisiteError(f'Refusing to replace existing {destination}; use a fresh output folder or correct configuration.')
  else:destination.symlink_to(source,target_is_directory=source.is_dir())
 def workspace(self):
  self.work.mkdir(exist_ok=True);self.ref.mkdir(exist_ok=True)
  self.link(self.work/'4danyone',self.path('sources','four_d_anyone'));self.link(self.work/'models',self.path('models'));self.link(self.root/'soma-assets',self.path('assets','soma'));self.link(self.root/'checkpoints/sam2.1_hiera_large.pt',self.path('assets','sam2_checkpoint'));self.link(self.root/'bin/ffmpeg',Path(self.ffmpeg()));self.link(self.ref/'moge-source',self.path('sources','moge'));self.link(self.ref/'moge-model',self.path('models')/'moge-3')
 def setup(self):
  if not self.config_path.exists():
   write(self.config_path,self.config)
   raise PrerequisiteError(f'Wrote {self.config_path}; no runtimes have been installed. Edit its Python/source/asset paths, follow README.md, then rerun setup. --fetch-sources can fetch pinned source inside this output root.')
  if self.args.fetch_sources:
   for name,url in REPOS.items():
    dest=self.path('sources',name)
    if not dest.resolve().is_relative_to(self.root):raise PrerequisiteError('--fetch-sources writes only within the selected output root')
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():self.run(['git','clone',url,dest])
    revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
    if revision!=PINS[name]:self.run(['git','-C',dest,'checkout',PINS[name]])
  self.ffmpeg();names=['control_export','control_render'] if self.args.mode=='control' else ['gem','reconstruction','moge']
  for name in names:self.python(name)
  required=['soma'] if self.args.mode=='control' else list(PINS)
  for name in required:
   source=self.path('sources',name);self.need(source)
   revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
   if revision!=PINS[name]:raise PrerequisiteError(f'{name} source revision {revision} differs from tested pin {PINS[name]}; check out the pinned revision before running.')
  self.need(self.path('assets','soma'))
  if self.args.mode!='control':
   self.need(self.path('assets','gem_config'),self.path('assets','sam2_checkpoint'),self.path('models')/'4danyone/model.safetensors',self.path('models')/'4danyone/Wan2.2_VAE.pth',self.path('models')/'4danyone/prompt_context.safetensors',self.path('models')/'4danyone/Wan22_TI2V_5B_Turbo_lora_rank_64_fp16.safetensors',self.path('models')/'moge-3/model.pt',self.path('models')/'birefnet')
   self.workspace()
  modules={'gem':['torch','gem','soma','sam2'],'reconstruction':['torch','numpy','PIL','fdanyone','gsplat'],'moge':['torch','moge.model.v3'],'control_export':['torch','soma'],'control_render':['torch','gsplat','nvdiffrast.torch']}
  for name in names:self.run([self.python(name),'-c','import importlib; '+ '; '.join(f'importlib.import_module({x!r})' for x in modules[name])])
  write(self.root/'setup.json',{'configured':True,'mode':self.args.mode,'source_pins':{k:PINS[k] for k in required},'note':'Imports/paths checked without GPU inference; model loading and CUDA compilation occur in their real stages.'})
 def prepare(self):
  if self.args.mode=='control':
   motion=self.path('sources','soma')/'assets/example_animation.usd';self.need(motion,self.path('assets','soma'));digest=sha(motion)
   if digest!='c09372492aaacdca3ca7ec5d737263d8e6042b66fdd29318d91848427fa40695':raise PrerequisiteError('Official SOMA motion hash differs; resolve the pinned Git LFS asset, not an LFS pointer or private animation.')
   write(self.root/'control-input.json',{'official_motion_sha256':digest,'synthetic_control':True});return
  if not self.args.video:raise PrerequisiteError('prepare requires --video /path/to/a/local-video-you-can-use.mp4; source video downloaders are not included.')
  source=self.args.video.expanduser().resolve();self.need(source);digest=sha(source)
  if (self.root/'input.json').exists():
   old=json.loads((self.root/'input.json').read_text())
   if old['original_sha256']!=digest:raise PrerequisiteError('This output root belongs to another input. Use a fresh root to preserve existing results.')
   self.need(self.root/'input.mp4',self.root/'source.mp4')
   if len(list((self.root/'frames').glob('*.jpg')))!=old['frames']:raise PrerequisiteError('Prepared RGB cache is incomplete; preserve this run and prepare a fresh output root.')
   print(json.dumps({'prepare':'reusing verified prepared-frame inventory','frames':old['frames']}));return
  ff=self.ffmpeg();png=subprocess.check_output([ff,'-v','error','-i',str(source),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1']);width,height=struct.unpack('>II',png[16:24])
  if abs(width/height-9/16)>.003 or min(width,height)<256 or width%2 or height%2:raise PrerequisiteError('This tested preset supports portrait 9:16 video, even dimensions >=256px on each axis. Other framing needs a camera/crop adapter; it is not silently stretched.')
  original=self.root/'original.mp4';shutil.copy2(source,original)
  self.run([ff,'-v','error','-n','-i',original,'-vf','fps=30','-an','-c:v','libx264','-crf','10','-pix_fmt','yuv420p',self.root/'input.mp4'])
  self.run([ff,'-v','error','-n','-i',self.root/'input.mp4','-vf','scale=540:960','-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',self.root/'source.mp4'])
  frames=self.root/'frames';frames.mkdir();self.run([ff,'-v','error','-i',self.root/'input.mp4','-vf','scale=540:960','-q:v','2',frames/'%06d.jpg']);count=len(list(frames.glob('*.jpg')))
  if count<121:raise PrerequisiteError('At least 121 normalized frames (4.03s at 30Hz) are required by this preset.')
  write(self.root/'input.json',{'schema':1,'width':width,'height':height,'frames':count,'fps':30,'duration':count/30,'original_sha256':digest,'normalized_sha256':sha(self.root/'input.mp4'),'rgb_scope':'Original-resolution normalized-time video; 540x960 working RGB. Original file preserved separately.','source_is_local':True,'timing':'Shared normalized 30Hz input.mp4 drives RGB, GEM and ROI. Original file is separately preserved; no raw variable-FPS frame-index correspondence is claimed.'})
  write(self.root/'frame_times.json',{'fps':30,'frames':[{'frame':i,'time':i/30} for i in range(count)],'input':'input.mp4'})
 def rig(self):
  if self.args.mode=='control':
   self.script('control_export','control_sample.py','--stage','export','--soma-source',self.path('sources','soma'),'--assets-dir',self.path('assets','soma'),'--out',self.root/'control');return
  self.workspace();self.need(self.root/'input.json');motion=self.root/'motion.pt'
  if not motion.exists():self.run([self.python('gem'),'-m','gem.inference','motion-video','--task','body','--input',self.root/'input.mp4','--config',self.path('assets','gem_config'),'--device','cuda','--camera-mode','static','--postprocess','--soma-assets',self.path('assets','soma'),'--output',motion],cwd=self.path('sources','gem'))
  self.script('gem','rig_export.py','--root',self.root);self.script('gem','segment.py','--root',self.root)
 def multiview(self):
  self.real_stage();self.workspace();self.need(self.root/'rig/geometry.npz',self.root/'masks/000121.png')
  self.script('reconstruction','multiview.py','--root',self.root,'--name','pilot','--views','6')
  self.script('reconstruction','multiview.py','--root',self.root,'--name','offset','--views','6','--start-yaw','30','--turbo')
 def train(self):
  self.real_stage();self.workspace();self.need(self.work/'pilot/generation.json')
  steps=self.config['seed_train_steps'];self.script('reconstruction','seed_train.py','--root',self.root,'--name','pilot','--steps',steps,'--stop-after',steps)
  self.script('reconstruction','clean_model.py','--root',self.root,'--model',self.work/'pilot/reconstruction/checkpoints/latest.npz','--out',self.work/'seed-clean.npz')
 def real_stage(self):
  if self.args.mode=='control':raise PrerequisiteError('The known-geometry control does not perform video reconstruction or diffusion. Run rig → render → package → check; train/refine/extend/multiview are intentionally not claimed for this mode.')
 def geometry(self,data,model,suffix,cameras='0'):
  raw=self.ref/f'moge-raw-{suffix}';aligned=self.ref/f'moge-aligned-{suffix}'
  self.script('moge','moge_infer.py','--root',self.root,'--data',data,'--out',raw,'--cameras',cameras)
  self.script('reconstruction','align_geometry.py','--root',self.root,'--model',model,'--raw',raw,'--out',aligned);return aligned
 def refine(self):
  self.real_stage();self.workspace();self.need(self.work/'seed-clean.npz',self.work/'offset/generation.json')
  self.run([self.python('reconstruction'),'-c',f'import sys; sys.path.insert(0,{str(self.work/"4danyone")!r}); from fdanyone.download import ensure_perceptual_vgg19; print(ensure_perceptual_vgg19({str(self.work/"models")!r}))'])
  self.script('reconstruction','hires.py','--root',self.root,'--steps',self.config['hires_steps'],'--stop-after',self.config['hires_steps'])
  self.script('reconstruction','clean_model.py','--root',self.root,'--model',self.work/'twelve-view-hires/checkpoints/latest.npz','--out',self.work/'final-4d.npz')
  roi=self.ref/'roi';self.script('reconstruction','prepare_data.py','--root',self.root,'--kind','roi','--out',roi)
  roi_model=self.ref/'roi-original'/f'model-{self.config["roi_steps"]}.npz'
  self.script('reconstruction','train_refine.py','--root',self.root,'--name','roi-original','--roi','--steps',self.config['roi_steps'])
  data=self.work/'twelve-view-hires/data';prior=self.geometry(data,roi_model,'seed','0,2,3,4');out=self.ref/'moge3';steps=self.config['geometry_steps']
  self.script('reconstruction','train_refine.py','--root',self.root,'--name','moge3','--base',roi_model,'--roi','--steps',steps,'--geometry',prior)
  selected=out/f'model-{steps}.npz';meta=json.loads((self.root/'input.json').read_text());segments=[{'id':'s00','start_frame':0,'valid_frames':min(120,meta['frames']),'model':str(selected.relative_to(self.root))}]
  if self.args.trajectory_experiment and not self.args.seed_only and meta['frames']>121:
   for i,start in enumerate(range(120,meta['frames'],120),1):
    name=f's{i:02d}';target=self.ref/'intervals'/name;target.mkdir(parents=True,exist_ok=True);init=target/'warm.npz';self.script('reconstruction','warmstart.py','--geometry',self.root/'rig/geometry.npz','--model',selected,'--origin',self.work/'pilot/soma-conditioning.npz','--start',start,'--out',init,'--mode','trajectory')
    data=target/'data';self.script('reconstruction','prepare_data.py','--root',self.root,'--kind','observed','--start',start,'--out',data)
    crops=target/'roi';self.script('reconstruction','prepare_data.py','--root',self.root,'--kind','roi','--start',start,'--out',crops)
    prior=self.geometry(data,init,name);steps=self.config['interval_steps']
    self.script('reconstruction','fit_interval.py','--root',self.root,'--out',target,'--start',start,'--steps',steps,'--geometry',prior)
    segments.append({'id':name,'start_frame':start,'valid_frames':min(120,meta['frames']-start),'model':str((target/f'model-{steps}.npz').relative_to(self.root))})
  else:segments[0]['valid_frames']=121
  for item in segments:item['sha256']=sha(safe(self.root,item['model']))
  write(self.root/'models.json',{'schema':1,'fps':30,'input_frames':meta['frames'],'covered_frames':sum(s['valid_frames'] for s in segments),'segments':segments,'method':('Seed Base24 plus six Turbo offset views, original-resolution ROI and MoGe-3' if len(segments)==1 else 'Experimental canonical SOMA appearance transfer and observed-only interval fitting'),'full_method':('seed-only' if len(segments)==1 else 'appearance-trajectory-experiment'),'source':{'credit':self.config.get('source_credit','Source: local user-supplied RGB'),'attribution_url':self.config.get('source_reference_url')},'new_full_interval_multiview_diffusion':False,'input_source_is_private':True})
 def extend(self):
  self.real_stage();self.workspace();self.need(self.root/'models.json',self.root/'input.json',HERE/'fresh_interval.py')
  seed=self.verify_models();count=json.loads((self.root/'input.json').read_text())['frames']
  if seed.get('full_method')=='fresh-twelve-direction-intervals':
   # Recover a process interrupted after the atomic inventory update but before
   # the outer stage journal was marked complete. Never train these models again.
   self.verify_stage('extend');path=self.root/'extension-progress.json';progress=json.loads(path.read_text()) if path.exists() else {'schema':1};progress.update(complete=True,input_frames=count,fps=30,segments=seed['segments']);write(path,progress);print('FULL_EXTENSION_REUSED',count);return
  if count<=121:raise PrerequisiteError('This source is already covered by the short interval. No full-length extension is needed.')
  if len(seed['segments'])!=1 or seed['covered_frames']!=121:raise PrerequisiteError('extend consumes a completed refine --seed-only result. Preserve any existing full-motion experiment and use a separate output root for another recipe.')
  first={**seed['segments'][0],'valid_frames':120};first['sha256']=sha(safe(self.root,first['model']));segments=[first]
  progress={'schema':1,'method':'fresh-twelve-direction-intervals','input_frames':count,'fps':30,'complete':False,'segments':segments}
  # Keep models.json at the verified short result until every interval exists.
  write(self.root/'extension-progress.json',progress)
  for i,start in enumerate(range(120,count,120),1):
   name=f's{i:02d}'
   self.script('reconstruction','fresh_interval.py','--root',self.root,'--config',self.config_path,'--name',name,'--start',start,'--steps',self.config.get('full_base_steps',self.config['seed_train_steps']),'--hires-steps',self.config['hires_steps'],'--roi-steps',self.config['roi_steps'],'--geometry-steps',self.config['geometry_steps'])
   report_file=self.work/name/'selected.json';self.need(report_file);report=json.loads(report_file.read_text());model=safe(self.root,report['final_model']);self.need(model)
   expected=min(120,count-start)
   flags=report.get('actual_done_flags',{})
   if report['start_frame']!=start or report['valid_frames']!=expected or not FRESH_STAGES.issubset(flags) or not all(flags[k] is True for k in FRESH_STAGES):raise PrerequisiteError('The interval report does not establish complete matching time coverage.')
   digest=sha(model)
   if digest!=report['final_sha256']:raise PrerequisiteError('A selected interval checkpoint changed after verification.')
   segments.append({'id':name,'start_frame':start,'valid_frames':expected,'model':str(model.relative_to(self.root)),'sha256':digest,'report':str(report_file.relative_to(self.root))})
   progress['segments']=segments;write(self.root/'extension-progress.json',progress)
  covered=sum(x['valid_frames'] for x in segments)
  if covered!=count:raise PrerequisiteError('Full-motion coverage differs from the normalized source.')
  result={'schema':1,'fps':30,'input_frames':count,'covered_frames':covered,'segments':segments,'method':'Seed Base24 plus Turbo offset; later intervals use two fresh six-view Turbo passes, original ROI and MoGe-3 guidance','full_method':'fresh-twelve-direction-intervals','source':seed.get('source',{'credit':'Source: local user-supplied RGB'}),'new_full_interval_multiview_diffusion':True,'input_source_is_private':True}
  write(self.root/'models.json',result);progress['complete']=True;write(self.root/'extension-progress.json',progress)
 def render(self):
  if self.args.mode=='control':self.script('control_render','control_sample.py','--stage','render','--out',self.root/'control','--ffmpeg',self.ffmpeg());return
  self.verify_models();self.script('reconstruction','render_sequence.py','--root',self.root,'--out',self.render_dir(),'--ffmpeg',self.ffmpeg())
 def package_stage(self):
  if self.package.exists() and any(self.package.iterdir()):raise PrerequisiteError('Package destination is not empty; use --package-dir with a fresh folder to preserve previous exports.')
  self.package.mkdir(parents=True,exist_ok=True)
  if self.args.mode=='control':
   src=self.root/'control';self.need(src/'manifest.json',src/'source.mp4',src/'data/meta.json')
   control=json.loads((src/'data/meta.json').read_text())
   if control.get('representation')!='soma-skinned-gaussians' or control.get('source_motion_sha256')!='c09372492aaacdca3ca7ec5d737263d8e6042b66fdd29318d91848427fa40695':raise PrerequisiteError('Control publication requires the verified official SOMA synthetic export; private monocular packages cannot be relabeled.')
   for name in ['manifest.json','source.mp4','comparison.mp4','poster.jpg','data']:self.copy(src/name,self.package/name)
   self.copy(self.path('sources','soma')/'LICENSE',self.package/'SOMA-LICENSE.txt');(self.package/'NOTICE.txt').write_text('Synthetic control based on NVIDIA SOMA-X official example motion and native neutral geometry, Apache-2.0. Wrapper code: repository MIT. No private footage.\n');return
  models=self.verify_models();segments=[]
  for item in models['segments']:
   dest=self.package/'browser'/item['id'];self.script('reconstruction','export_model.py','--model',safe(self.root,item['model']),'--out',dest);segments.append({'id':item['id'],'start':item['start_frame']/30,'duration':item['valid_frames']/30,'root':f'browser/{item["id"]}/'})
  duration=models['covered_frames']/30;self.run([self.ffmpeg(),'-v','error','-n','-i',self.root/'input.mp4','-t',duration,'-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',self.package/'source.mp4'])
  for name in ['comparison.mp4','poster.jpg']:
   if (self.render_dir()/name).exists():self.copy(self.render_dir()/name,self.package/name)
  provenance='Observed source + RGB-estimated motion + generated appearance priors; unseen surfaces are inferred.'
  provenance+=(' Later intervals use fresh multiview generation and native Gaussian fitting.' if models.get('new_full_interval_multiview_diffusion') else ' Short seed fitting or explicitly selected appearance-trajectory experiment; see models.json.')
  camera={};render_record=self.render_dir()/'rendered.json'
  if render_record.is_file():
   framing=json.loads(render_record.read_text()).get('camera',{});input_meta=json.loads((self.root/'input.json').read_text())
   if all(k in framing for k in ['target','radius','fov']):camera={'target':framing['target'],'distance':framing['radius'],'fov':framing['fov'],'framing_aspect':.75,'source_width':input_meta['width'],'source_height':input_meta['height']}
  write(self.package/'manifest.json',{'schema':1,'title':'Local monocular human reconstruction','fps':30,'duration':duration,'representation':'native-conditional-4d','source':{'url':'source.mp4','title':'Local source RGB','credit':models.get('source',{}).get('credit','Source: local user-supplied RGB'),'attribution_url':models.get('source',{}).get('attribution_url'),'rights':'Input-footage reuse permissions are separate from tool/model licenses'},'segments':segments,'provenance':provenance,'camera':camera,'private_local_output':True,'comparison':'comparison.mp4' if (self.package/'comparison.mp4').exists() else None,'poster':'poster.jpg' if (self.package/'poster.jpg').exists() else None})
 def verify_stage(self,stage):
  if stage=='rig':
   if self.args.mode=='control':self.need(self.root/'control/data/meta.json',self.root/'control/control-reference.npz')
   else:
    self.need(self.root/'rig/geometry.npz',self.root/'rig/rig.json');count=json.loads((self.root/'input.json').read_text())['frames']
    if len(list((self.root/'masks').glob('*.png')))!=count:raise PrerequisiteError('Source-mask count no longer matches prepared RGB')
  elif stage=='multiview':
   for name in ['pilot','offset']:
    self.need(self.work/name/'generation.json');g=json.loads((self.work/name/'generation.json').read_text());self.need(*(Path(x) for x in g['target_videos']))
  elif stage=='train':self.need(self.work/'seed-clean.npz')
  elif stage=='refine':
   m=self.verify_models()
   expected=json.loads((self.root/'input.json').read_text())['frames'] if self.args.trajectory_experiment and not self.args.seed_only else 121
   if m['covered_frames']!=expected:raise PrerequisiteError('Saved refinement has different time coverage; use a new root for a changed recipe')
  elif stage=='extend':
   self.need(self.root/'models.json');m=json.loads((self.root/'models.json').read_text())
   if m.get('full_method')!='fresh-twelve-direction-intervals' or m['covered_frames']!=json.loads((self.root/'input.json').read_text())['frames']:raise PrerequisiteError('The saved full-length extension is incomplete or uses a different recipe.')
   cursor=0
   for item in m['segments']:
    if item['start_frame']!=cursor or not 0<item['valid_frames']<=120 or item['valid_frames']!=min(120,m['covered_frames']-cursor):raise PrerequisiteError('The full-motion timeline has a gap, overlap or invalid playback length.')
    cursor+=item['valid_frames']
    path=safe(self.root,item['model']);self.need(path)
    if sha(path)!=item['sha256']:raise PrerequisiteError('A verified full-length checkpoint changed.')
   if cursor!=m['covered_frames']:raise PrerequisiteError('The saved interval sum does not cover the full source.')
  elif stage=='render':
   if self.args.mode=='control':self.need(*(self.root/'control'/name for name in ['source.mp4','comparison.mp4','manifest.json']))
   else:
    models=self.verify_models();video=self.render_dir()/'comparison.mp4';record=self.render_dir()/'rendered.json';self.need(video,record);saved=json.loads(record.read_text())
    if saved.get('models_sha256')!=sha(self.root/'models.json') or saved.get('renderer_sha256')!=sha(HERE/'render_sequence.py') or saved.get('frames')!=models['covered_frames'] or saved.get('comparison_mp4_sha256')!=sha(video) or saved.get('full_video_decode') is not True:raise PrerequisiteError('Saved render metadata or video differs from the verified model inventory. Preserve the files and inspect the rendering output.')
  elif stage=='package':
   if self.args.mode=='reconstruction':self.verify_models()
   check_package(self.package)

 @staticmethod
 def copy(source,dest):
  if source.is_dir():shutil.copytree(source,dest)
  else:shutil.copy2(source,dest)


def check_package(package,deep=False,ffmpeg=None,report_path=None):
 package=package.resolve();manifest=json.loads((package/'manifest.json').read_text());end=0.;reports=[]
 if not manifest.get('segments'):raise ValueError('Package has no model intervals')
 for item in manifest['segments']:
  if abs(float(item['start'])-end)>1e-4:raise ValueError('Missing or overlapping timeline interval')
  duration=float(item['duration'])
  if not math.isfinite(duration) or duration<=0:raise ValueError('Invalid interval duration')
  end+=duration;folder=safe(package,item['root']);meta=json.loads((folder/'meta.json').read_text());N=meta['gaussians'];files={}
  if not isinstance(N,int) or N<=0 or meta['frames']<=0 or meta['fps']<=0:raise ValueError('Model dimensions/time base must be positive')
  if duration>float(meta['duration'])+1e-4:raise ValueError('Played interval exceeds model time coverage')
  for name,record in meta['files'].items():
   path=safe(folder,name);raw=gzip.decompress(path.read_bytes());assert len(raw)==record['raw_bytes'];assert hashlib.sha256(raw).hexdigest()==record['raw_sha256'];files[name]=raw
   if deep and name.endswith(('.f32.gz','.f16.gz')):
    fmt='<e' if name.endswith('.f16.gz') else '<f'
    if not all(math.isfinite(x[0]) for x in struct.iter_unpack(fmt,raw)):raise ValueError(f'Nonfinite values in {name}')
  field=files['gaussians.f32.gz'];assert len(field)==N*14*4
  if meta.get('representation')=='soma-skinned-gaussians':
   bones=meta['bones'];influences=meta['influences'];assert len(files['bone-matrices.f32.gz'])==meta['frames']*bones*16*4;assert len(files['bone-weights.f32.gz'])==N*influences*4
   error=0.
   for sample in meta['parity_samples']:
    idx,frame=sample['index'],sample['frame'];xyz=struct.unpack_from('<3f',field,idx*56);position=[0.,0.,0.]
    for k in range(influences):
     bi=struct.unpack_from('<H',files['bone-indices.u16.gz'],(idx*influences+k)*2)[0];assert bi<bones;weight=struct.unpack_from('<f',files['bone-weights.f32.gz'],(idx*influences+k)*4)[0];matrix=struct.unpack_from('<16f',files['bone-matrices.f32.gz'],(frame*bones+bi)*64)
     for axis in range(3):position[axis]+=weight*(sum(matrix[axis*4+j]*xyz[j] for j in range(3))+matrix[axis*4+3])
    error=max(error,max(abs(a-b) for a,b in zip(position,sample['position'])))
   if error>1e-4:raise ValueError('SOMA native position parity failed')
  else:
   assert len(files['motion.f32.gz'])==N*16 and len(files['variance.f32.gz'])==N*16 and len(files['sh.f16.gz'])==N*48*2;error=0.
   for sample in meta['parity_samples']:
    idx=sample['index'];xyz=struct.unpack_from('<3f',field,idx*56);vel=struct.unpack_from('<4f',files['motion.f32.gz'],idx*16);dt=sample['time']-vel[3];position=[xyz[j]+vel[j]*dt for j in range(3)];error=max(error,max(abs(a-b) for a,b in zip(position,sample['position'])))
    if 'opacity' in sample:
     peak=struct.unpack_from('<f',field,idx*56+40)[0];invvar=struct.unpack_from('<f',files['variance.f32.gz'],idx*16)[0];error=max(error,abs(peak*math.exp(-.5*dt*dt*invvar)-sample['opacity']))
   if error>1e-4:raise ValueError('Native conditional numeric parity failed')
  reports.append({'id':item['id'],'gaussians':N,'frames':meta['frames'],'native_numeric_max_position_error':error,'hashes_verified':True})
 if abs(end-float(manifest['duration']))>1e-4:raise ValueError('Timeline total differs from manifest')
 source_url=manifest.get('source',{}).get('url')
 if source_url:
  source=safe(package,source_url);assert source.is_file() and source.stat().st_size>0
 else:
  youtube=manifest.get('source',{}).get('youtube_id','')
  if len(youtube)!=11 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in youtube):raise ValueError('Model-only packages require an explicit official YouTube reference')
  if manifest['source'].get('attribution_url')!='https://www.youtube.com/shorts/'+youtube:raise ValueError('YouTube source citation differs from the embed')
 videos_decoded=[]
 if ffmpeg:
  for name in [source_url,manifest.get('comparison')]:
   if name:subprocess.run([ffmpeg,'-v','error','-i',str(safe(package,name)),'-f','null','-'],check=True);videos_decoded.append(name)
 result={'schema':1,'pass':True,'duration':end,'segments':reports,'deep_finite_check':deep,'videos_fully_decoded':videos_decoded,'scope':'File/time/numeric export validation, not real-person geometry accuracy'};
 if report_path:write(report_path,result)
 return result


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--config',type=Path);p.add_argument('--mode',choices=['reconstruction','control'],default='reconstruction');p.add_argument('--package-dir',type=Path);p.add_argument('--video',type=Path);p.add_argument('--seed-only',action='store_true');p.add_argument('--trajectory-experiment',action='store_true');p.add_argument('--fetch-sources',action='store_true');p.add_argument('--deep',action='store_true');p.add_argument('--port',type=int,default=8099);p.add_argument('stage',choices=STAGES);a=p.parse_args()
 if a.seed_only and a.trajectory_experiment:p.error('--seed-only and --trajectory-experiment select different refinement scopes')
 try:r=Runner(a)
 except (PrerequisiteError,ValueError,OSError) as exc:print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(2)
 try:
  if a.stage=='check':print(json.dumps(check_package(r.package,a.deep,shutil.which(r.config.get('ffmpeg','ffmpeg')),r.root/'checks.json'),indent=2));return
  if a.stage=='serve':
   r.need(r.package/'manifest.json');print(f'Package: http://127.0.0.1:{a.port}/manifest.json\nOpen the Pages human-4d-gaussian lab and select this local result folder. This local server serves data only, not GPU inference.',flush=True)
   handler=lambda *args,**kwargs:http.server.SimpleHTTPRequestHandler(*args,directory=str(r.package),**kwargs);http.server.ThreadingHTTPServer(('127.0.0.1',a.port),handler).serve_forever();return
  journal=r.journal_path();recipe={'config':r.config,'mode':a.mode,'seed_only':a.seed_only if a.stage=='refine' else False}
  if a.stage=='refine':recipe['trajectory_experiment']=a.trajectory_experiment
  if a.stage in ['render','package'] and (r.root/'models.json').is_file():recipe['models']=sha(r.root/'models.json')
  if a.stage=='package':recipe['package']=str(r.package)
  fingerprint=hashlib.sha256(json.dumps(recipe,sort_keys=True).encode()).hexdigest()
  if a.stage not in ['setup','prepare'] and journal.exists():
   old=json.loads(journal.read_text())
   if old.get('status')=='completed':
    if old.get('configuration_sha256')!=fingerprint:raise PrerequisiteError('Completed stage has a different configuration. Use a fresh output root to preserve existing results.')
    r.verify_stage(a.stage);print(json.dumps({'stage':a.stage,'status':'reused-verified-existing-outputs','new_gpu_execution':False}));return
  if a.stage=='refine' and (r.ref/'roi-original').exists():raise PrerequisiteError('Partial refinement outputs already exist. Preserve them and use a fresh root or finish the explicit adapter stages; this runner will not silently overwrite model experiments.')
  write(journal,{'stage':a.stage,'status':'running','started_unix':time.time(),'configuration_sha256':fingerprint});gpu=a.stage in ['rig','multiview','train','refine','extend','render']
  if gpu:r.need(r.root/'setup.json')
  with contextlib.ExitStack() as stack:
   if gpu:
    lock=r.path('gpu_lock');lock.parent.mkdir(parents=True,exist_ok=True);f=stack.enter_context(lock.open('a+'));fcntl.flock(f,fcntl.LOCK_EX)
   getattr(r,'package_stage' if a.stage=='package' else a.stage)()
  write(journal,{'stage':a.stage,'status':'completed','finished_unix':time.time(),'configuration_sha256':fingerprint});print(json.dumps({'stage':a.stage,'status':'completed','root':str(r.root)}))
 except (PrerequisiteError,ValueError,AssertionError,KeyError,TypeError,OSError,subprocess.CalledProcessError) as exc:
  if a.stage not in ['check','serve'] and not (r.journal_path().exists() and json.loads(r.journal_path().read_text()).get('status')=='completed'):write(r.journal_path(),{'stage':a.stage,'status':'failed','error':str(exc),'finished_unix':time.time()})
  print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(2)
if __name__=='__main__':main()
