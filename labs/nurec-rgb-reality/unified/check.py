"""Check saved RGB-D viewer receipts and buffers without a GPU."""
import hashlib,json
from pathlib import Path
import numpy as np


def main():
    repo=Path(__file__).resolve().parents[3];root=repo/'site/public/showcase/reality-joint-geometry'
    scene=json.loads((root/'scene.json').read_text());assert len(scene['frames'])==17
    assert scene['reference_is_ground_truth'] is False
    for m in scene['models']:
        data=(root/m['depth_file']).read_bytes();assert len(data)==m['depth_bytes']
        assert hashlib.sha256(data).hexdigest()==m['depth_sha256']
        w,h=m['grid'];q=np.frombuffer(data,dtype='<u2').reshape(-1,h,w)
        assert len(q)==17*m['views_per_frame']==len(m['rgb'])
        assert len(m['camera_to_world'])==len(q)==len(m['intrinsics'])
        assert np.isfinite(m['camera_to_world']).all() and np.isfinite(m['intrinsics']).all()
        for C in np.array(m['camera_to_world']):
            np.testing.assert_allclose(C[:3,:3].T@C[:3,:3],np.eye(3),atol=1e-3)
            assert np.linalg.det(C[:3,:3])>.99
        assert m['alignment']['reference_is_ground_truth'] is False
        assert all((root/x).is_file() for x in m['rgb'])
        assert m['inference']['inference_seconds']>0 and m['inference']['peak_allocated_gib']<32
        assert all(v>0 for v in np.array(m['intrinsics'])[:,[0,1],[0,1]].flat)
        print(m['id'],len(q),'RGB views',len(data),'depth bytes; finite poses and buffer checksum verified')
    print('Saved outputs checked. This is integrity validation, not ground-truth depth accuracy.')


if __name__=='__main__':main()
