"""Check permission-scoped model-only publication, timeline, array and video hashes."""
from pathlib import Path
import argparse,hashlib,json,runpy,subprocess
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
PACKAGE=REPO/'site/public/showcase/human-4d-dance'


def main(deep=False):
    read=lambda n:json.loads((PACKAGE/n).read_text())
    manifest=read('manifest.json');export=read('export.json');media=read('media.json')
    assert manifest['representation']=='native-conditional-4d'
    assert manifest['permission']['scope']=='Derived3D/4D results'
    assert manifest['permission']['source_footage_redistributed'] is False
    assert manifest['source']['youtube_id']=='rWS8uli1-m0' and not manifest['source'].get('url')
    assert manifest['source']['attribution_url']=='https://www.youtube.com/shorts/rWS8uli1-m0'
    assert manifest['duration']==31.9 and manifest['fps']==30 and len(manifest['segments'])==8
    assert not export['source_rgb_included'] and not export['source_audio_included']
    assert not any(PACKAGE.rglob('source.mp4'))
    check=runpy.run_path(str(HERE/'pipeline.py'))['check_package']
    result=check(PACKAGE,deep)
    assert all(r['hashes_verified'] and r['gaussians']<=400000 and r['native_numeric_max_position_error']<1e-4 for r in result['segments'])
    for segment in manifest['segments']:
        path=(PACKAGE/segment['root']).resolve();meta=json.loads((path/'meta.json').read_text())
        assert path.is_relative_to(PACKAGE) and meta['preview']['not_full_model']
        assert meta['preview']['retained_gaussians']<meta['preview']['original_gaussians']
    for row in media['media']:
        file=PACKAGE/row['file'];assert file.stat().st_size==row['bytes']
        assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256']
    files=[f for f in PACKAGE.rglob('*') if f.is_file()]
    assert max(f.stat().st_size for f in files)<100*1024**2
    print(f'PASS:31.9s/957 frames,8 reduced browser segments, retained-parameter parity, model-only media hashes and explicit YouTube citation; {sum(f.stat().st_size for f in files)/1024**2:.1f}MiB. Permission is maintainer-confirmed; not a general reuse license or unseen-view accuracy claim.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--deep',action='store_true');main(parser.parse_args().deep)
