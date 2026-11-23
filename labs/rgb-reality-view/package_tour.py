"""Add concise bilingual captions to an actual recorded browser interaction."""
import argparse,json,shutil,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--font',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
ffmpeg=shutil.which('ffmpeg')
if not ffmpeg:
 import imageio_ffmpeg
 ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
font=ImageFont.truetype(str(a.font),24)
try:font.set_variation_by_axes([450])
except (OSError,AttributeError):pass
text={
'en':['RGB cameras → COLMAP → NVIDIA 3DGUT. No LiDAR or supplied poses.','Drag to orbit around the actual reconstructed 3D scene.','Tilt, zoom and pan around the added Volvo S90 mesh.','Switch to the reconstructed driver viewpoint.','Replay the camera-estimated path through a static scene.'],
'ko':['RGB 카메라 → COLMAP → NVIDIA 3DGUT · LiDAR·제공된 위치 정보 사용 안 함','마우스로 회전하면 같은 3D 장면을 다른 각도에서 볼 수 있습니다.','확대·이동하면서 실제 Volvo S90의 3D 형상을 살펴보세요.','운전자 시점으로도 전환할 수 있습니다.','사진에서 추정한 이동 경로를 정적 장면 안에서 재생합니다.']}
for lang in ['en','ko']:
 meta=json.loads((a.input/f'interaction.{lang}.json').read_text());events={e['action']:e for e in meta['events']};duration=meta['content_seconds'];cuts=[0,events['orbit_first_half']['time_seconds']-.9,events['tilt']['time_seconds']-1.8,events['pan']['time_seconds']+.3,events['driver']['time_seconds']+1.3,duration]
 with tempfile.TemporaryDirectory() as folder:
  inputs=['-ss',str(meta['trim_start_seconds']),'-i',str(a.input/meta['raw_file'])];chain='[0:v]setpts=PTS-STARTPTS,fps=30[v0];';tmp=Path(folder)
  for i,line in enumerate(text[lang]):
   im=Image.new('RGBA',(1280,720),(0,0,0,0));d=ImageDraw.Draw(im);bbox=d.textbbox((0,0),line,font=font);width=bbox[2]-bbox[0];x=max(18,(1280-width)//2)
   d.rounded_rectangle((x-12,510,min(1265,x+width+12),554),radius=5,fill=(255,255,255,229));d.text((x,516),line,font=font,fill=(30,36,41,255));file=tmp/f'{i}.png';im.save(file)
   inputs+=['-loop','1','-i',str(file)];chain+=f'[v{i}][{i+1}:v]overlay=0:0:enable=\'between(t,{max(0,cuts[i]):.3f},{cuts[i+1]:.3f})\'[v{i+1}];'
  target=a.output/f'rgb-reality-view.{lang}.mp4';run=[ffmpeg,'-v','error','-y',*inputs,'-filter_complex',chain.rstrip(';'),'-map',f'[v{len(text[lang])}]','-t',str(duration),'-an','-c:v','libx264','-crf','21','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(target)];subprocess.run(run,check=True)
  subprocess.run([ffmpeg,'-v','error','-i',str(target),'-f','null','-'],check=True)
  shutil.copy2(a.input/f'rgb-reality-view.{lang}.jpg',a.output/f'rgb-reality-view.{lang}.jpg')
 print('TOUR_PACKAGED',lang,round(duration,2),'seconds',target.stat().st_size,'bytes')
