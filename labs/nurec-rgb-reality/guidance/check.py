"""CPU-only checks of the saved guidance experiment and browser model exports."""
import argparse, gzip, hashlib, json, math, struct, subprocess
from pathlib import Path
import numpy as np
from PIL import Image

LAB=Path(__file__).resolve().parents[1];REPO=LAB.parents[1];EVIDENCE=LAB/'evidence/guidance'


def read(name):return json.loads((EVIDENCE/name).read_text())


def main(decode=False):
    comparison=read('comparison.json');runs=read('matched-runs.json');cases={r['case']:r for r in comparison['cases']}
    assert {'baseline','depth','depth-normal','depth-normal-soft'}<=cases.keys()
    assert comparison['split']['train_images']==138 and comparison['split']['held_out_images']==24
    assert len({r['seed_sha256'] for r in runs.values()})==len({r['split_sha256'] for r in runs.values()})==1
    assert len({r['guidance_receipt_sha256'] for r in runs.values()})==1
    reference_hashes=None
    for name,case in cases.items():
        assert case['training_steps']==16000 and case['gaussian_limit']==450000 and case['views']==len(case['frames'])==24
        assert runs[name]['seed']==42 and not runs[name]['uses_lidar'] and not runs[name]['uses_supplied_depth']
        active=runs[name]['native_differentiable_losses'];expected={'depth','normal'} if name.startswith('depth-normal') else {'depth'} if name=='depth' else set()
        assert {r['kind'] for r in active}==expected
        assert all(r['differentiable'] and r['finite'] and r['valid_pixels']>0 for r in active)
        hashes={r['image']:r['reference_sha256'] for r in case['frames']}
        if reference_hashes is None:reference_hashes=hashes
        assert hashes==reference_hashes
        for metric,mean in case['mean_per_image'].items():
            values=[r[metric] for r in case['frames']];assert all(math.isfinite(v) for v in values)
            assert abs(sum(values)/len(values)-mean)<1e-10
    priors=read('priors-summary.json');assert priors['model']=='depth-anything/DA3-BASE' and priors['model_license']=='Apache-2.0'
    assert priors['images']==138 and priors['held_out_images_used']==0 and not priors['uses_lidar']
    sample=read('input-output-sample.json');assert sample['ray_distance_relative_units']>sample['z_depth_relative_units']>0
    assert abs(np.linalg.norm(sample['world_normal'])-1)<1e-5
    published=read('sample-files.json');reference=EVIDENCE/published['reference']['file'];truth=np.asarray(Image.open(reference).convert('RGB'),float)/255
    assert hashlib.sha256(reference.read_bytes()).hexdigest()==published['reference']['sha256']
    for name,row in published['predictions'].items():
        path=EVIDENCE/row['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        frame=next(r for r in cases[name]['frames'] if r['image']==published['image'])
        assert row['sha256']==frame['native_render_sha256']
        prediction=np.asarray(Image.open(path).convert('RGB'),float)/255;assert prediction.shape==truth.shape
        psnr=-10*math.log10(float(np.mean((truth-prediction)**2)));assert abs(psnr-frame['psnr_db'])<1e-8
    production=read('production-model.json');assert production['split']['production_fit'] and production['split']['train_images']==162
    assert production['split']['held_out_images']==0 and production['training']['steps']==32000
    assert production['seed']['normal_and_photometric_checks'] and not production['seed']['uses_lidar']
    web=REPO/'site/public/showcase/nurec-rgb-reality';manifest=json.loads((web/'guidance.json').read_text())
    assert manifest['default']=='guided' and len({v['id'] for v in manifest['variants']})==len(manifest['variants'])
    for variant in manifest['variants']:
        path=web/variant['file'];assert path.resolve().is_relative_to(web.resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==variant['sha256']
        with gzip.open(path,'rb') as f:magic,version,count=struct.unpack('<III',f.read(12))
        assert magic==0x5053474e and version==3 and count==variant['gaussians']
    assert next(v for v in manifest['variants'] if v['id']=='guided')['sha256']==production['export']['sha256']
    smoke=read('final-source-smoke.json');assert smoke['completed'] and smoke['training_steps']==4
    assert {p['kind'] for p in smoke['native_differentiable_losses']}=={'depth','normal'}
    browsers=read('browser-check.json')
    assert {(r['language'],r['mobile']) for r in browsers}=={('en',False),('ko',False),('en',True),('ko',True)}
    for row in browsers:
        assert not row['errors'] and not row['failed'] and row['gaussians']==1200000
        assert set(row['same_camera_model_switches'])=={'guided','original','matched-rgb','matched-depth'}
        assert row['actual_pointer'] and row['inline_video']['inline']
    fps=read('browser-fps.json');assert len(fps['results'])==6
    assert all(r['gaussians']==1200000 and r['fps']>0 and not r['errors'] and not r['context_lost'] for r in fps['results'])
    for lang in ['en','ko']:
        trace=read(f'interaction.{lang}.json');events={v['action']:v['state'] for v in trace['events']}
        assert not trace['errors'] and events['original-driver']['gaussians']==450000 and events['guided-driver']['gaussians']==1200000
        assert np.allclose(events['original-driver']['camera'],events['guided-driver']['camera'],atol=1e-6)
        assert events['finished']['frame']!=events['guided-path-playback']['frame']
        for local,published in [('native-comparison','nurec-guidance'),('interaction','nurec-guided-interaction')]:
            movie=EVIDENCE/f'{local}.{lang}.mp4';alias=web.parent/f'{published}.{lang}.mp4'
            assert hashlib.sha256(movie.read_bytes()).hexdigest()==hashlib.sha256(alias.read_bytes()).hexdigest()
            if decode:subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True)
    for name,expected in read('artifacts.json')['files'].items():
        path=REPO/name;assert path.resolve().is_relative_to(REPO.resolve())
        assert path.stat().st_size==expected['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==expected['sha256']
    print('Verified matched RGB comparisons, native differentiable geometry losses, actual pixel PSNR, and guided SPZ provenance. No CUDA required.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--decode-video',action='store_true');a=p.parse_args();main(a.decode_video)
