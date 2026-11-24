"""Render the original and production models on exactly the same novel paths.

This visual comparison changes initialization, steps and model capacity as well
as guidance. It is separate from evaluate.py's matched-budget held-out scores.
"""
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation, Slerp
from run_experiment import IMAGE, LAB


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);a=p.parse_args();root=a.root.resolve();reference=a.reference.resolve()
    subprocess.run([sys.executable,str(LAB/'make_views.py'),'--root',str(root)],check=True)
    # More native camera samples make the comparison recording smooth. These
    # are scripted novel viewpoints, not additional observed photographs.
    for view in ['quarter','orbit']:
        path=root/f'rig-{view}.json';rig=json.loads(path.read_text());trajectory=rig['rig_trajectories'][0]
        sensor=next(iter(trajectory['cameras_frame_T_rig_worlds']));matrices=np.array([pair[0] for pair in trajectory['cameras_frame_T_rig_worlds'][sensor]])
        if view=='orbit':matrices=np.concatenate([matrices,matrices[:1]])
        grid=np.arange(len(matrices));samples=np.linspace(0,len(matrices)-1,160,endpoint=view!='orbit')
        rotations=Slerp(grid,Rotation.from_matrix(matrices[:,:3,:3]))(samples).as_matrix();positions=np.stack([np.interp(samples,grid,matrices[:,axis,3]) for axis in range(3)],axis=-1)
        poses=np.repeat(np.eye(4)[None],len(samples),axis=0);poses[:,:3,:3]=rotations;poses[:,:3,3]=positions
        timestamps=np.linspace(1000000,8800000,len(samples)).astype(int).tolist()
        trajectory['cameras_frame_T_rig_worlds']={sensor:[[M.tolist(),M.tolist()] for M in poses]}
        trajectory['cameras_frame_timestamps_us']={sensor:[[t,t] for t in timestamps]}
        trajectory['T_rig_worlds']=[M.tolist() for M in poses];trajectory['T_rig_world_timestamps_us']=timestamps
        path.write_text(json.dumps(rig)+'\n')
    new=json.loads((root/'results/depth.json').read_text());old=json.loads((reference/'nurec-result.json').read_text());records=[]
    for case,report,prefix in [('original',old,'/reference'),('guided',new,'/work')]:
        artifact=(reference if case=='original' else root)/report['artifact']
        assert hashlib.file_digest(artifact.open('rb'),'sha256').hexdigest()==report['artifact_sha256']
        for view in ['quarter','orbit']:
            args=['--artifact-path',prefix+'/'+report['artifact'],'--output-dir',f'/work/preview/{case}-{view}',
                '--camera-id','front_camera','--image-scale','1.0','--renderer','gsplat','--custom-rig-trajectory',f'/work/rig-{view}.json',
                '--no-replicate-training-views','--calib-source','training-rig-poses','--save-workers','2']
            command=['flock',os.environ.get('GPU_LOCK','/tmp/rgb-reality-view.gpu.lock'),'docker','run','--rm','--gpus','device=0','--network','none',
                '--user',f'{os.getuid()}:{os.getgid()}','-v',f'{root}:/work','-v',f'{reference}:/reference:ro','-v',f'{LAB}:/lab:ro',
                '-e','HOME=/work/runtime-home','-e',f'RGB_RENDER_ARGS={json.dumps(args)}',IMAGE,'run-script','/lab/guidance/render.py']
            subprocess.run(command,check=True)
            images=sorted((root/'preview'/f'{case}-{view}').rglob('*.png'))
            records.append({'case':case,'view':view,'artifact_sha256':report['artifact_sha256'],
                'camera_path_sha256':hashlib.file_digest((root/f'rig-{view}.json').open('rb'),'sha256').hexdigest(),
                'frames':len(images),'rgb_sha256':[hashlib.file_digest(f.open('rb'),'sha256').hexdigest() for f in images]})
    (root/'preview/paired-renders.json').write_text(json.dumps({'schema':1,'native_renderer':'NuRec gsplat','enhancement':False,
        'scope':'Same camera path. Production model also changes seed density, steps and capacity; not a loss-only or held-out comparison.','renders':records},indent=2)+'\n')


if __name__=='__main__':main()
