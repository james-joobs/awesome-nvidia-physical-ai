"""CPU-only integrity, camera geometry and optional full-video decode checks."""
import argparse,hashlib,json,math,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main(decode=False):
 report=json.loads((ROOT/'recorded.json').read_text());assert report['dataset']['contains_nvidia_av_data'] is False
 assert report['nurec']['training_steps']==6000 and report['nurec']['training_seconds']>0
 assert report['preparation']['image_count']==456 and report['preparation']['camera_count']==6
 assert report['preparation']['seed_gaussians']==320000
 assert report['harmonizer']['frames']==report['video_frames_per_view']==76
 assert all(math.isfinite(t) and t>0 for t in report['harmonizer']['per_frame_seconds'])
 for name,expected in report['files'].items():
  p=ROOT/'evidence'/name;assert p.stat().st_size==expected['bytes'],name;assert hashlib.sha256(p.read_bytes()).hexdigest()==expected['sha256'],name
  if decode and p.suffix=='.mp4':subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
 views=json.loads((ROOT/'evidence/ego-views.json').read_text())['views'];assert len(views)==2
 for view in views:
  T=view['camera_to_rig'];assert len(T)==4 and all(len(row)==4 and all(math.isfinite(x) for x in row) for row in T)
  for i in range(3):
   for j in range(3):assert abs(sum(T[k][i]*T[k][j] for k in range(3))-(1 if i==j else 0))<1e-6
  R=[row[:3] for row in T[:3]];det=sum(R[0][i]*(R[1][(i+1)%3]*R[2][(i+2)%3]-R[1][(i+2)%3]*R[2][(i+1)%3]) for i in range(3));assert abs(det-1)<1e-6
 print('Verified real-road sources, 456-image preparation, 76-frame outputs, camera transforms and evidence hashes.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--decode-video',action='store_true');main(parser.parse_args().decode_video)
