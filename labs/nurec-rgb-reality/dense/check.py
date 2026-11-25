"""Validate packaged scene provenance, dimensions and integrity without a GPU."""
import gzip,hashlib,json,struct
from pathlib import Path
import numpy as np
from PIL import Image

def main():
    repo=Path(__file__).resolve().parents[3];base=repo/'site/public/showcase/reality-joint-geometry';scene=json.loads((base/'scene.json').read_text());root=base/'dense';dense=json.loads((root/'dense.json').read_text())
    assert dense['schema']==3 and dense['source_rgb_only'] and not dense['worldlatent_executed']
    record=dense['static_gaussians'];data=(root/record['file']).read_bytes()
    assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256']
    magic,version,count=struct.unpack('<III',gzip.decompress(data)[:12]);assert magic==0x5053474e and version==3
    report=dense['decomposition'];assert count==report['retained_gaussians'] and count+report['removed_gaussians']==report['input_gaussians']
    mask=dense['mask'];raw=gzip.decompress((root/mask['file']).read_bytes());assert len(raw)==mask['decoded_bytes']==int(np.prod(mask['shape'])) and hashlib.sha256(raw).hexdigest()==mask['sha256']
    values=np.frombuffer(raw,'u1');assert set(np.unique(values))<={0,1} and 0<values.mean()<.5
    model=next(m for m in scene['models'] if m['id']=='calibrated');assert mask['shape']==[102,model['grid'][1],model['grid'][0]]
    for m in dense['models']:
        assert m['rgb_kind']=='generated' and len(m['rgb'])==17 and m['latent']['is_worldvae'] is False
        assert m['latent']['shape']==[1,5,56,60,90] and m['run']['task']=='prediction'
        assert m['run']['lidar_used'] is False and m['run']['camera_ground_truth_used'] is False
        blob=(base/m['depth_file']).read_bytes();assert len(blob)==m['depth_bytes']==17*np.prod(m['grid'])*2
        assert hashlib.sha256(blob).hexdigest()==m['depth_sha256']
        for path in m['rgb']:assert Image.open(base/path).size==(720,480)
        C=np.array(m['camera_to_world']);assert np.isfinite(C).all();np.testing.assert_allclose(C[:,:3,:3].transpose(0,2,1)@C[:,:3,:3],np.repeat(np.eye(3)[None],17,axis=0),atol=1e-3)
        assert (np.linalg.det(C[:,:3,:3])>.99).all()
        assert m['inference']['peak_allocated_gib']<32
    print('DENSE_SCENE_OK',count,'background Gaussians;',report['removed_gaussians'],'removed; 102 foreground masks; 2 real joint-diffusion runs')

if __name__=='__main__':main()
