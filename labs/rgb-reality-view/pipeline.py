"""Reproduce an RGB-only driving-scene reconstruction on one RTX 5090.

All outputs stay local. Model/scene/data rights are separate from this MIT code.
Use --help; the bilingual guide explains setup, own videos, and source licenses.
"""
import argparse,hashlib,json,os,platform,re,shutil,subprocess,time
from pathlib import Path
from input_guard import verify_rgb_inputs
LAB=Path(__file__).resolve().parent
PIN='dfd3d54c8c612003fb7948443edf7778f2bcd5ec'
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(os.environ.get('RGB_VIEW_ROOT',str(Path.home()/'physical-ai-labs/rgb-road'))));p.add_argument('--input',type=Path,help='Your RGB image folder, optionally one subfolder per camera');p.add_argument('--video',type=Path,help='Your RGB video, extracted locally with FFmpeg');p.add_argument('--sample-fps',type=float,default=3);p.add_argument('--capture-fps',type=float,default=10);p.add_argument('--front-folder',default='front_camera');p.add_argument('--cuda-home',type=Path);p.add_argument('--iterations',type=int,default=16000);p.add_argument('--port',type=int,default=8090);p.add_argument('stage',choices=['setup','example','ingest','sfm','train','export','serve','perceive','all']);a=p.parse_args();root=a.root.expanduser().resolve();root.mkdir(parents=True,exist_ok=True);sfm_py=root/'.venv/bin/python';source=root/'3dgrut';gpu_py=source/'.venv/bin/python'
def run(args,**kwargs):return subprocess.run([str(x) for x in args],check=True,**kwargs)
def uv_path():
 uv=shutil.which('uv') or str(Path.home()/'.local/bin/uv')
 if not Path(uv).is_file():raise SystemExit('Install uv first: https://docs.astral.sh/uv/getting-started/installation/')
 return uv
def cuda_home():
 candidates=[a.cuda_home] if a.cuda_home else [Path('/usr/local/cuda'),*Path('/usr/local').glob('cuda-*')]
 valid=[]
 for d in candidates:
  if not d or not (d/'bin/nvcc').is_file():continue
  text=subprocess.check_output([str(d/'bin/nvcc'),'--version'],text=True);m=re.search(r'release (\d+)\.(\d+)',text)
  if m and (int(m[1]),int(m[2])) in [(12,8),(12,9)]:valid.append((int(m[2]),d.resolve()))
 if not valid:raise SystemExit('This preset needs a CUDA 12.8/12.9 toolkit. Pass --cuda-home /path/to/cuda; CUDA 12.0 cannot compile for RTX 5090.')
 return max(valid,key=lambda pair:pair[0])[1]
def gpu_env():
 cuda=cuda_home();return {**os.environ,'CUDA_HOME':str(cuda),'PATH':f'{cuda}/bin:{os.environ.get("PATH","")}','TORCH_CUDA_ARCH_LIST':'12.0','MAX_JOBS':'2','OMP_NUM_THREADS':'8','CUDA_VISIBLE_DEVICES':'0','WANDB_MODE':'disabled','UV_INDEX':'pytorch=https://download.pytorch.org/whl/cu128'}
