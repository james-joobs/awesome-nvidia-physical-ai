"""Package completed PandaSet NuRec/Harmonizer frames; never run fake inference."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--font',type=Path,required=True);a=p.parse_args();r=a.input;out=a.output;out.mkdir(parents=True,exist_ok=True)
views=['front','ego-elevated','ego-quarter'];frames={v:sorted((r/'renders'/v).rglob('*.png')) for v in views};frames['enhanced']=sorted((r/'enhanced').glob('*.png'));n=76
if not all(len(v)==n for v in frames.values()):raise ValueError('Expected 76 completed frames per view and enhancement')
layers={}
for v in views[1:]:
 clean=Image.open(r/'vehicle-layers'/f'{v}-car.png').convert('RGBA');shadowed=Image.open(r/'vehicle-layers'/f'{v}-shadowed.png').convert('RGBA')
 shadow=Image.new('RGBA',clean.size,(16,20,24,0));shadow.putalpha(ImageChops.subtract(shadowed.getchannel('A'),clean.getchannel('A')).point(lambda x:round(x*.22)))
 layers[v]=Image.alpha_composite(shadow,clean)

font=ImageFont.truetype(str(a.font),22);small=ImageFont.truetype(str(a.font),16)
for f,w in [(font,450),(small,400)]:
 try:f.set_variation_by_axes([w])
 except (OSError,AttributeError):pass
copy={
 'en':['Real-road reconstruction · Volvo S90 ego reference','PandaSet + NuRec · added car model, not the original collection vehicle','Elevated view','Quarter view · Harmonizer','Original camera photograph','NuRec at original camera','New view · NuRec','Same new view · Harmonizer'],
 'ko':['실사 도로 복원 · Volvo S90 자차 표시','PandaSet + NuRec · Volvo는 별도로 추가한 차량 모델입니다','차량을 따라가는 높은 시점','사선 시점 · Harmonizer','원래 카메라 사진','같은 카메라 · NuRec 복원','새 시점 · NuRec','같은 새 시점 · Harmonizer']}
credit='PandaSet: Scale AI / Hesai | Car: lazercar, CC BY 4.0 | Demo: CC BY-SA 4.0 | Built on NVIDIA Cosmos'
def frame(v,i,car=False):
 im=Image.open(frames[v][i]).convert('RGBA')
 if car:im=Image.alpha_composite(im,layers['ego-quarter' if v=='enhanced' else v])
 return im.convert('RGB')
def footer(im,title,subtitle=None):
 d=ImageDraw.Draw(im);d.rectangle((0,im.height-82,im.width,im.height),fill='white');d.text((14,im.height-77),title,font=font,fill='#20252a')
 if subtitle:d.text((14,im.height-46),subtitle,font=small,fill='#5a626a')
 d.text((14,im.height-23),credit,font=small,fill='#5a626a');return im

def encode(name,stream,size=(1024,576)):
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','10','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(out/name)],stdin=subprocess.PIPE)
 for im in stream:proc.stdin.write(im.resize(size,Image.Resampling.LANCZOS).tobytes())
 proc.stdin.close()
 if proc.wait():raise RuntimeError('Encoding failed')
def sequence(lang):
 c=copy[lang]
 for v,title in [('ego-elevated',c[2]),('enhanced',c[3])]:
  for i in range(n):yield footer(frame(v,i,True),f'Volvo S90 Recharge · {title}',c[1])
def comparison(lang):
 c=copy[lang]
 for i in range(n):
  im=Image.new('RGB',(2048,1260),'white');d=ImageDraw.Draw(im)
  source=Image.open(r/'data/001/camera/front_camera'/f'{i+2:02d}.jpg').convert('RGB').resize((1024,576));tiles=[source,frame('front',i),frame('ego-quarter',i,True),frame('enhanced',i,True)]
  for j,(tile,title) in enumerate(zip(tiles,c[4:])):
   x=(j%2)*1024;y=(j//2)*606;im.paste(tile,(x,y+30));d.text((x+12,y+2),title,font=font,fill='#20252a')
  d.text((12,1227),credit,font=font,fill='#555d65');yield im
for lang in ['en','ko']:
 encode(f'pandaset-nurec.{lang}.mp4',sequence(lang));encode(f'comparison.{lang}.mp4',comparison(lang),size=(1280,788))
 im=footer(frame('enhanced',36,True),'Volvo S90 Recharge · '+copy[lang][3],copy[lang][1]);im.save(out/f'pandaset-nurec.{lang}.jpg',quality=91)
encode('volvo-quarter.mp4',(footer(frame('enhanced',i,True),'Volvo S90 · added ego reference') for i in range(n)))
encode('nurec-quarter.mp4',(footer(frame('ego-quarter',i),'PandaSet · NuRec novel view') for i in range(n)))
folder=out/'frames';folder.mkdir(exist_ok=True)
for i in [0,36,75]:
 for name in ['front','ego-quarter','enhanced']:
  (folder/f'{i:02d}-{name}.png').write_bytes(frames[name][i].read_bytes())
for v in views[1:]:layers[v].save(out/f'{v}-layer.png')
for name in ['ground-plane.json','ego-views.json']:(out/name).write_bytes((r/name).read_bytes())
# Clear source attribution and scopes accompany even an independently copied bundle.
(out/'README.md').write_text('''# Real road / Volvo ego-view evidence

PandaSet by Scale AI and Hesai. Original terms: ../PANDASET-DATA-LICENSE.txt.
Volvo S90 Recharge (Free) by lazercar, CC BY 4.0. Paint, alignment, shadows and rendering modified.
https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9
https://creativecommons.org/licenses/by/4.0/
New demo media: CC BY-SA 4.0; original PandaSet Dataset Terms also apply.
https://creativecommons.org/licenses/by-sa/4.0/
Built on NVIDIA Cosmos.

Real measured RGB/LiDAR, static NuRec baseline, non-temporal Harmonizer.
The Volvo is an added visual reference. No original ego-vehicle identity,
vehicle control, wheel animation, dynamic actor reconstruction or closed-loop driving is claimed.
No NVIDIA PhysicalAI AV dataset content or model weights are present.

See ../SOURCES.md for the upstream license-label discrepancy and community-mirror provenance.
''')
files={}
for path in out.rglob('*'):
 if path.is_file():files[str(path.relative_to(out))]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
prepared=json.loads((r/'prepared.json').read_text());h=json.loads((r/'harmonizer-result.json').read_text());nr=json.loads((r/'nurec-result.json').read_text())
report={'recorded_at':'2026-11-23','scope':'real measured road reconstruction + added Volvo display mesh; static scene, non-temporal enhancement, no driving control','dataset':{'name':'PandaSet','authors':'Scale AI and Hesai','scene':'001','mirror':'https://huggingface.co/datasets/georghess/pandaset','mirror_status':'unofficial community mirror','revision':'e2e123aea3b3132c67f4b395ec6120f63e190271','payload_terms':'CC BY 4.0 + PandaSet Dataset Terms','alternate_notice':'Scale Nucleus labels PandaSet CC BY-SA 4.0; preserved in SOURCES.md','new_media_license':'CC BY-SA 4.0 + original data terms','contains_nvidia_av_data':False},'nurec':nr,'preparation':prepared,'harmonizer':h,'video_frames_per_view':n,'capture_fps':10,'added_vehicle':'Volvo S90 Recharge by lazercar, CC BY 4.0','files':files}
(out.parent/'recorded.json').write_text(json.dumps(report,indent=2)+'\n');print('PACKAGED',len(files),'files')
