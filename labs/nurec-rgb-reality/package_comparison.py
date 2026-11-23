"""Pair actual native NuRec/Harmonizer frames; label without invented scene content."""
import argparse,json,shutil,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--enhanced',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--font',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);files=sorted(a.native.glob('*.png'));assert len(files)==48 and all((a.enhanced/f.name).exists() for f in files)
font=ImageFont.truetype(str(a.font),23);small=ImageFont.truetype(str(a.font),17)
for f in [font,small]:
 try:f.set_variation_by_axes([450])
 except (AttributeError,OSError):pass
for lang in ['en','ko']:
 with tempfile.TemporaryDirectory() as folder:
  for i,path in enumerate(files):
   before=Image.open(path).convert('RGB');after=Image.open(a.enhanced/path.name).convert('RGB');assert before.size==after.size==(1024,576);im=before.copy();im.paste(after.crop((512,0,1024,576)),(512,0));im=im.resize((1280,720),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im);d.line((640,0,640,720),fill=(255,255,255),width=2)
   labels=[(14,14,'NuRec native' if lang=='en' else 'NuRec 원본 렌더링'),(654,14,'Harmonizer'),(14,680,'Same camera pose · non-temporal enhancement' if lang=='en' else '같은 카메라 시점 · 프레임별 보정'),(964,680,'Built on NVIDIA Cosmos')]
   for x,y,text in labels:
    f=font if y<100 else small;b=d.textbbox((0,0),text,font=f);w=b[2]-b[0];d.rectangle((x-6,y-3,x+w+6,y+31 if y<100 else y+24),fill=(247,249,250));d.text((x,y),text,fill=(27,35,41),font=f)
   im.info.clear();im.save(Path(folder)/f'{i:06d}.png')
  target=a.output/f'nurec-harmonizer.{lang}.mp4';subprocess.run(['ffmpeg','-v','error','-y','-framerate','6','-i',str(Path(folder)/'%06d.png'),'-an','-r','30','-c:v','libx264','-crf','21','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True);subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True)
  Image.open(Path(folder)/'000000.png').convert('RGB').save(a.output/f'nurec-harmonizer.{lang}.jpg',quality=88)
 print('PACKAGED_NATIVE_COMPARISON',lang,48,'paired poses, 8 seconds')
