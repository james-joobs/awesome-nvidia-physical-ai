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
'en':['NuRec-trained scene and actual RGB recognition. No LiDAR.','Toggle actual detection masks and approximate 3D contact markers.','Alpamayo: 64 predicted poses; a 1.8 m camera-height assumption.','Inspect the original RGB from each selected camera.','Orbit the NuRec-trained Gaussians in the browser preview.','Driver view and saved predictions: no vehicle controls are applied.'],
'ko':['NuRec 학습 장면과 실사 RGB 인식 결과입니다. LiDAR는 쓰지 않습니다.','실제 검출 마스크와 3D 접점 추정 표시를 껐다 켜며 비교합니다.','Alpamayo 미래 자세 64개 · 거리 스케일에는 카메라 높이 1.8m를 가정했습니다.','선택한 카메라의 원본 RGB에서 인식 결과를 직접 확인합니다.','마우스로 NuRec 학습 장면의 브라우저 미리보기를 둘러봅니다.','운전자 시점과 예측 경로를 확인합니다. 차량 제어는 하지 않습니다.']}
for lang in ['en','ko']:
 meta=json.loads((a.input/f'interaction.{lang}.json').read_text());events={e['action']:e for e in meta['events']};duration=meta['content_seconds'];cuts=[0,events['recognition_off']['time_seconds']-1.6,events['policy_off']['time_seconds']-1.2,events['front_camera']['time_seconds']-1.7,events['left_camera']['time_seconds'],events['overhead']['time_seconds'],duration]
 with tempfile.TemporaryDirectory() as folder:
  inputs=['-ss',str(meta['trim_start_seconds']),'-i',str(a.input/meta['raw_file'])];chain='[0:v]setpts=PTS-STARTPTS,fps=30[v0];';tmp=Path(folder)
  for i,line in enumerate(text[lang]):
   im=Image.new('RGBA',(1280,720),(0,0,0,0));d=ImageDraw.Draw(im);bbox=d.textbbox((0,0),line,font=font);width=bbox[2]-bbox[0];x=max(18,(1280-width)//2)
   d.rounded_rectangle((x-12,420,min(1265,x+width+12),464),radius=5,fill=(255,255,255,229));d.text((x,426),line,font=font,fill=(30,36,41,255));file=tmp/f'{i}.png';im.save(file)
   inputs+=['-loop','1','-i',str(file)];chain+=f'[v{i}][{i+1}:v]overlay=0:0:enable=\'between(t,{max(0,cuts[i]):.3f},{cuts[i+1]:.3f})\'[v{i+1}];'
  target=a.output/f'nurec-rgb-reality.{lang}.mp4';run=[ffmpeg,'-v','error','-y',*inputs,'-filter_complex',chain.rstrip(';'),'-map',f'[v{len(text[lang])}]','-t',str(duration),'-an','-c:v','libx264','-crf','21','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(target)];subprocess.run(run,check=True)
  subprocess.run([ffmpeg,'-v','error','-i',str(target),'-f','null','-'],check=True)
  shutil.copy2(a.input/f'nurec-rgb-reality.{lang}.jpg',a.output/f'nurec-rgb-reality.{lang}.jpg')
 print('TOUR_PACKAGED',lang,round(duration,2),'seconds',target.stat().st_size,'bytes')
