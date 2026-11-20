"""Inspect published WorldGen evidence with Python's standard library; no GPU."""
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct


def main():
    root=Path(__file__).resolve().parents[2]
    folder=root/'labs/worldgen-scenes'
    record=json.loads((folder/'recorded.json').read_text())
    for name,digest in record['implementation_sha256'].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest,name
    assert {row['mode'] for row in record['cases']}=={'t2s','i2s'}
    assert len(record['cases'])==3
    for case in record['cases']:
        evidence=folder/'evidence'/case['id']
        result=json.loads((evidence/'result.json').read_text())
        audit=json.loads((evidence/'geometry-audit.json').read_text())
        cameras=json.loads((evidence/'cameras.json').read_text())
        assert result['status']=='success' and result['resolution']==[1600,800]
        assert result['gaussians']['gaussians']==1_280_000 and result['gaussians']['all_finite']
        assert result['distance']['shape']==[800,1600] and result['distance']['max']==20
        assert audit['distance_finite'] and audit['distance_positive'] and audit['finite_ply_fields']
        assert all(abs(v-1)<1e-3 for v in audit['quaternion_norm_range'])
        for sample in audit['samples']:
            assert math.isclose(sum(v*v for v in sample['ray']),1,abs_tol=1e-5)
            assert max(abs(x-r*sample['distance']) for x,r in zip(sample['xyz'],sample['ray']))<1e-4
        assert len(cameras['frames'])==480 and cameras['fps']==24
        centers=[f['center'] for f in cameras['frames']]
        assert max(c[0] for c in centers)-min(c[0] for c in centers)>.39
        for frame in cameras['frames']:
            # W2C must map the documented optical center back to the origin.
            for row in frame['world_to_camera'][:3]:
                assert abs(sum(row[j]*frame['center'][j] for j in range(3))+row[3])<1e-5
        assert hashlib.sha256((evidence/'cameras.json').read_bytes()).hexdigest()==case['render']['cameras_sha256']
        for name,meta in case['published'].items():
            data=(root/'site/public/showcase'/name).read_bytes()
            assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],name
        spz=gzip.decompress((root/'site/public/showcase'/case['web_preview']['file']).read_bytes())
        magic,version,count,degree,_,_,_=struct.unpack_from('<IIIBBBB',spz)
        assert magic==int.from_bytes(b'NGSP','little') and version==3 and count==320_000 and degree==0
        assert len(spz)==16+count*20
        assert .5<case['render']['mean_alpha']<=1
        if case['mode']=='i2s':
            assert result['conditioning']['max_preserved_rgb_error']==0
            assert .1<result['conditioning']['observed_panorama_fraction']<.3
            assert hashlib.sha256((folder/'evidence/input.png').read_bytes()).hexdigest()==result['conditioning']['source_sha256']
    print('WorldGen: 3 generated scenes, 1,440 translated camera poses, 3 MP4s and 3 compressed previews verified.')


if __name__=='__main__': main()
