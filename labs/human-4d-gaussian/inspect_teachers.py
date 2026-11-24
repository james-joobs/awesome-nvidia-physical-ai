"""Create private generated-view contact sheets for manual teacher review.

This tool does not automatically detect a wrong orientation, identity, anatomy
or missing coverage, and its output does not approve any teacher for training.
"""
import argparse,json,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--offset',action='store_true');a=p.parse_args();w=a.root/'multiview-prior';name=a.name+('-offset' if a.offset else '');case=w/name;g=json.loads((case/'generation.json').read_text());c=json.loads((case/'adapter.json').read_text());
if len(g['target_videos'])!=6 or len(c['cameras'])!=6 or len(c['source_frames'])!=121:raise ValueError('Expected six generated views with a 121-frame conditioning window')
a.out.parent.mkdir(parents=True,exist_ok=True);W,H=264,480;canvas=Image.new('RGB',(6*W,3*(H+28)),'white');draw=ImageDraw.Draw(canvas);
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except OSError:font=ImageFont.load_default()
with tempfile.TemporaryDirectory(prefix='teacher-inspect-') as td:
 for ci,video in enumerate(g['target_videos']):
  sub=Path(td)/str(ci);sub.mkdir();subprocess.run([str(a.root/'bin/ffmpeg'),'-hide_banner','-loglevel','error','-i',str(video),'-vf',r'select=eq(n\,0)+eq(n\,60)+eq(n\,120),scale=264:480','-fps_mode','vfr','-frames:v','3','-threads','2',str(sub/'%02d.png')],check=True)
  samples=sorted(sub.glob('*.png'))
  if len(samples)!=3:raise ValueError(f'Camera {ci} is missing requested 0/60/120 frame samples; do not approve this teacher set')
  for ri,path in enumerate(samples):
   canvas.paste(Image.open(path).convert('RGB'),(ci*W,ri*(H+28)+28));angle=c['cameras'][ci]['yaw_degrees'];seconds=(c['source_frames'][min(ri*60,120)])/30;draw.text((ci*W+5,ri*(H+28)+6),f'PRIOR {angle:g}deg / {seconds:.2f}s',font=font,fill='#34454f')
canvas.save(a.out,quality=94);print('TEACHER_CONTACT',a.out,'MANUAL_REVIEW_ONLY; no automatic quality approval',flush=True)