def setup():
 if platform.system()!='Linux' or platform.machine() not in {'x86_64','AMD64'}:raise SystemExit('GPU reconstruction preset: Linux x86_64. The viewer and saved-result checks also run on Mac/Windows.')
 uv=uv_path();env=gpu_env()
 if not sfm_py.exists():run([uv,'venv','--python','3.11',sfm_py.parent.parent])
 run([uv,'pip','install','--python',sfm_py,'pycolmap-cuda12==3.13.0','Pillow==13.0.0','numpy==2.4.6','scipy==1.17.1','plyfile==1.1.5','imageio-ffmpeg==0.6.0'])
 if not source.exists():run(['git','clone','--recursive','https://github.com/nv-tlabs/3dgrut.git',source])
 head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
 if head!=PIN:
  if subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip():raise SystemExit('The 3DGRUT checkout has edits. Use a fresh output folder; your changes were preserved.')
  run(['git','-C',source,'checkout',PIN]);run(['git','-C',source,'submodule','update','--init','--recursive'])
 if not gpu_py.exists():run([uv,'venv','--python','3.11',gpu_py.parent.parent])
 run([uv,'pip','install','--python',gpu_py,'torch==2.8.0','torchvision==0.23.0','--index-url','https://download.pytorch.org/whl/cu128'])
 run([uv,'pip','install','--python',gpu_py,'-c',LAB/'constraints.txt','-e',str(source)+'[gui]'],env=env)
 installed=subprocess.run([str(gpu_py),'-c','import tinycudann'],env=env,capture_output=True)
 if installed.returncode:run([uv,'pip','install','--python',gpu_py,'--no-build-isolation',source/'thirdparty/tiny-cuda-nn/bindings/torch'],env=env)
 run([uv,'pip','install','--python',gpu_py,'kaolin==0.18.0','-f','https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.8.0_cu128.html'],env=env)
 run([uv,'pip','install','--python',gpu_py,'--no-build-isolation','-r',source/'requirements_extra.txt','slangtorch==1.3.18','pycolmap-cuda12==3.13.0'],env=env)
 run([gpu_py,'-c','import torch,tinycudann,kaolin,ppisp,slangtorch;from fused_ssim import fused_ssim;assert torch.cuda.is_available();print("GPU environment ready:",torch.cuda.get_device_name(0))'],env=env)
 (root/'setup.done.json').write_text(json.dumps({'3dgrut_commit':PIN,'torch':'2.8.0+cu128','sfm':'pycolmap-cuda12 3.13.0','cuda_toolkit':str(cuda_home().name),'arch':'12.0','reconstruction_pretrained_weights_required':False,'perception_weights':'public TorchVision COCO_V1; downloaded on first perception run'},indent=2)+'\n')
