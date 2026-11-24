"""Train matched-budget NuRec ablations and render untouched RGB test views.

Run make_inputs.py, prepare_ncore.py and infer_priors.py first. Large artifacts
and raw logs stay in --root, outside Git. Rendered comparisons use no Harmonizer.
"""
import argparse, copy, hashlib, json, os, re, subprocess, zipfile
from pathlib import Path

LAB=Path(__file__).resolve().parents[1]
IMAGE='nvcr.io/nvidia/nre/nre-ga:26.04@sha256:97f43e7130c5636ce3e80ea3184d97f56a87fdd989b05cce42230881dbdea284'


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def run(args,log):
    with log.open('w') as stream:subprocess.run([str(x) for x in args],check=True,stdout=stream,stderr=subprocess.STDOUT)


def heldout_paths(root,rig,dest):
    import numpy as np
    meta=json.loads((root/'all-cameras.json').read_text())
    held=set(json.loads((root/'split.json').read_text())['held_out_timestamp_us'])
    outputs=[]
    for camera in sorted({r['camera'] for r in meta['frames']}):
        rows=sorted([r for r in meta['frames'] if r['camera']==camera and r['timestamp_us'] in held],key=lambda r:r['timestamp_us'])
        key=next(k for k in rig['camera_calibrations'] if k.startswith(camera+'@'))
        cal=rig['camera_calibrations'][key];F=np.array(cal['T_sensor_rig'])
        poses=[np.array(r['camera_to_world'])@np.linalg.inv(F) for r in rows]
        times=[[r['timestamp_us'],r['timestamp_us']] for r in rows]
        trajectory=copy.deepcopy(rig['rig_trajectories'][0])
        trajectory.update(cameras_frame_timestamps_us={key:times},lidars_frame_timestamps_us={},
            cameras_frame_T_rig_worlds={key:[[M.tolist(),M.tolist()] for M in poses]},
            cameras_linear_start_frame_indices={key:0},lidars_linear_start_frame_indices={},
            T_rig_worlds=[M.tolist() for M in poses],T_rig_world_timestamps_us=[t[0] for t in times])
        d=copy.deepcopy(rig);d['rig_trajectories']=[trajectory];d['camera_calibrations']={key:cal};d['lidar_calibrations']={}
        path=dest/f'{camera}.json';path.write_text(json.dumps(d)+'\n')
        outputs.append({'camera':camera,'height':rows[0]['height'],'path':path,'images':[r['image'] for r in rows]})
    return outputs


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--variant',choices=['all','baseline','depth','depth-normal','depth-normal-soft'],default='all');p.add_argument('--steps',type=int,default=16000);p.add_argument('--max-gaussians',type=int,default=450000);p.add_argument('--seed-file',default='seed.ply');p.add_argument('--priors',default='priors-base');p.add_argument('--no-render',action='store_true');a=p.parse_args()
    root=a.root.resolve();cases=['baseline','depth','depth-normal'] if a.variant=='all' else [a.variant]
    assert a.steps>=1000 and a.max_gaussians>10000
    prior_report=json.loads((root/(a.priors+'.json')).read_text())
    for frame in prior_report['frames']:
        camera=Path(frame['image']).parts[0]
        assert sha(root/a.priors/camera/f"{frame['timestamp_us']}.npz")==frame['sha256'],'RGB prior integrity mismatch'
    lock=os.environ.get('GPU_LOCK','/tmp/rgb-reality-view.gpu.lock')
    docker=['flock',lock,'docker','run','--rm','--gpus','device=0','--network','none','--shm-size=8g','--user',f'{os.getuid()}:{os.getgid()}',
        '-v',f'{root}:/work','-v',f'{LAB}:/lab:ro','-e','NUREC_RGB_ROOT=/work','-e','HOME=/work/runtime-home']
    (root/'results').mkdir(exist_ok=True)
    for case in cases:
        weights={'distance':.1 if case!='baseline' else 0.,'normal':.03 if case=='depth-normal' else .005 if case=='depth-normal-soft' else 0.,'gaussian_flatten':.0005 if case=='depth-normal' else .00005 if case=='depth-normal-soft' else 0.}
        overrides=[f'out_dir=/work/train/{case}',f'dataset.n_samples_per_epoch={a.steps}',f'model.strategy.add.max_n_gaussians={a.max_gaussians}',*[f'loss.{k}.lambda_={v}' for k,v in weights.items()]]
        if a.seed_file!='seed.ply':
            overrides.append(f'model.layers.background.initialization.path=/work/{a.seed_file}')
        receipt=root/'results'/f'{case}.json';log=root/f'train-{case}.log'
        if receipt.exists():
            report=json.loads(receipt.read_text());assert report['overrides']==overrides,'Use a new output folder for different settings'
            artifact=root/report['artifact'];assert sha(artifact)==report['artifact_sha256']
            assert report['split_sha256']==sha(root/'split.json') and report['seed_sha256']==sha(root/a.seed_file)
            assert report['guidance_receipt_sha256']==sha(root/(a.priors+'.json'))
        else:
            command=[*docker,'-v',f'{LAB}/guidance/scene.yaml:/app/run.runfiles/_main/configs/geometry-guided.yaml:ro',
                '-e',f'RGB_GUIDANCE_CASE={case}','-e',f'RGB_PRIOR_FOLDER={a.priors}','-e',f'RGB_GUIDANCE_OVERRIDES={json.dumps(overrides)}',IMAGE,'run-script','/lab/guidance/train.py']
            print('GUIDANCE_CASE_START',case,flush=True);run(command,log)
            text=log.read_text();timing=re.findall(r'Train elapsed time:\s*([\d.]+) seconds',text)
            artifacts=list((root/'train'/case).rglob('last.usdz'))
            assert timing and len(artifacts)==1,'Completed training and a single final artifact are required'
            artifact=artifacts[0]
            active=[json.loads(line.split('RGB_GUIDANCE_NATIVE_LOSS ',1)[1]) for line in text.splitlines() if 'RGB_GUIDANCE_NATIVE_LOSS ' in line]
            assert {x['kind'] for x in active}==({'depth','normal'} if case.startswith('depth-normal') else {'depth'} if case=='depth' else set())
            report={'schema':1,'case':case,'steps':a.steps,'gaussian_limit':a.max_gaussians,'seed':42,'loss_weights':weights,'overrides':overrides,
                'training_seconds':float(timing[-1]),'artifact':artifact.relative_to(root).as_posix(),'artifact_sha256':sha(artifact),
                'split_sha256':sha(root/'split.json'),'seed_sha256':sha(root/a.seed_file),'guidance_receipt_sha256':sha(root/(a.priors+'.json')),
                'native_differentiable_losses':active,'uses_lidar':False,'uses_supplied_depth':False}
            receipt.write_text(json.dumps(report,indent=2)+'\n');print('GUIDANCE_CASE_TRAINED',case,report['training_seconds'],flush=True)
        if not a.no_render and json.loads((root/'split.json').read_text())['held_out_images']:
            target=root/'evaluation'/case;target.mkdir(parents=True,exist_ok=True)
            with zipfile.ZipFile(artifact) as archive:rig=json.loads(archive.read('rig_trajectories.json'))
            views=heldout_paths(root,rig,target)
            # Load a model once and render all six cameras together.
            combined=None
            for view in views:
                one=json.loads(view['path'].read_text())
                if combined is None:combined=one;continue
                combined['camera_calibrations'].update(one['camera_calibrations'])
                for key in ['cameras_frame_timestamps_us','cameras_frame_T_rig_worlds','cameras_linear_start_frame_indices']:
                    combined['rig_trajectories'][0][key].update(one['rig_trajectories'][0][key])
            path=target/'all-cameras.json';path.write_text(json.dumps(combined)+'\n')
            camera_args=[part for v in views for part in ['--camera-id',v['camera']]]
            render_args=['--artifact-path','/work/'+artifact.relative_to(root).as_posix(),'--output-dir',f'/work/evaluation/{case}',
                *camera_args,'--image-scale','1.0','--renderer','gsplat','--custom-rig-trajectory','/work/'+path.relative_to(root).as_posix(),
                '--no-replicate-training-views','--calib-source','training-rig-poses','--save-workers','2']
            run([*docker,'-e',f'RGB_RENDER_ARGS={json.dumps(render_args)}',IMAGE,'run-script','/lab/guidance/render.py'],target/'render.log')
            (target/'views.json').write_text(json.dumps([{k:v for k,v in view.items() if k!='path'} for view in views],indent=2)+'\n')
            print('GUIDANCE_CASE_RENDERED',case,flush=True)


if __name__=='__main__':main()
