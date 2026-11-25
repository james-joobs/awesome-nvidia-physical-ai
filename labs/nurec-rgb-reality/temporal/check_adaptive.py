"""CPU checks for published progressive-rendering measurements and media."""
from pathlib import Path
import hashlib,json,math,runpy,sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
EVIDENCE=HERE.parent/'evidence/adaptive'


def main():
    read=lambda name:json.loads((EVIDENCE/name).read_text())
    validation=read('validation.json');assert validation['parameters_verified']
    assert validation['checkpoint_sha256']=='6e65e9ec33019a49f7f0d15f81f5e089c2527e131bd5339d6a14f9b3531db524'
    preview=validation['preview'];hq=validation['refinement']
    assert len(preview)==160 and len(hq)==20
    assert all(r['resolution']==[512,288] and math.isfinite(r['model_ms']) and r['model_ms']>0 for r in preview)
    assert all(r['history_frames']==4 for r in preview[4:])
    assert all(r['pixel_equal_fresh_hq_reference'] and r['rgb_sha256']==r['reference_rgb_sha256']
               and r['resolution']==[1024,576] and not r['hq_uses_preview_history']
               and r['model_calls']==2 and r['reused_reference_slots']==4 for r in hq)
    assert 24<sum(r['psnr_vs_hq_db'] for r in preview[4:])/156<25
    assert .87<sum(r['ssim_vs_hq'] for r in preview[4:])/156<.89
    sys.path.insert(0,str(HERE))
    try:summarize=runpy.run_path(str(HERE/'adaptive_stats.py'))['interaction_summary']
    finally:sys.path.pop(0)
    traces=read('interaction.json');assert traces['gpu_count']==1 and traces['idle_ms']==180
    runs=traces['runs'];assert {(r['language'],r['profile']) for r in runs}=={(l,p) for l in ['en','ko'] for p in ['exact','adaptive','native']}
    actual={}
    for record in runs:
        assert not record['errors']
        summary=summarize(record);assert summary==record['summary']
        actual[record['language'],record['profile']]=summary
        if record['profile']!='exact':
            assert all(s['redundant_idle_requests']==0 for s in summary['stops'])
            for row in record['rows']:
                assert not row['hq_uses_preview_history']
                expected=([512,288],'preview-512') if row['phase']=='preview' else ([1024,576],'hq')
                assert (row['resolution'],row['history_bank'])==expected
        if record['profile']=='native':
            assert summary['painted_ai_updates_while_moving']==0
            assert summary['browser_preview_fps_while_moving']>50
            moves=[e for e in record['events'] if e['kind']=='moving']
            assert not any(e['start_ms']<=r['input_view']['captured_at_ms']<e['end_ms'] for e in moves for r in record['rows'])
    for lang in ['en','ko']:
        old,new=actual[lang,'exact'],actual[lang,'adaptive']
        assert new['delivered_ai_fps_while_moving']>old['delivered_ai_fps_while_moving']*1.8
        assert new['moving_capture_to_paint_median_ms']<old['moving_capture_to_paint_median_ms']*.6
    smoke=read('portable-smoke.json');assert len(smoke['preview'])==12
    assert smoke['parameters_verified'] and all(r['pixel_equal_fresh_hq_reference'] for r in smoke['refinement'])
    media=read('media.json')['media'];assert len(media)==6
    for item in media:
        file=(REPO/item['file']).resolve();assert file.is_relative_to(REPO/'site/public/showcase')
        assert file.stat().st_size==item['bytes']<100*1024**2
        digest=hashlib.sha256(file.read_bytes()).hexdigest();assert digest==item['sha256']
        lang=file.name.split('.')[-2]
        assert hashlib.sha256((EVIDENCE/f"{item['alias']}.{lang}.mp4").read_bytes()).hexdigest()==digest
    print('PASS:160 real preview frames,20 stationary HQ pixel matches,6 actual move/rest passes, separate browser/AI FPS, no redundant idle calls, portable GPU run and6 video hashes.')


if __name__=='__main__':main()
