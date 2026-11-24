"""Export a completed guided NuRec model through its native export command."""
import argparse, gzip, hashlib, json, os, struct, subprocess, zipfile
from pathlib import Path
from run_experiment import IMAGE, LAB


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--variant',default='depth');a=p.parse_args();root=a.root.resolve()
    receipt=json.loads((root/'results'/f'{a.variant}.json').read_text());artifact=root/receipt['artifact']
    assert hashlib.file_digest(artifact.open('rb'),'sha256').hexdigest()==receipt['artifact_sha256']
    with zipfile.ZipFile(artifact) as archive:
        (root/'resolved-export.yaml').write_bytes(archive.read('parsed_config.yaml'))
        (root/'training-rig.json').write_bytes(archive.read('rig_trajectories.json'))
    command=['flock',os.environ.get('GPU_LOCK','/tmp/rgb-reality-view.gpu.lock'),'docker','run','--rm','--gpus','device=0','--network','none',
        '--user',f'{os.getuid()}:{os.getgid()}','-v',f'{root}:/work','-v',f'{LAB}:/lab:ro','-e','HOME=/work/runtime-home',
        '-e','RGB_EXPORT_ARGS='+json.dumps(['--config-name','resolved-guided.yaml','--checkpoint-name','last.ckpt','--output-dir','/work/gaussians']),
        '-v',f'{root}/resolved-export.yaml:/app/run.runfiles/_main/configs/resolved-guided.yaml:ro',IMAGE,
        'run-script','/lab/guidance/export_native.py']
    subprocess.run(command,check=True)
    output=root/'guided.spz'
    subprocess.run(['npm','exec','--yes','--package=@playcanvas/splat-transform@3.12.0','--','splat-transform','-w',
        str(root/'gaussians/background/model.ply'),'--filter-harmonics','1',str(output),'--spz-version','3'],check=True)
    with gzip.open(output,'rb') as f:magic,version,count=struct.unpack('<III',f.read(12))
    assert magic==0x5053474e and version==3 and count>10000
    (root/'exported.json').write_text(json.dumps({'schema':1,'case':a.variant,'gaussians':count,'file':'guided.spz',
        'bytes':output.stat().st_size,'sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),
        'artifact_sha256':receipt['artifact_sha256'],'source':'NuRec official export-gaussian-plys output; degree-1 SPZ browser conversion',
        'browser_renderer':'Spark / Three.js; differs from native NuRec rendering'},indent=2)+'\n')
    print('GUIDED_SPZ_EXPORTED',count,flush=True)


if __name__=='__main__':main()
