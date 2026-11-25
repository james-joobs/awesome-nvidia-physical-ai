"""One-GPU, public-checkpoint-only temporal Reality View workflow."""
from __future__ import annotations
import argparse,hashlib,io,json,os,platform,shutil,subprocess,tarfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE_PIN='826c1998796e024bc82c9843b3ec515c50737573'
DEPS_PIN='a2c298b0a3df3778b973fe65e9e58877b292d8a7'
MODEL_PIN='20ca33d4612b1e98e0526b3a7ee604af5b289f58'
MODEL_SHA='6e65e9ec33019a49f7f0d15f81f5e089c2527e131bd5339d6a14f9b3531db524'
BASE='nvcr.io/nvidia/pytorch:25.10-py3@sha256:42263b2424fc237b34c4fc4a91c30d603c57eed36e37d31ff6d9a4f1f801edee'

def run(args,**kw):subprocess.run([str(x) for x in args],check=True,**kw)
def sha(path):return hashlib.file_digest(Path(path).open('rb'),'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--input',type=Path);p.add_argument('--image',default='physical-ai-harmonizer:826c199');p.add_argument('--max-frames',type=int);p.add_argument('--rig',type=Path);p.add_argument('--port',type=int,default=8765);p.add_argument('--comparison-dir',type=Path);p.add_argument('stage',choices=['setup','compare','evaluate','check','serve','benchmark','adaptive-benchmark']);a=p.parse_args()
    root=a.root.expanduser().resolve();root.mkdir(parents=True,exist_ok=True)
    if root.is_relative_to(HERE.parents[2]/'site/public'):raise ValueError('Keep checkpoints, runtime data and raw logs outside site/public')
    source=root/'deps/harmonizer';checkpoint=source/'models/diffusion_harmonizer.pkl';comparison=(a.comparison_dir or root/'comparison').resolve();lock=os.environ.get('GPU_LOCK','/tmp/rgb-reality-view.gpu.lock')
    if a.stage=='setup':
        if platform.system()!='Linux' or platform.machine() not in ['x86_64','AMD64']:raise ValueError('GPU setup requires Linux x86_64; inspect saved results and use the browser on other machines')
        uv=shutil.which('uv') or str(Path.home()/'.local/bin/uv')
        if not Path(uv).is_file():raise ValueError('Install uv first; see the GPU onboarding guide')
        for tool in ['git','docker','flock']:
            if not shutil.which(tool):raise ValueError(f'Install {tool} first; see the GPU onboarding guide')
        source.parent.mkdir(exist_ok=True)
        if not source.exists():run(['git','clone','https://github.com/NVIDIA/harmonizer.git',source]);run(['git','-C',source,'checkout',SOURCE_PIN])
        if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=SOURCE_PIN:raise ValueError('Dependency source differs; preserve it and select a fresh root')
        context=root/'docker-context'
        if not context.exists():
            context.mkdir();archive=tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git','-C',str(source),'archive','HEAD'])))
            for member in archive.getmembers():
                if member.issym() or member.islnk() or not (context/member.name).resolve().is_relative_to(context.resolve()):raise ValueError('Unexpected dependency archive member')
            archive.extractall(context,filter='data')
            dockerfile=context/'Dockerfile.cosmos';text=dockerfile.read_text();clone='RUN git clone --recursive --depth 1 https://github.com/nvidia-cosmos/cosmos-predict2.5.git /cosmos-predict2.5';assert clone in text
            text=text.replace(clone,clone+f' && cd /cosmos-predict2.5 && git fetch --depth 1 origin {DEPS_PIN} && git checkout --detach {DEPS_PIN} && git submodule update --init --recursive');dockerfile.write_text(text)
        run(['docker','build','--build-arg','BASE='+BASE,'-t',a.image,'-f',context/'Dockerfile.cosmos',context])
        # The only downloaded model artifact is the fully released Harmonizer
        # checkpoint. No gated Cosmos base weights or license acceptance API.
        code='from huggingface_hub import hf_hub_download;import sys;hf_hub_download("nvidia/Harmonizer","diffusion_harmonizer.pkl",revision="'+MODEL_PIN+'",local_dir=sys.argv[1])'
        run([uv,'run','--no-project','--with','huggingface-hub==0.36.0','python','-c',code,checkpoint.parent])
        if sha(checkpoint)!=MODEL_SHA:raise ValueError('Official checkpoint checksum mismatch')
        (root/'setup.json').write_text(json.dumps({'source_revision':SOURCE_PIN,'dependency_revision':DEPS_PIN,'base_image':BASE,'image_id':subprocess.check_output(['docker','image','inspect',a.image,'--format','{{.Id}}'],text=True).strip(),'model_revision':MODEL_PIN,'model_sha256':MODEL_SHA,'no_gated_base_checkpoint':True},indent=2)+'\n');return
    if not checkpoint.is_file() or sha(checkpoint)!=MODEL_SHA:raise ValueError('Run setup and verify the pinned public checkpoint first')
    if a.stage in ['compare','serve']:
        if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=SOURCE_PIN:raise ValueError('Use the pinned upstream source')
        run(['git','-C',source,'diff','--quiet','HEAD','--','src'])
    if a.stage=='check':
        for mode in ['independent','temporal']:
            folder=comparison/mode;data=json.loads((folder/'result.json').read_text());assert data['checkpoint_sha256']==MODEL_SHA and data['standalone_initialization']['all_learned_parameters_equal_released_tensors']
            for row in data['records']:
                file=(folder/row['output']).resolve();assert file.is_relative_to(folder) and sha(file)==row['output_sha256']
            if mode=='temporal':assert any(x['history_frames']==4 for x in data['records'])
        print('VERIFIED_REAL_TEMPORAL_RESULTS');return
    common=['docker','run','--rm','--user',f'{os.getuid()}:{os.getgid()}','-v',f'{root}:/data','-v',f'{source}:/work:ro','-v',f'{HERE}:/adapters:ro','-w','/work/src','-e','HOME=/tmp','-e','PYTHONPATH=/work/src:/adapters','-e','HF_HUB_OFFLINE=1','-e','TRANSFORMERS_OFFLINE=1']
    if a.stage=='serve':
        run(['flock',lock,*common,'--gpus','device=0','--network','host','--shm-size=8g','--entrypoint','python',a.image,'/adapters/service.py','--checkpoint','/work/models/diffusion_harmonizer.pkl','--components','/data/components','--record-root','/data/live-captures','--port',a.port]);return
    if a.input:a.input=a.input.expanduser().resolve()
    if not a.input or not a.input.is_dir():raise ValueError('Supply --input with ordered16:9 novel-view render frames')
    if not comparison.is_relative_to(root):raise ValueError('Keep comparison outputs inside the selected private runtime root')
    if a.stage=='adaptive-benchmark':
        if not a.rig or not a.rig.expanduser().is_file():raise ValueError('Supply --rig with the matching rig-orbit.json')
        target=comparison/'adaptive-benchmark'
        run(['flock',lock,*common,'--gpus','device=0','--network','none','--shm-size=8g','-v',f'{a.input}:/input:ro','-v',f'{a.rig.expanduser().resolve()}:/rig.json:ro','--entrypoint','python',a.image,'/adapters/benchmark_adaptive.py','--input','/input','--rig','/rig.json','--out','/data/'+str(target.relative_to(root)),'--checkpoint','/work/models/diffusion_harmonizer.pkl','--components','/data/components',*(['--max-frames',a.max_frames] if a.max_frames else [])]);return
    if a.stage=='benchmark':
        target=comparison/'speed-benchmark'
        run(['flock',lock,*common,'--gpus','device=0','--network','none','--shm-size=8g','-v',f'{a.input}:/input:ro','--entrypoint','python',a.image,'/adapters/benchmark_speed.py','--input','/input','--out','/data/'+str(target.relative_to(root)),'--checkpoint','/work/models/diffusion_harmonizer.pkl','--components','/data/components',*(['--max-frames',a.max_frames] if a.max_frames else [])]);return
    if a.stage=='compare':
        for mode in ['independent','temporal']:
            run(['flock',lock,*common,'--gpus','device=0','--network','none','--shm-size=8g','-v',f'{a.input}:/input:ro','--entrypoint','python',a.image,'/adapters/enhance.py','--input','/input','--out','/data/'+str((comparison/mode).relative_to(root)),'--checkpoint','/work/models/diffusion_harmonizer.pkl','--standalone-components','/data/components','--mode',mode,*(['--max-frames',a.max_frames] if a.max_frames else [])])
    elif a.stage=='evaluate':
        run([*common,'--network','none','-v',f'{a.input}:/input:ro','--entrypoint','python',a.image,'/adapters/evaluate.py','--input','/input','--independent','/data/'+str((comparison/'independent').relative_to(root)),'--temporal','/data/'+str((comparison/'temporal').relative_to(root)),'--out','/data/'+str((comparison/'evaluation.json').relative_to(root))])
if __name__=='__main__':main()
