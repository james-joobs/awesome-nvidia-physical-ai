"""Caption the actual RGB perception viewer recording in English and Korean."""
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
'en':['Real RGB frames → Mask R-CNN: vehicles and pedestrians.','Toggle overlays to compare RGB with actual model predictions.','Switch cameras: masks and boxes come from each real image.','Orbit the scene; 3D markers use an approximate RGB road plane.','Driver view and replay share the recorded camera timeline.'],
'ko':['실사 RGB → Mask R-CNN · 주변 차량과 사람을 실제로 인식합니다.','인식 표시를 껐다 켜며 원본과 모델의 예측을 비교합니다.','카메라마다 실제 이미지에서 마스크와 검출 박스를 만듭니다.','마우스로 시점을 바꿉니다. 3D 표시는 RGB 도로면 기반 위치 추정입니다.','운전자 시점과 경로 재생을 같은 촬영 시간에 맞춰 확인합니다.']}
for lang in ['en','ko']:
 meta=json.loads((a.input/f'perception-interaction.{lang}.json').read_text());events={e['action']:e for e in meta['events']};duration=meta['content_seconds'];cuts=[0,events['recognition_off']['time_seconds']-1.6,events['front_camera']['time_seconds']-1.7,events['left_camera']['time_seconds'],events['overhead']['time_seconds'],duration]
 with tempfile.TemporaryDirectory() as folder:
  inputs=['-ss',str(meta['trim_start_seconds']),'-i',str(a.input/meta['raw_file'])];chain='[0:v]setpts=PTS-STARTPTS,fps=30[v0];';tmp=Path(folder)
  for i,line in enumerate(text[lang]):
   im=Image.new('RGBA',(1280,720),(0,0,0,0));d=ImageDraw.Draw(im);bbox=d.textbbox((0,0),line,font=font);width=bbox[2]-bbox[0];x=max(18,(1280-width)//2)
   d.rounded_rectangle((x-12,471,min(1265,x+width+12),515),radius=5,fill=(255,255,255,229));d.text((x,477),line,font=font,fill=(30,36,41,255));file=tmp/f'{i}.png';im.save(file)
   inputs+=['-loop','1','-i',str(file)];chain+=f'[v{i}][{i+1}:v]overlay=0:0:enable=\'between(t,{max(0,cuts[i]):.3f},{cuts[i+1]:.3f})\'[v{i+1}];'
  target=a.output/f'rgb-perception.{lang}.mp4';run=[ffmpeg,'-v','error','-y',*inputs,'-filter_complex',chain.rstrip(';'),'-map',f'[v{len(text[lang])}]','-t',str(duration),'-an','-c:v','libx264','-crf','21','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(target)];subprocess.run(run,check=True)
  subprocess.run([ffmpeg,'-v','error','-i',str(target),'-f','null','-'],check=True)
  shutil.copy2(a.input/f'rgb-perception.{lang}.jpg',a.output/f'rgb-perception.{lang}.jpg')
 print('TOUR_PACKAGED',lang,round(duration,2),'seconds',target.stat().st_size,'bytes')
