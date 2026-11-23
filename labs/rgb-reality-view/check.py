"""Check published RGB provenance, model geometry and actual browser interactions.

CPU only, standard library. --decode-video additionally needs FFmpeg on PATH.
This checks integrity and observed execution, not autonomous-driving accuracy.
"""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

LAB = Path(__file__).resolve().parent
REPO = LAB.parents[1]

def read(name):
    return json.loads((LAB / name).read_text())

def matrix_ok(matrix):
    assert len(matrix) == 3 and all(len(row) == 3 for row in matrix)
    assert all(math.isfinite(x) for row in matrix for x in row)
    for i in range(3):
        for j in range(3):
            assert abs(sum(matrix[k][i] * matrix[k][j] for k in range(3)) - (i == j)) < 1e-6
    det = sum(matrix[0][i] * (matrix[1][(i+1)%3] * matrix[2][(i+2)%3] - matrix[1][(i+2)%3] * matrix[2][(i+1)%3]) for i in range(3))
    assert abs(det - 1) < 1e-6

def main(decode=False):
    report = read('recorded.json')
    assert report['pipeline']['inputs'] == ['RGB pixels']
    manifest = read('evidence/input-manifest.json')
    assert len(manifest['images']) == 162
    assert manifest['external_sensor_inputs'] == []
    assert not any(manifest[k] for k in ['supplied_camera_poses', 'supplied_intrinsics', 'supplied_depth', 'supplied_ground_plane'])
    assert hashlib.sha256((LAB / 'evidence/input-manifest.json').read_bytes()).hexdigest() == report['training']['input_manifest_sha256']
    download = read('evidence/download-result.json')
    assert download['downloaded_modalities'] == ['RGB JPEG'] and len(download['files']) == 162
    assert all(Path(row['file']).suffix == '.jpg' for row in download['files'])
    assert {row['file'] for row in download['files']} == {row['image'] for row in manifest['images']}
    sfm = read('evidence/sfm-result.json')
    assert sfm['registered_images'] == sfm['input_images'] == 162
    assert sfm['sparse_points'] > 20000 and sfm['mean_reprojection_error_px'] < 2
    assert sfm['selected_model'] == 'sfm-selected'
    assert report['training']['training_steps'] == 16000
    assert report['training']['training_loop_seconds'] > 0 and report['training']['gpu_count'] == 1
    scene = REPO / 'site/public/showcase/rgb-reality-view'
    with gzip.open(scene / 'road.spz', 'rb') as f:
        header = f.read(16)
    magic, version, count = struct.unpack('<III', header[:12])
    assert magic == 0x5053474E and version == 3 and count == report['viewer']['gaussians'] == 400000
    assert header[12] == 1  # retained spherical-harmonics degree
    car = (scene / 'volvo-s90.glb').read_bytes()
    assert car[:4] == b'glTF' and struct.unpack('<I', car[4:8])[0] == 2
    assert struct.unpack('<I', car[8:12])[0] == len(car)
    geometry = json.loads((scene / 'cameras.json').read_text())
    assert len(geometry['frames']) == 27 and geometry['road_plane_inliers'] >= 25
    assert 'RGB' in geometry['road_plane_source'] and 'not measured meters' in geometry['units']
    T = geometry['world_to_viewer']
    assert len(T) == 4 and T[3] == [0, 0, 0, 1]
    scale = math.sqrt(sum(T[0][j]**2 for j in range(3)))
    assert scale > 0
    matrix_ok([[T[i][j] / scale for j in range(3)] for i in range(3)])
    last = -1
    for frame in geometry['frames']:
        assert frame['time_seconds'] > last
        last = frame['time_seconds']
        matrix_ok(frame['camera_rotation_opencv'])
        assert frame['K'][0][0] > 0 and frame['K'][1][1] > 0
        assert all(math.isfinite(x) for x in frame['camera_position'] + frame['ground_position'])
    for lang in ['en', 'ko']:
        trace = read(f'evidence/interaction.{lang}.json')
        assert trace['errors'] == [] and len(trace['events']) == 9
        events = {e['action']: e for e in trace['events']}
        assert all(e['gaussians'] == count for e in events.values())
        assert math.dist(events['initial']['camera'], events['orbit_first_half']['camera']) > .1
        assert events['path_replay']['frame'] != events['initial']['frame']
        assert events['driver']['view'] == 'driver' and events['side']['view'] == 'side'
    for name, expected in report['files'].items():
        path = REPO / name
        assert path.resolve().is_relative_to(REPO.resolve())
        assert path.stat().st_size == expected['bytes'], name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256'], name
        if decode and path.suffix == '.mp4':
            subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'null', '-'], check=True)
    import runpy
    runpy.run_path(str(LAB/'check_perception.py'))['main'](decode=decode)
    print('Verified 162 RGB-only inputs, estimated cameras, 400k Gaussians, 27 poses, bilingual mouse traces and artifact hashes.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--decode-video', action='store_true')
    main(parser.parse_args().decode_video)
