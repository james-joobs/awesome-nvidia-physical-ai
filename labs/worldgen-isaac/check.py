"""Validate saved calibration, physical outcomes and media without CUDA or NumPy."""
import argparse,hashlib,json,math
from pathlib import Path


def check_run(folder):
    r=json.loads((folder/'result.json').read_text())
    assert r['status']=='complete' and r['isaacsim_version'].startswith('6.2')
    assert r['stage']['up_axis']=='Z' and r['stage']['meters_per_unit']==1
    assert r['samples'] and all(math.isfinite(v) for s in r['samples'] for pose in s['poses'].values() for values in pose for v in values)
    if r['scenario']=='probes':
        heights=[p[0][2] for p in r['final_poses'].values()]
        if r['no_floor'] and not r['raw_collider']:assert max(heights)<-1
        elif r['raw_collider']:assert all(.0<z<.20 for z in heights)
        else:assert all(abs(z-.05)<.002 for z in heights)
    else:
        path='/World/Robot/Chassis';position=r['final_poses'][path][0]
        assert all(.20<s['poses'][path][0][2]<.28 for s in r['samples'])
        assert r['stage']['render_mesh_collision'] is False and r['stage']['proxy_floor'] is True
        assert r['raycasts']['floor_left']['collider']=='/World/ProxyFloor'
        assert abs(r['raycasts']['crate']['position'][2]-.6)<1e-4
        if r['scenario']=='blocked':
            assert abs(position[0]+.5)<.025 and r['crate_contact_events']
            assert position[0]-r['samples'][0]['poses'][path][0][0]>.6
        else:
            assert r['reached_goal'] and math.hypot(position[0]-1.3,position[1])<.12
            assert min(s['poses'][path][0][1] for s in r['samples'])<-.8
            if r['scenario']=='detour':assert not r['crate_contact_events'],'The detour touched the crate'
            else:
                assert r['crate_contact_events']
                assert {'contact','reverse','detour'}=={sample['phase'] for sample in r['samples']}
    print(folder.name,r['scenario'],'physical outcome verified')
    return r


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path);a=p.parse_args()
    if a.run:check_run(a.run);return
    folder=Path(__file__).resolve().parent;root=folder.parents[1]
    record=json.loads((folder/'recorded.json').read_text())
    calibration=json.loads((folder/'assets/calibration.json').read_text())
    assert calibration['metric_scale'].startswith('assumed')
    assert abs(calibration['meters_per_worldgen_unit']*calibration['source_floor_plane']['offset']-1.5)<1e-6
    rows=calibration['source_to_isaac']['rotation_rows']
    for i in range(3):
        for j in range(3):assert abs(sum(a*b for a,b in zip(rows[i],rows[j]))-int(i==j))<1e-6
    assert calibration['floor_inlier_rms_m']<.025
    assert calibration['render_mesh']=={'stride':4,'vertices':80000,'triangles':158802,'collision_enabled':False,'small_uv_seam_gap':True}
    for case in record['runs']:check_run(folder/'evidence'/case)
    for rel,meta in record['files'].items():
        data=(root/rel).read_bytes();assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],rel
    print('Calibrated assets, contact tests, live robot runs and native-GUI media hashes verified.')


if __name__=='__main__':main()