def ingest():
 if a.video:
  ffmpeg=shutil.which('ffmpeg')
  if not ffmpeg:ffmpeg=subprocess.check_output([str(sfm_py),'-c','import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],text=True).strip()
  frames=root/'video-rgb/camera';frames.mkdir(parents=True,exist_ok=True);run([ffmpeg,'-v','error','-i',a.video,'-vf',f'fps={a.sample_fps}','-q:v','2',frames/'%06d.jpg']);src=frames.parent
 elif a.input:src=a.input
 else:raise SystemExit('Use --input /path/to/RGB or --video /path/to/clip.mp4; omit both for the public example in stage all.')
 run([sfm_py,LAB/'prepare_images.py','--input',src,'--output',root/'work'])
 (root/'ingest.json').write_text(json.dumps({'kind':'video' if a.video else 'images','sample_fps':a.sample_fps if a.video else a.capture_fps,'front_folder':'camera' if a.video else a.front_folder},indent=2)+'\n')
def sfm():
 verify_rgb_inputs(root/'work');run([sfm_py,LAB/'sfm.py','--root',root/'work','--device','cuda'],env=gpu_env())
def train():
 verify_rgb_inputs(root/'work')
 expected=json.loads((root/'work/sfm-result.json').read_text())['registered_images']
 count=int(subprocess.check_output([str(sfm_py),'-c','import sys,pycolmap as c;print(c.Reconstruction(sys.argv[1]).num_reg_images())',str(root/'work/undistorted/sparse/0')],text=True).strip())
 if count!=expected:raise RuntimeError('The selected and undistorted RGB model have different image counts; rerun the sfm stage.')
 env=gpu_env();out=root/'train';args=[gpu_py,source/'train.py','--config-name','apps/colmap_3dgut_mcmc.yaml',f'path={root}/work/undistorted',f'out_dir={out}','experiment_name=rgb-only',f'n_iterations={a.iterations}','num_workers=2','strategy.add.max_n_gaussians=400000','export_ply.enabled=true','export_usd.enabled=false','test_last=false','with_gui=false','with_viser_gui=false','compute_extra_metrics=false','enable_frame_timings=true','log_frequency=100','enable_writer=false','dataset.load_exif=false']
 start=time.perf_counter();samples=[]
 import fcntl
 with open(os.environ.get('GPU_LOCK','/tmp/rgb-reality-view.gpu.lock'),'w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with (root/'train.log').open('w') as log:
   child=subprocess.Popen([str(x) for x in args],cwd=source,env=env,stdout=log,stderr=subprocess.STDOUT)
   while child.poll() is None:
    try:
     values=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0].split(',');samples.append({'t_seconds':time.perf_counter()-start,'gpu_memory_mib':int(values[0]),'utilization_percent':int(values[1])})
    except (subprocess.SubprocessError,ValueError):pass
    time.sleep(1)
   if child.returncode:raise SystemExit(f'Training failed. Inspect {root/"train.log"}; raw logs stay in your output folder.')
 log=(root/'train.log').read_text(errors='replace');tables=re.findall(r'│\s*(\d+)\s*│\s*(\d+)\s*│\s*([\d.]+)\s*s\s*│',log);models=list(out.rglob('export_last.ply'))
 if not models or not tables:raise RuntimeError('No completed model and observed training summary were found')
 artifact=max(models,key=lambda p:p.stat().st_mtime);steps,epochs,seconds=tables[-1]
 report={'3dgrut_commit':PIN,'training_steps':int(steps),'epochs':int(epochs),'training_loop_seconds':float(seconds),'wall_seconds_including_compile':time.perf_counter()-start,'gpu_count':1,'gpu_memory_mib_sampled_total_peak':max((s['gpu_memory_mib'] for s in samples),default=0),'memory_scope':'nvidia-smi total GPU usage sampled each second; includes display/background allocations','input_manifest_sha256':hashlib.sha256((root/'work/input-manifest.json').read_bytes()).hexdigest(),'dataset_type':'COLMAP estimated from RGB','test_last':False,'evaluation_scope':'No independent novel-view accuracy claim. All images inform SfM; photometric train/validation split is not a sensor-exclusion benchmark.','ply':str(artifact.relative_to(root))}
 (root/'training-result.json').write_text(json.dumps(report,indent=2)+'\n');print('TRAIN_COMPLETE',json.dumps(report),flush=True)
def perceive():
 verify_rgb_inputs(root/'work')
 # Older local installs may predate the perception extension.
 run([uv_path(),'pip','install','--python',gpu_py,'pycolmap-cuda12==3.13.0'])
 import fcntl
 with open(os.environ.get('GPU_LOCK','/tmp/rgb-reality-view.gpu.lock'),'w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);run([gpu_py,LAB/'perceive.py','--root',root],env=gpu_env())
def export():
 verify_rgb_inputs(root/'work');report=json.loads((root/'training-result.json').read_text());folder=a.front_folder
 ingest=json.loads((root/'ingest.json').read_text()) if (root/'ingest.json').exists() else {}
 if ingest.get('kind')=='video':folder='camera'
 if folder=='front_camera':
  groups={row['image'].split('/')[0] for row in verify_rgb_inputs(root/'work')['images']}
  if folder not in groups and len(groups)==1:folder=next(iter(groups))
 out=root/'viewer';run([sfm_py,LAB/'prepare_viewer.py','--root',root/'work','--output',out,'--front-folder',folder,'--capture-fps',ingest.get('sample_fps',a.capture_fps)])
 npm=shutil.which('npm')
 if not npm:raise SystemExit('Install Node.js/npm to create the compressed browser model; the full RGB-only PLY has already been saved.')
 run([npm,'exec','--yes','--package=@playcanvas/splat-transform@3.12.0','--','splat-transform','-w',root/report['ply'],'--filter-harmonics','1',out/'road.spz','--spz-version','3'])
 shutil.copy2(LAB/'assets/volvo-s90.glb',out/'volvo-s90.glb')
 for name in ['viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js']:shutil.copy2(LAB/name,out/name)
 shutil.copy2(LAB/'assets/VEHICLE-LICENSE.txt',out/'VEHICLE-LICENSE.txt')
 if (root/'PANDASET-DATA-LICENSE.txt').exists():shutil.copy2(root/'PANDASET-DATA-LICENSE.txt',out/'PANDASET-DATA-LICENSE.txt');credits=(LAB/'assets/EXAMPLE-ATTRIBUTION.txt').read_text()
 else:credits='Scene: user-provided RGB images; preserve their original rights.\n'+(LAB/'assets/VEHICLE-LICENSE.txt').read_text()
 (out/'ATTRIBUTION.txt').write_text(credits);print('VIEWER_READY',str(out),flush=True)
if a.stage=='setup':setup()
elif a.stage=='example':run([sfm_py,LAB/'fetch_example.py','--root',root])
elif a.stage=='ingest':ingest()
elif a.stage=='sfm':sfm()
elif a.stage=='train':train()
elif a.stage=='export':export()
elif a.stage=='perceive':perceive()
elif a.stage=='serve':run(['python3',LAB/'serve.py','--root',root/'viewer','--port',a.port])
else:
 if not (root/'setup.done.json').exists():setup()
 if a.input or a.video:ingest()
 else:run([sfm_py,LAB/'fetch_example.py','--root',root])
 sfm();train();export();perceive();run(['python3',LAB/'serve.py','--root',root/'viewer','--port',a.port])
