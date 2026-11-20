"""Validate recorded sensor navigation without NumPy, CUDA or Isaac Sim."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def check_run(folder):
    r = json.loads((folder / 'result.json').read_text())
    scans = json.loads((folder / 'scans.json').read_text())
    assert r['status'] == 'complete' and r['isaacsim_version'].startswith('6.2')
    assert r['stage']['meters_per_unit'] == 1 and r['stage']['up_axis'] == 'Z'
    assert not r['stage']['render_mesh_collision'] and r['stage']['proxy_floor']
    assert r['navigation']['obstacle_transforms_as_input'] is False
    samples = r['samples']
    path = '/World/Robot/Chassis'
    positions = [s['poses'][path][0] for s in samples]
    assert all(all(math.isfinite(v) for v in p) and .20 < p[2] < .28 for p in positions)
    assert all(abs(p[0]) < 2.1 and abs(p[1]) < 1.6 for p in positions)
    assert r['sensor']['scan_frames'] == len(scans)
    for previous, current in zip(scans, scans[1:]):
        assert current['sensor_time_s'] > previous['sensor_time_s']
        assert abs(current['sim_time_s'] - previous['sim_time_s'] - .1) < 1e-5
    for frame in scans:
        assert len(frame['depths_m']) == len(frame['hit_positions_world']) == 180
        assert all(math.isfinite(v) and .05 <= v <= 2.50001 for v in frame['depths_m'])
        assert all(len(p) == 3 and all(math.isfinite(v) for v in p) for p in frame['hit_positions_world'])
    final = r['final_poses'][path][0]
    if r['sensor_off']:
        assert not scans and not r['reached_goal']
        assert max(math.dist(p[:2], positions[0][:2]) for p in positions) < .01
        assert all(s['command'] == [0., 0.] for s in samples)
    elif r['scenario'] == 'sensor':
        assert len(scans) > 30 and r['reached_goal'] and not r['crate_contact_events']
        assert math.dist(final[:2], (1.3, 0)) < .13
        assert min(scans[0]['depths_m']) < 1.1
        if r['layout'] == 'lower':
            assert max(p[1] for p in positions) > .8 and min(p[1] for p in positions) > -.2
        else:
            assert min(p[1] for p in positions) < -.8
    else:
        assert r['layout'] == 'lower' and not r['reached_goal'] and r['crate_contact_events']
        assert -.6 < final[0] < -.4 and final[1] < -.6
    print(folder.name, r['scenario'], r['layout'], 'verified')
    return r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path)
    args = parser.parse_args()
    if args.run:
        check_run(args.run)
        return
    folder = Path(__file__).resolve().parent
    record = json.loads((folder / 'recorded.json').read_text())
    for case in record['runs']:
        check_run(folder / 'evidence' / case)
    root = folder.parents[1]
    for name, expected in record['files'].items():
        data = (root / name).read_bytes()
        assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256'], name
    print('Actual scans, route adaptation, contacts, sensor-off stop and media verified.')


if __name__ == '__main__':
    main()
