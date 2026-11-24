"""One actual new multiview interval, with durable stage and output checks.

The caller owns GPU locking. This helper neither installs runtimes nor acquires
another lock. It consumes prepared RGB, fitted geometry, masks and the completed
seed coordinate frame. All paths and journals stay in the selected local root.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as stream:
  for block in iter(lambda:stream.read(8<<20),b''):h.update(block)
 return h.hexdigest()
def write(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n');temp.replace(path)
def inventory(paths):
 files=[]
 for path in paths:
  if not path.exists():raise ValueError(f'Missing completed-stage output: {path}')
  files.extend(sorted(p for p in path.rglob('*') if p.is_file()) if path.is_dir() else [path])
 return [{'path':str(x),'bytes':x.stat().st_size,'sha256':sha(x)} for x in files]
def verify(records):
 for row in records:
  path=Path(row['path'])
  if not path.is_file() or path.stat().st_size!=row['bytes'] or sha(path)!=row['sha256']:raise ValueError(f'Completed output changed or disappeared: {path}; preserve this run and choose a fresh output root')


def preserve_or_update_recipe(recipe,spec,state_path):
 """Allow reviewed teacher rejection before fitting, never a new experiment.

 Generation inputs, runtime/code hashes and generation settings stay frozen.
 Exclusions may change only after a completed views-only review checkpoint.
 """
 if not recipe.exists():
  if recipe.parent.exists() and any(recipe.parent.iterdir()):raise ValueError('Unknown existing interval outputs have no recipe fingerprint; choose a fresh output directory')
  write(recipe,spec);return
 previous=json.loads(recipe.read_text())
 if previous==spec:return
 changed={key for key in previous.keys() | spec.keys() if previous.get(key)!=spec.get(key)}
 state=json.loads(state_path.read_text()) if state_path.is_file() else {}
 stages=state.get('stages',{})
 review_only=(state.get('status')=='awaiting_teacher_review' and set(stages)=={'views-base','views-offset'} and all(row.get('status')=='complete' for row in stages.values()))
 if not changed or not changed <= {'excluded_base_cameras','loss_sampling'} or not review_only:raise ValueError('Input, recipe, runtime or adapter code changed; preserve this interval and select a fresh output root')
 for row in stages.values():verify(row['outputs'])
 previous_hash=sha(recipe);receipt=recipe.parent/f'recipe-before-curation-{previous_hash}.json'
 if receipt.exists():
  if sha(receipt)!=previous_hash:raise ValueError('The preserved pre-curation recipe changed; inspect this local run')
 else:shutil.copy2(recipe,receipt)
 update={'previous_recipe':receipt.name,'previous_recipe_sha256':previous_hash,'previous_exclusions':previous.get('excluded_base_cameras',[]),'new_exclusions':spec.get('excluded_base_cameras',[]),'scope':'Explicit human teacher rejection before any fitting stage; no automatic orientation/identity quality decision'}
 state.setdefault('teacher_curation',[]).append(update)
 write(recipe,spec);write(state_path,state)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--out',type=Path);p.add_argument('--config',type=Path);p.add_argument('--steps',type=int,default=20000);p.add_argument('--hires-steps',type=int,default=6000);p.add_argument('--roi-steps',type=int,default=3000);p.add_argument('--geometry-steps',type=int,default=1500);p.add_argument('--base-seed',type=int,default=42);p.add_argument('--offset-seed',type=int,default=42);p.add_argument('--base-profile',choices=['turbo','base24'],default='turbo');p.add_argument('--exclude-base-cameras',default='');p.add_argument('--views-only',action='store_true');p.add_argument('--roi-source-stride',type=int,default=1);p.add_argument('--roi-source-offset',type=int,default=0);a=p.parse_args();r=a.root.expanduser().resolve();w=r/'multiview-prior';case=w/a.name;offset=w/(a.name+'-offset');out=(a.out or case/'fresh-refinement').expanduser().resolve()
 if not a.name or any(x not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for x in a.name) or a.name in ['pilot','offset']:raise ValueError('Use a simple new interval name, such as s01')
 if not out.is_relative_to(r):raise ValueError('Interval outputs must stay within the local runtime root')
 if any(x<1 for x in [a.steps,a.hires_steps,a.roi_steps,a.geometry_steps,a.roi_source_stride]):raise ValueError('Training steps and source stride must be positive')
 config_path=a.config or r/'runtime.json'
 if not config_path.is_file():raise ValueError('Missing runtime.json; configure the isolated runtimes with pipeline.py setup first')
 config=json.loads(config_path.read_text());meta=json.loads((r/'input.json').read_text());count=meta['frames']
 if not 0<a.start<count:raise ValueError('A fresh later interval must start after frame 0 and before the end of the prepared clip')
 excluded={int(x) for x in a.exclude_base_cameras.split(',') if x}
 if not excluded <= set(range(1,6)):raise ValueError('Only generated base cameras1..5 may be explicitly rejected')
 valid=min(121,count-a.start);ids=[min(t,count-1) for t in range(a.start,a.start+121)]
 def configured_python(name):
  path=Path(config['python'][name]).expanduser();path=path if path.is_absolute() else r/path
  if not path.is_file():raise ValueError(f'Missing isolated {name} Python in runtime.json')
  return path
 py=configured_python('reconstruction');moge_py=configured_python('moge');env=os.environ.copy();cuda=config.get('cuda_home')
 if cuda:env['CUDA_HOME']=cuda;env['PATH']=str(Path(cuda)/'bin')+os.pathsep+env.get('PATH','')
 env['TORCH_CUDA_ARCH_LIST']=config.get('cuda_arch','12.0');env['MAX_JOBS']='2'
 required=[r/'input.json',r/'input.mp4',r/'rig/geometry.npz',w/'pilot/soma-conditioning.npz',*[r/f'frames/{i+1:06d}.jpg' for i in sorted(set(ids))],*[r/f'masks/{i+1:06d}.png' for i in sorted(set(ids))]]
 missing=[str(x) for x in required if not x.is_file()]
 if missing:raise ValueError('Missing prepared seed/input files: '+', '.join(missing))
 # Playback length comes from prepared RGB; never silently clamp an incomplete
 # fitted motion export and then claim that those missing frames were trained.
 import numpy as np
 with np.load(r/'rig/geometry.npz',allow_pickle=False) as fitted:
  temporal=['joints','vertices','K']+[x for x in ['deformations','D','times','observations'] if x in fitted.files]
  if not any(x in fitted.files for x in ['deformations','D']):raise ValueError('Fitted geometry has no bone deformation sequence')
  for key in temporal:
   values=fitted[key]
   if values.ndim<1 or len(values)!=count or not np.isfinite(values).all():raise ValueError(f'Fitted {key} must contain exactly {count} finite prepared-time frames')
  if fitted['joints'].ndim!=3 or fitted['joints'].shape[-1]!=3 or fitted['vertices'].ndim!=3 or fitted['vertices'].shape[-1]!=3:raise ValueError('Invalid fitted joint/vertex tensor layout')
  if fitted['K'].shape!=(count,3,3):raise ValueError('Expected one 3x3 intrinsic matrix per prepared frame')
  if not np.allclose(fitted['K'][ids],fitted['K'][ids[0]],rtol=1e-5,atol=1e-3):raise ValueError('This static-camera interval requires constant estimated intrinsics')
  for key in ['deformations','D']:
   if key in fitted.files and (fitted[key].ndim!=4 or fitted[key].shape[-2:]!=(4,4)):raise ValueError('Expected bone transforms [T,bones,4,4]')
  if 'times' in fitted.files and (fitted['times'].shape!=(count,) or not np.allclose(fitted['times'],np.arange(count)/30,rtol=0,atol=1e-4)):raise ValueError('Fitted times must match the shared normalized 30Hz RGB timeline')

 scripts=['fresh_interval.py','multiview.py','seed_train.py','clean_model.py','fresh_hires.py','fresh_roi.py','train_refine.py','geometry_loss.py','moge_infer.py','align_geometry.py']
 spec={'schema':1,'name':a.name,'start_frame':a.start,'valid_frames':valid,'source_frame_ids':ids,'steps':a.steps,'hires_steps':a.hires_steps,'roi_steps':a.roi_steps,'geometry_steps':a.geometry_steps,'roi_source_stride':a.roi_source_stride,'roi_source_offset':a.roi_source_offset,'generator':{'base':{'views':6,'yaw':0,'profile':a.base_profile,'seed':a.base_seed},'offset':{'views':6,'yaw':30,'profile':'turbo','seed':a.offset_seed},'rcp':False},'excluded_base_cameras':sorted(excluded),'loss_sampling':f'3:{5-len(excluded)} seed;6:{11-len(excluded)} high-resolution observed/generated; duplicates are weighting only','input_inventory':inventory(required),'runtime_config_sha256':sha(config_path),'source_code':{x:sha(HERE/x) for x in scripts}}
 recipe=out/'recipe.json';state_path=out/'stages.json'
 preserve_or_update_recipe(recipe,spec,state_path)
 state=json.loads(state_path.read_text()) if state_path.exists() else {'name':a.name,'start_frame':a.start,'valid_frames':valid,'stages':{}}
 def run(label,script,args,outputs,python=py,partial=None,resume_native=False):
  old=state['stages'].get(label)
  if old and old['status']=='complete':verify(old['outputs']);print('FRESH_STAGE_REUSED',a.name,label,flush=True);return
  if old and partial is not None and partial.exists():
   # Preserve failed/interrupted ROI or diffusion outputs before a deterministic
   # retry. Native optimizers alone resume their verified checkpoint format.
   if resume_native:
    ck=partial/'checkpoints'
    if ck.exists():shutil.copytree(ck,partial/f'checkpoints-before-resume-{time.time_ns()}')
   else:partial.rename(partial.with_name(partial.name+f'.partial-{time.time_ns()}'))
  unknown=outputs[:2] if label in ['views-base','views-offset'] else outputs
  if old and partial is None:
   for target in outputs:
    if target.exists():target.rename(target.with_name(target.name+f'.partial-{time.time_ns()}'))
  if not old and any(x.exists() for x in unknown):raise ValueError(f'Unknown existing {label} outputs cannot be silently adopted; choose a new interval name/output folder')
  started=time.time();state.update(status='running',current_stage=label);state['stages'][label]={'status':'running','started_at':started};write(state_path,state);print('FRESH_STAGE_START',a.name,label,flush=True)
  argv=[str(python),'-u',str(HERE/script),'--root',str(r),*map(str,args)]
  with (out/f'{label}.log').open('w') as log:result=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,env=env)
  record=state['stages'][label];record.update(returncode=result.returncode,seconds=time.time()-started,status='complete' if result.returncode==0 else 'failed')
  if result.returncode==0:record['outputs']=inventory(outputs)
  write(state_path,state)
  if result.returncode:raise RuntimeError(f'{label} failed; read {out/(label+".log")}. Intermediate files remain local.')
  print('FRESH_STAGE_DONE',a.name,label,round(record['seconds'],2),flush=True)
 run('views-base','multiview.py',['--name',a.name,'--start',a.start,'--views',6,'--seed',a.base_seed,*(['--turbo'] if a.base_profile=='turbo' else [])],[case/'generation.json',case/'generated',case/'adapter.json',case/'soma-conditioning.npz'],partial=case/'generated')
 run('views-offset','multiview.py',['--name',a.name+'-offset','--start',a.start,'--views',6,'--start-yaw',30,'--seed',a.offset_seed,'--turbo'],[offset/'generation.json',offset/'generated',offset/'adapter.json',offset/'soma-conditioning.npz'],partial=offset/'generated')
 if a.views_only:
  for offset_view in [False,True]:
   contact=out/('teachers-offset.jpg' if offset_view else 'teachers-base.jpg');argv=[str(py),str(HERE/'inspect_teachers.py'),'--root',str(r),'--name',a.name,'--out',str(contact)]+(['--offset'] if offset_view else []);subprocess.run(argv,check=True,env=env)
  state['teacher_contact_sheets']=inventory([out/'teachers-base.jpg',out/'teachers-offset.jpg'])
  state.update(status='awaiting_teacher_review',current_stage=None,review_scope='Inspect generated orientation, body/hand coverage and identity across all views/times. No Gaussian fitting or selected model is claimed.');write(state_path,state);print('FRESH_VIEWS_READY_FOR_REVIEW',a.name,flush=True);return
 run('seed20k','seed_train.py',['--name',a.name,'--steps',a.steps,'--stop-after',a.steps,'--exclude-generated-cameras',','.join(map(str,sorted(excluded)))],[case/'reconstruction/checkpoints/latest.npz',case/'reconstruction/data',case/'reconstruction/data-plan.json'],partial=case/'reconstruction',resume_native=True)
 clean=out/'seed-clean.npz';run('clean-seed','clean_model.py',['--name',a.name,'--model',case/'reconstruction/checkpoints/latest.npz','--out',clean],[clean,clean.with_suffix('.cleanup.json')])
 hires=out/'hires';run('hires','fresh_hires.py',['--name',a.name,'--out',hires,'--base',clean,'--steps',a.hires_steps,'--stop-after',a.hires_steps],[hires/'checkpoints/latest.npz',hires/'data'],partial=hires,resume_native=True)
 roi=out/'roi';run('original-roi','fresh_roi.py',['--name',a.name,'--out',roi,'--source-stride',a.roi_source_stride,'--source-offset',a.roi_source_offset],[roi/'pixels.npz',roi/'crops.json',roi/'PROVENANCE.json'],partial=roi)
 roi_fit=out/'roi-fit';roi_model=roi_fit/f'model-{a.roi_steps}.npz';run('roi','train_refine.py',['--name',a.name+'-roi','--data',hires/'data','--base',hires/'checkpoints/latest.npz','--out',roi_fit,'--roi-root',roi,'--roi','--steps',a.roi_steps],[roi_model],partial=roi_fit)
 view_rows=json.loads((hires/'data/cameras.json').read_text())['cameras']
 geometry_ids=[0,2,3,4]
 if excluded:
  geometry_ids=[0]
  for desired_yaw in [120,150,210]:
   choices=[c for c in view_rows if c.get('supervision')=='generated' and c['camera_id'] not in geometry_ids]
   chosen=min(choices,key=lambda c:abs((float(c['yaw_degrees'])-desired_yaw+180)%360-180));geometry_ids.append(chosen['camera_id'])
 raw=out/'moge-raw';aligned=out/'moge-aligned';run('moge-infer','moge_infer.py',['--data',hires/'data','--out',raw,'--cameras',','.join(map(str,geometry_ids))],[raw],python=moge_py,partial=raw)
 run('moge-align','align_geometry.py',['--model',roi_model,'--raw',raw,'--out',aligned],[aligned],partial=aligned)
 geometry_fit=out/'geometry-fit';geometry_model=geometry_fit/f'model-{a.geometry_steps}.npz';run('geometry','train_refine.py',['--name',a.name+'-geometry','--data',hires/'data','--base',roi_model,'--out',geometry_fit,'--roi-root',roi,'--roi','--geometry',aligned,'--steps',a.geometry_steps],[geometry_model],partial=geometry_fit)
 final=out/'final-clean.npz';run('clean-final','clean_model.py',['--name',a.name,'--model',geometry_model,'--out',final],[final,final.with_suffix('.cleanup.json')])
 alias=case/'final.npz';digest=sha(final)
 if alias.exists() and sha(alias)!=digest:raise ValueError('Existing selected final model differs; preserve this interval and choose a new name/output root')
 if not alias.exists():shutil.copy2(final,alias)
 with np.load(final,allow_pickle=False) as z:final_meta=json.loads(z['metadata'].tobytes())
 camera_keys=[json.dumps([c['K'],c['w2c']],sort_keys=True) for c in final_meta['cameras']];unique_cameras=len(set(camera_keys))
 result={'schema':1,'id':a.name,'start_frame':a.start,'valid_frames':min(120,count-a.start),'valid_training_frames':valid,'internal_training_frames':121,'fps':30,'model':str(alias.relative_to(r)),'final_model':str(alias.relative_to(r)),'base_seed':a.base_seed,'offset_seed':a.offset_seed,'base_profile':a.base_profile,'offset_profile':'turbo','new_multiview_diffusion':True,'generated_camera_directions':12,'unique_training_cameras':unique_cameras,'synthetic_views_used':unique_cameras-1,'training_camera_slots':len(camera_keys),'excluded_base_cameras':sorted(excluded),'observed_cameras':1,'view_scope':'Observed RGB plus generated side/back priors, not measured unseen geometry','recipe_sha256':sha(recipe),'final_sha256':digest,'actual_done_flags':{k:v['status']=='complete' for k,v in state['stages'].items()}};write(out/'result.json',result);write(case/'selected.json',result);state.update(status='complete',current_stage=None,completed_at=time.time(),result=result);write(state_path,state);print('FRESH_INTERVAL_COMPLETE',json.dumps(result),flush=True)

if __name__=='__main__':main()
