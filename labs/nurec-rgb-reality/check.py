"""CPU checks of actual RGB-only NuRec, enhancement, perception and VLA outputs.

Integrity and execution checks do not establish driving or detector accuracy.
"""
import argparse,gzip,hashlib,json,math,struct,subprocess
from pathlib import Path
LAB=Path(__file__).resolve().parent
REPO=LAB.parents[1]
def read(name):return json.loads((LAB/name).read_text())
def proper_rotation(R):
 assert len(R)==3 and all(len(row)==3 for row in R) and all(math.isfinite(x) for row in R for x in row)
 for i in range(3):
  for j in range(3):assert abs(sum(R[k][i]*R[k][j] for k in range(3))-(i==j))<2e-3
 det=sum(R[0][i]*(R[1][(i+1)%3]*R[2][(i+2)%3]-R[1][(i+2)%3]*R[2][(i+1)%3]) for i in range(3));assert abs(det-1)<2e-3

def main(decode=False):
 report=read('recorded.json');n=read('evidence/nurec-result.json');assert n['training_steps']==16000 and n['training_seconds']>0
 assert not n['uses_lidar'] and not n['uses_source_sensor_poses'] and not n['uses_source_annotations']
 assert n['preset']=='experimental/3dgut/3dgut_colmap' and len(n['artifact_sha256'])==64
 prep=read('evidence/prepared.json');assert prep['image_count']==162 and prep['camera_count']==6 and prep['seed_gaussians']>20000
 assert 'RGB' in prep['seed_source']
 rig=read('evidence/rig-bundle-result.json');assert rig['input_images']==162 and rig['rig_frames']==27 and rig['rigs']==1 and rig['reprojection_after_px']<2
 harm=read('evidence/harmonizer-result.json');pairs=read('evidence/render-pairs.json');assert harm['frames']==pairs['frames']==48 and len(pairs['pairs'])==48
 assert pairs['nurec_artifact_sha256']==n['artifact_sha256'] and harm['checkpoint_sha256']==pairs['harmonizer_checkpoint_sha256']
 assert all(math.isfinite(t) and t>0 for t in harm['per_frame_seconds'])
 fresh=read('evidence/fresh-pipeline-check.json');assert fresh['exit_code']==0 and fresh['fresh_output_folder'] and fresh['new_python_environments']
 assert fresh['stages_completed']==['setup','rgb','rig','prepare','train','render','enhance','policy','perceive','export']
 assert fresh['completion_marker']=='RGB_NUREC_PIPELINE_COMPLETE' and not fresh['uses_lidar']
 assert fresh['exported_gaussians']==450000 and fresh['enhanced_frames']==48 and fresh['actual_alpamayo_keyframes']==4
 browsers=read('evidence/browser-check.json');assert {(r['language'],r['mobile']) for r in browsers}=={('en',False),('ko',False),('en',True),('ko',True)}
 for browser in browsers:
  assert not browser['errors'] and not browser['failed'] and browser['nurec_backend'] and browser['actual_alpamayo_path']
  assert browser['dimensions']['content']<=browser['dimensions']['width']+1 and browser['inline_video']['inline']
 policy=read('evidence/alpamayo-result.json');assert len(policy['keyframes'])==4 and policy['gpu_count']==1
 assert policy['input_shapes']['image_frames']==[22,1,3,576,1024] and policy['input_shapes']['ego_history_xyz']==[1,20,3]
 for k in policy['keyframes']:
  assert k['prediction']['finite'] and len(k['xyz_m_assumed_scale'])==len(k['world_xyz_relative_units'])==len(k['rotations'])==64
  assert k['assumed_camera_height_m']==1.8
  assert all(len(p)==3 and all(math.isfinite(x) for x in p) for p in k['world_xyz_relative_units'])
  for R in k['rotations']:proper_rotation(R)
 sample=read('evidence/policy-input-sample.json');assert len(sample['shots'])==22 and len(sample['history_xyz_m'])==len(sample['history_rot'])==20
 assert 'assumed' in sample['scale_status'] and 'RGB' in sample['history_source']
 for row in sample['shots']:assert row['timestamp_us']/1e6<=row['requested_time_seconds']+1e-8
 for R in sample['history_rot']:proper_rotation(R)
 assert max(abs(x) for x in sample['history_xyz_m'][-1])<1e-5
 web=REPO/'site/public/showcase/nurec-rgb-reality';g=json.loads((web/'cameras.json').read_text());assert g['backend']=='NuRec 26.04' and len(g['frames'])==27
 assert g['world_to_viewer']==[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
 with gzip.open(web/'road.spz','rb') as f:magic,version,count=struct.unpack('<III',f.read(12))
 assert magic==0x5053474E and version==3 and count==450000==g['trained_gaussians']
 data=json.loads((web/'perception.json').read_text());perception=read('evidence/perception-result.json');assert hashlib.sha256((web/'perception.json').read_bytes()).hexdigest()==perception['perception_sha256']
 assert not perception['uses_source_annotations'] and not perception['uses_lidar'] and len(data['frames'])==27
 for relative,sha in perception['rgb_preview_sha256'].items():
  path=web/relative;assert path.resolve().is_relative_to(web.resolve());assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
 viewpolicy=json.loads((web/'alpamayo.json').read_text());assert viewpolicy['keyframes']==policy['keyframes']
 for lang in ['en','ko']:
  trace=read(f'evidence/interaction.{lang}.json');events={e['action']:e for e in trace['events']};assert trace['errors']==[] and len(events)==11
  assert events['initial']['gaussians']==450000 and events['initial']['policy']['poses']==64 and events['initial']['perception']['people_in_camera']>0
  assert not events['policy_off']['policy']['enabled'] and events['policy_on']['policy']['enabled']
  assert not events['recognition_off']['perception']['enabled'] and events['recognition_on']['perception']['enabled']
  assert math.dist(events['initial']['camera'],events['orbit']['camera'])>.1 and events['perception_replay']['frame']!=events['initial']['frame']
 for relative,expected in report['files'].items():
  path=REPO/relative;assert path.resolve().is_relative_to(REPO.resolve());assert path.stat().st_size==expected['bytes'],relative;assert hashlib.sha256(path.read_bytes()).hexdigest()==expected['sha256'],relative
  if decode and path.suffix=='.mp4':subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True)
 print('Verified RGB-only NuRec completion, 450k exported Gaussians, 48 native/enhanced pairs, four actual Alpamayo outputs, perception, causal input times and browser interactions.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--decode-video',action='store_true');main(p.parse_args().decode_video)
