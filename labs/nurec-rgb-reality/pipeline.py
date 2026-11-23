"""Reproduce the RGB-only NuRec + Harmonizer + Alpamayo demonstration.

One NVIDIA GPU is used sequentially. All generated data, caches and raw logs are
stored in --root outside the repository. Runtime/model/data terms stay separate.
"""
import argparse,os,platform,shutil,subprocess
from pathlib import Path
LAB=Path(__file__).resolve().parent;SHARED=LAB.parent/'rgb-reality-view'
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.home()/'physical-ai-labs/nurec-rgb-road');p.add_argument('--model-root',type=Path,default=Path.home()/'physical-ai-models');p.add_argument('--assumed-camera-height-m',type=float,default=1.8,help='Explicit scale prior for Alpamayo only; not measured from RGB');p.add_argument('--port',type=int,default=8092);p.add_argument('--no-serve',action='store_true',help='Complete GPU/export stages and exit without starting HTTP');p.add_argument('stage',choices=['setup','rgb','rig','prepare','train','render','enhance','policy','perceive','export','serve','all']);a=p.parse_args();root=a.root.expanduser().resolve();root.mkdir(parents=True,exist_ok=True);modelroot=a.model_root.expanduser().resolve();sfm=root/'.venv/bin/python';detector=root/'.perception-venv/bin/python';uv=shutil.which('uv') or str(Path.home()/'.local/bin/uv');env={**os.environ,'NUREC_RGB_ROOT':str(root),'RGB_VIEW_ROOT':str(root/'rgb-source'),'RGB_SFM_PYTHON':str(sfm),'ALPAMAYO_ROOT':str(modelroot),'REALITY_VIEW_ROOT':str(root),'HARMONIZER_WEIGHTS':str(root/'checkpoints/Harmonizer'),'UV_BIN':uv,'CUDA_VISIBLE_DEVICES':'0','OMP_NUM_THREADS':'8'}
def run(args,**kw):return subprocess.run([str(v) for v in args],check=True,env=env,**kw)
def lockrun(args):return run(['flock',env.get('GPU_LOCK','/tmp/rgb-reality-view.gpu.lock'),*args])
def shell(stage):return run(['bash',LAB/'run.sh',stage])
def setup():
 if platform.system()!='Linux':raise SystemExit('GPU workflow: Linux with NVIDIA Container Toolkit. Saved-result viewing also works on Mac/Windows.')
 if not Path(uv).is_file():raise SystemExit('Install uv: https://docs.astral.sh/uv/getting-started/installation/')
 if not sfm.exists():run([uv,'venv','--python','3.11',sfm.parent.parent])
 run([uv,'pip','install','--python',sfm,'pycolmap-cuda12==3.13.0','numpy==2.4.6','Pillow==13.0.0','scipy==1.17.1','plyfile==1.1.5'])
 # Review NGC runtime terms and model licenses in SOURCES.md before setup.
 run(['docker','pull','nvcr.io/nvidia/nre/nre-ga:26.04@sha256:97f43e7130c5636ce3e80ea3184d97f56a87fdd989b05cce42230881dbdea284'])
 run(['bash',LAB.parent/'reality-view/setup_models.sh']);run([sfm,LAB/'setup_metrics.py','--root',root])
 if not detector.exists():run([uv,'venv','--python','3.11',detector.parent.parent])
 run([uv,'pip','install','--python',detector,'torch==2.8.0','torchvision==0.23.0','--index-url','https://download.pytorch.org/whl/cu128'])
 run([uv,'pip','install','--python',detector,'pycolmap-cuda12==3.13.0','numpy==2.4.6','Pillow==13.0.0','scipy==1.17.1'])
def rgb():
 source=root/'rgb-source'
 run([sfm,SHARED/'fetch_example.py','--root',source]);shutil.copy2(source/'PANDASET-DATA-LICENSE.txt',root/'PANDASET-DATA-LICENSE.txt')
 lockrun([sfm,SHARED/'sfm.py','--root',source/'work','--device','cuda'])
def rig():
 run([sfm,LAB/'rig_bundle.py','--rgb-root',root/'rgb-source','--output',root/'rig-source']);run([sfm,SHARED/'prepare_viewer.py','--root',root/'rig-source/work','--output',root/'rig-source/viewer']);env['RGB_VIEW_ROOT']=str(root/'rig-source');shell('export-rgb')
def policy():
 run([sfm,LAB/'prepare_policy.py','--root',root,'--assumed-camera-height-m',a.assumed_camera_height_m]);lockrun([modelroot/'alpamayo2-edge/.venv/bin/python',LAB/'run_policy.py','--root',root,'--model',modelroot/'checkpoints/Alpamayo2-Edge'])
def perceive():lockrun([detector,SHARED/'perceive.py','--root',root/'rig-source'])
def export():run([sfm,LAB/'export_viewer.py','--root',root])
def serve():run(['python3',SHARED/'serve.py','--root',root/'viewer','--port',a.port])
def train():shell('train');shell('collect');shell('export-ply')
functions={'setup':setup,'rgb':rgb,'rig':rig,'prepare':lambda:shell('prepare'),'train':train,'render':lambda:shell('render'),'enhance':lambda:shell('enhance'),'policy':policy,'perceive':perceive,'export':export,'serve':serve}
if a.stage=='all':
 for stage in ['setup','rgb','rig','prepare','train','render','enhance','policy','perceive','export']:
  print('RGB_NUREC_STAGE',stage,flush=True);functions[stage]()
 if not a.no_serve:serve()
 print('RGB_NUREC_PIPELINE_COMPLETE',flush=True)
else:functions[a.stage]()
