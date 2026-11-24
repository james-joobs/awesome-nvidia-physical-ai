"""CPU integrity checks for the published one-GPU optimization experiment."""
from pathlib import Path
import hashlib,json,math,runpy

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
EVIDENCE=HERE.parent/'evidence/speed'

def main():
    read=lambda name:json.loads((EVIDENCE/name).read_text())
    data=read('benchmark.json');profiles=data['profiles']
    assert data['resolution']==[1024,576] and data['precision']=='bfloat16' and data['previous_outputs']==4
    assert data['learned_parameters']['all_learned_parameters_equal_released_tensors']
    baseline=profiles['baseline']['records']
    for name,profile in profiles.items():
        assert len(profile['records'])==160
        assert [r['input_sha256'] for r in profile['records']]==[r['input_sha256'] for r in baseline]
        assert all(math.isfinite(r['model_ms']) and r['model_ms']>0 for r in profile['records'])
    assert [r['rgb_sha256'] for r in profiles['exact']['records']]==[r['rgb_sha256'] for r in baseline]
    assert profiles['exact']['fidelity']['all_frames_pixel_equal']
    assert profiles['exact']['fidelity']['mean_ssim']==1
    assert profiles['exact']['model_median_ms']<profiles['baseline']['model_median_ms']
    assert profiles['exact']['shared_flow_warp_l1']==profiles['baseline']['shared_flow_warp_l1']
    parity=read('service-parity.json');assert parity['pixel_equal']
    assert [r['rgb_sha256'] for r in parity['runs']['baseline']]==[r['rgb_sha256'] for r in parity['runs']['exact']]
    assert parity['runs']['exact'][-1]['history_frames']==4
    summarize=runpy.run_path(str(HERE/'stats.py'))['interaction_summary']
    runs=read('interaction.json')['runs'];assert {(r['language'],r['profile']) for r in runs}=={(l,p) for l in ['en','ko'] for p in ['baseline','exact']}
    actual={}
    for record in runs:
        assert not record['errors']
        summary=summarize(record)
        assert summary==record['summary']
        assert summary['native_presented_fps']>30
        assert len({tuple(r['input_view']['camera']) for r in record['rows']})>8
        actual[record['language'],record['profile']]=summary
    for lang in ['en','ko']:
        old,new=actual[lang,'baseline'],actual[lang,'exact']
        assert new['delivered_ai_fps']>old['delivered_ai_fps']
        assert new['temporal_capture_to_paint_median_ms']<old['temporal_capture_to_paint_median_ms']
    media=read('media.json')['media'];assert len(media)==4
    for item in media:
        file=(REPO/item['file']).resolve();assert file.is_relative_to(REPO/'site/public/showcase')
        assert file.stat().st_size==item['bytes']<100*1024**2
        assert hashlib.sha256(file.read_bytes()).hexdigest()==item['sha256']
        alias='interaction' if 'speed-live.' in file.name else 'quality'
        lang=file.name.split('.')[-2]
        assert hashlib.sha256((EVIDENCE/f'{alias}.{lang}.mp4').read_bytes()).hexdigest()==item['sha256']
    smoke=read('portable-smoke.json');assert smoke['frames']==12 and smoke['exact_pixel_equal']
    print('PASS: 160-frame pixel equality, GPU/HTTP-cache parity, four real mouse passes, separate FPS/latency, portable runner and four video hashes. Fidelity/execution only; no driving-safety or unseen-view claim.')

if __name__=='__main__':main()
