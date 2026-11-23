"""Join the native enhancement comparison and actual browser interaction recording."""
import argparse,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);a=p.parse_args()
for lang in ['en','ko']:
 before=a.input/f'nurec-harmonizer.{lang}.mp4';viewer=a.input/f'nurec-rgb-reality.{lang}.mp4';target=a.input/f'nurec-overview.{lang}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(before),'-i',str(viewer),'-filter_complex','[0:v][1:v]concat=n=2:v=1:a=0[v]','-map','[v]','-an','-c:v','libx264','-crf','21','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True);shutil.copy2(a.input/f'nurec-rgb-reality.{lang}.jpg',a.input/f'nurec-overview.{lang}.jpg')
 print('Combined native GPU comparison and actual browser recording',lang)
