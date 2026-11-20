"""Check actual actor motion, measured standstill and route changes without GPU."""
import argparse,hashlib,json,math,runpy
from pathlib import Path

ROBOT='/World/Robot/Chassis'
MOVER='/World/MovingObstacle'


def distance_to_box(point, center, size):
    return math.hypot(*[max(abs(point[i]-center[i])-size[i]/2,0) for i in (0,1)])


def metrics(result):
    samples=result['samples'];size=result['moving_actor']['size']
    clearance=min(distance_to_box(s['poses'][ROBOT][0],s['poses'][MOVER][0],size)-.36 for s in samples)
    error=max(math.dist(s['poses'][MOVER][0],s['obstacle_target_xyz']) for s in samples)
    display=max(math.dist(s['poses'][MOVER][0],s['render_position_xyz']) for s in samples)
    return {'minimum_mover_clearance_bound_m':clearance,'max_actor_target_error_m':error,'max_physics_display_error_m':display}


def check_run(folder):
    r=json.loads((folder/'result.json').read_text());scans=json.loads((folder/'scans.json').read_text())
    assert r['status']=='complete' and r['isaacsim_version'].startswith('6.2')
    assert r['moving_actor']['schedule_passed_to_controller'] is False
    assert r['navigation']['obstacle_transforms_as_input'] is False
    assert r['stage']['meters_per_unit']==1 and r['stage']['up_axis']=='Z'
    assert not r['stage']['render_mesh_collision'] and r['stage']['proxy_floor']
    samples=r['samples'];positions=[s['poses'][ROBOT][0] for s in samples]
    assert all(.20<p[2]<.28 and abs(p[0])<2.1 and abs(p[1])<1.6 for p in positions)
    assert not r['crate_contact_events'],'Unexpected robot-obstacle contact'
    m=metrics(r);assert m['max_actor_target_error_m']<.002
    assert m['max_physics_display_error_m']<.002
    assert m['minimum_mover_clearance_bound_m']>.015
    ys=[s['poses'][MOVER][0][1] for s in samples]
    assert max(ys)-min(ys)>1.7,'The collider did not actually move'
    max_speed=1.5 if r['scenario']=='gate' else .875
    for old,new in zip(samples,samples[1:]):
        dt=new['sim_time_s']-old['sim_time_s']
        speed=math.dist(old['poses'][MOVER][0],new['poses'][MOVER][0])/dt
        assert speed<max_speed+.02,'Actor jumped instead of following a finite-speed target'
    assert len(scans)==r['sensor']['scan_frames'] and len(scans)>50
    for old,new in zip(scans,scans[1:]):assert new['sensor_time_s']>old['sensor_time_s']
    for scan in scans:
        assert len(scan['depths_m'])==len(scan['hit_positions_world'])==180
        assert all(math.isfinite(d) and .05<=d<=2.5001 for d in scan['depths_m'])
    if r['controller']=='static':
        assert r['scenario']=='gate' and not r['reached_goal']
        late=[s for s in samples if s['sim_time_s']>11]
        assert late and all(s['command']==[0.,0.] for s in late)
        assert abs(late[-1]['poses'][MOVER][0][1]-2.7)<.001
        assert math.dist(late[0]['poses'][ROBOT][0],late[-1]['poses'][ROBOT][0])<.01
        assert all(not s['planned_path_xy'] for s in scans if s['sim_time_s']>11)
        # Replaying only the final observation into a fresh copy finds a path.
        # The permanent memory, rather than a remaining physical wall, blocks it.
        fresh_class=runpy.run_path(str(Path(__file__).with_name('static_navigation.py')))['Navigator']
        fresh=fresh_class();last=scans[-1]
        fresh.update(last['pose_xyyaw'],last['depths_m'],last['hit_positions_world'],last['sensor_time_s'])
        assert fresh.path,'The last scan must show a traversable physical passage'
    else:
        assert r['reached_goal'] and r['map_cleared_total']>20
        final,rotation=r['final_poses'][ROBOT]
        assert math.dist(final[:2],(1.3,0))<.12
        qx,qy,qz,qw=rotation;yaw=math.atan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
        assert abs(yaw)<.09
        if r['scenario']=='gate':
            waiting=[s for s in samples if 4.0<s['sim_time_s']<7.5]
            assert len(waiting)>20 and all(s['command']==[0.,0.] for s in waiting)
            assert max(math.dist(s['poses'][ROBOT][0],waiting[0]['poses'][ROBOT][0]) for s in waiting)<.01
            assert any(s['sim_time_s']>8 and s['command'][0]>.05 for s in samples)
        else:
            assert min(p[1] for p in positions)<-.4 and max(p[1] for p in positions)>.8
            assert min(p[1] for p in scans[0]['planned_path_xy'])<-.8
            upper=min(s['sim_time_s'] for s in scans if s['planned_path_xy'] and max(p[1] for p in s['planned_path_xy'])>.8)
            assert upper>=2.,'The robot changed sides before the blocker began moving'
            assert any(s['phase']=='obstacle-brake' for s in samples)
        if r['dropout']['duration_s']:
            stopped=[s for s in samples if s['phase']=='sensor-stop']
            assert len(stopped)>=5 and all(s['command']==[0.,0.] and s['sensor_age_s']>.25 for s in stopped)
            assert max(math.dist(s['poses'][ROBOT][0],stopped[-1]['poses'][ROBOT][0]) for s in stopped[2:])<.01
    print(folder.name,r['scenario'],r['controller'],'verified',json.dumps(m))
    return r


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path);a=parser.parse_args()
    if a.run:check_run(a.run);return
    folder=Path(__file__).resolve().parent;root=folder.parents[1]
    record=json.loads((folder/'recorded.json').read_text())
    for case in record['runs']:check_run(folder/'evidence'/case)
    # The baseline really is the previously published implementation.
    assert (folder/'static_navigation.py').read_bytes()==(root/'labs/worldgen-navigation/navigation.py').read_bytes()
    for name,meta in record['files'].items():
        data=(root/name).read_bytes();assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],name
    print('Motion, stops, clearing, reactive replanning, sensor gap and native media verified.')


if __name__=='__main__':main()
