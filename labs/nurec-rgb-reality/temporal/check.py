"""Inspect published execution receipts and media integrity without a GPU."""
from pathlib import Path
import gzip
import hashlib
import json
import math
import struct

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / 'labs/nurec-rgb-reality/evidence/temporal'


def read(file):
    return json.loads(file.read_text())


def main():
    independent, temporal = [read(EVIDENCE / f'{mode}.json') for mode in ('independent', 'temporal')]
    assert independent['mode'] == 'independent' and temporal['mode'] == 'temporal'
    assert len(independent['records']) == len(temporal['records']) == 160
    assert independent['checkpoint_sha256'] == temporal['checkpoint_sha256']
    assert [r['input_sha256'] for r in independent['records']] == [r['input_sha256'] for r in temporal['records']]
    for report in (independent, temporal):
        assert report['internal_resolution'] == [1024, 576] and not report['uses_future_frames']
        init = report['standalone_initialization']
        assert init['all_learned_parameters_covered'] and init['all_learned_parameters_equal_released_tensors']
        assert init['parameter_counts'] == {'dit': 597536000, 'vae': 126892531}
        assert all(math.isfinite(r['model_seconds']) and r['model_seconds'] > 0 for r in report['records'])
    assert all(r['history_frames'] == 0 for r in independent['records'])
    assert [r['history_frames'] for r in temporal['records'][:5]] == [0, 0, 0, 0, 4]
    evaluation = read(EVIDENCE / 'evaluation.json')
    assert evaluation['frames'] == 160 and evaluation['contextual_pairs'] == 156
    assert evaluation['checkpoint_sha256'] == temporal['checkpoint_sha256']
    assert evaluation['summary']['temporal']['flow_warp_l1'] < evaluation['summary']['independent']['flow_warp_l1']
    portable = read(EVIDENCE / 'portable-validation.json')
    assert portable['setup']['no_gated_base_checkpoint']
    for mode, values in evaluation['summary'].items():
        for metric, value in values.items():
            assert math.isclose(portable['portable_cpu_evaluation']['summary'][mode][metric], value, rel_tol=1e-6, abs_tol=1e-8)
    for mode in ('independent', 'temporal'):
        smoke = portable['portable_wrapper_gpu_smoke'][mode]
        assert smoke['frames'] == 6 and smoke['all_learned_parameters_equal_released_tensors']
    assert portable['portable_wrapper_gpu_smoke']['temporal']['history_frames'] == [0, 0, 0, 0, 4, 4]
    browser = read(EVIDENCE / 'browser.json')
    assert {r['language'] for r in browser} == {'en', 'ko'}
    for report in browser:
        assert not report['errors'] and report['mobile']['width'] <= report['mobile']['viewport']
        assert any(e['action'] == 'small_mouse_orbit' and e['history_frames'] == 4 for e in report['events'])
        assert any(e['action'] == 'driver_view_resets_history' and e['history_reset'] for e in report['events'])
        assert any(e['action'] == 'independent_mode' and e['history_frames'] == 0 for e in report['events'])
        assert all(e['model_ms'] > 0 and e['round_trip_ms'] >= e['model_ms'] for e in report['events'])
    media = read(EVIDENCE / 'media.json')
    assert len(media['media']) == 4
    for item in media['media']:
        file = (REPO / item['file']).resolve()
        assert file.is_relative_to(REPO / 'site/public/showcase')
        assert file.stat().st_size == item['bytes'] < 100 * 1024**2
        assert hashlib.sha256(file.read_bytes()).hexdigest() == item['sha256']
    viewer = REPO / 'site/public/showcase/nurec-rgb-reality'
    assert 'enhancement_endpoint' not in read(viewer / 'cameras.json')
    variants = read(viewer / 'guidance.json')['variants']
    for variant in variants:
        file = viewer / variant['file']
        assert hashlib.sha256(file.read_bytes()).hexdigest() == variant['sha256']
        with gzip.open(file, 'rb') as stream:
            magic, version, count = struct.unpack('<III', stream.read(12))
        assert magic == 0x5053474e and version == 3 and count == variant['gaussians']
    support = read(viewer / 'support.json')
    assert sum(support['histogram'].values()) == 1200000 and support['geometry_opacity_unchanged']
    assert support['support_spz_sha256'] == next(v['sha256'] for v in variants if v['id'] == 'support')
    print('PASS: 160 matched frames, exact learned parameters, actual GPU interactions, four videos and model hashes. Integrity/execution only; not driving safety or unseen-view accuracy.')


if __name__ == '__main__':
    main()
