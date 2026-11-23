"""Build videos, matched-frame measurements and a small, inspectable evidence bundle.

CPU only. Requires numpy, Pillow and ffmpeg. Model inference is never replaced by
this compositor: it only reads the outputs of completed NuRec/Harmonizer/Alpamayo jobs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

parser=argparse.ArgumentParser()
parser.add_argument('--input',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--font',type=Path,required=True,help='Font with Korean glyphs, e.g. Noto Sans CJK')
args=parser.parse_args()
r=args.input;out=args.output;out.mkdir(parents=True,exist_ok=True)
meta=json.loads((r/'capture/capture.json').read_text())
raw=sorted((r/'novel').rglob('*.png'))
enhanced=sorted((r/'enhanced').glob('*.png'))
reference=[r/'capture'/row['image'] for row in meta['held_out']]
assert len(raw)==len(enhanced)==len(reference)==40

def image(path):return Image.open(path).convert('RGB')
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def psnr(a,b):
    mse=np.mean(((np.asarray(a,dtype=np.float64)-np.asarray(b,dtype=np.float64))/255)**2)
    return -10*math.log10(max(float(mse),1e-12))

per_frame=[]
for i,(a,b,c) in enumerate(zip(reference,raw,enhanced,strict=True)):
    per_frame.append({'frame':i,'nurec_psnr_db':psnr(image(a),image(b)),
                      'harmonizer_psnr_db':psnr(image(a),image(c))})
# Read the actual saved tensors without requiring torch or safetensors on the CPU.
blob=(r/'alpamayo/output.safetensors').read_bytes();n=struct.unpack('<Q',blob[:8])[0]
header=json.loads(blob[8:8+n]);payload=blob[8+n:]
def tensor(key):
    spec=header[key];assert spec['dtype']=='F32';begin,end=spec['data_offsets']
    return np.frombuffer(payload[begin:end],dtype='<f4').reshape(spec['shape'])
xyz=tensor('pred_xyz')[0,0,0];rot=tensor('pred_rot')[0,0,0]
assert xyz.shape==(64,3) and rot.shape==(64,3,3) and np.isfinite(xyz).all() and np.isfinite(rot).all()
trajectory={'frame':'ego at query time: x forward, y left, z up; meters',
    'dt_seconds':.1,'xyz_m':xyz.tolist(),'rotation_matrices':rot.tolist(),
    'world_ego_origin_m':[0,-1.8,0],'scope':'one inference; no controls, dynamics or closed-loop evaluation'}
(out/'trajectory.json').write_text(json.dumps(trajectory,indent=2)+'\n')
# Keep three lossless matched triplets for GPU-free numerical and visual checks.
frames_dir=out/'frames';frames_dir.mkdir(exist_ok=True)
files={}
for i in [0,20,39]:
 for kind,paths in [('reference',reference),('nurec',raw),('harmonizer',enhanced)]:
    p=frames_dir/f'{i:02d}-{kind}.png';p.write_bytes(paths[i].read_bytes());files[str(p.relative_to(out))]=sha(p)

font=ImageFont.truetype(str(args.font),23);small=ImageFont.truetype(str(args.font),18)
for f, weight in [(font,450),(small,400)]:
    try:
        if len(f.get_variation_axes()) == 1:f.set_variation_by_axes([weight])
    except OSError:
        pass
labels={
'en':['Original USD: held-out camera','NuRec: novel viewpoint','Harmonizer: non-temporal','Alpamayo 2 Edge: predicted path','Single prediction, not closed-loop driving','Built on NVIDIA Cosmos'],
'ko':['원래 USD · 별도 검사 카메라','NuRec · 새 시점 렌더링','Harmonizer · 프레임별 보정','Alpamayo 2 Edge · 예측 경로','단일 예측 경로 · 폐루프 주행 아님','Built on NVIDIA Cosmos']}

def caption(canvas,text,x=18,y=17):
    d=ImageDraw.Draw(canvas);b=d.textbbox((x,y),text,font=font)
    d.rounded_rectangle((b[0]-9,b[1]-6,b[2]+9,b[3]+6),radius=5,fill=(255,255,255))
    d.text((x,y),text,font=font,fill=(30,35,39))

def projected_path(canvas,row,visible=64):
    # Use the model's full 3D prediction. Do not flatten its z coordinates or invent a lane-following path.
    p=xyz[:visible].astype(np.float64)+np.array([0,-1.8,.08])
    c=np.array(row['camera_to_world']);cam=(p-c[:3,3])@c[:3,:3]
    K=np.array(row['K']);u=K[0,0]*cam[:,0]/np.maximum(cam[:,2],1e-6)+K[0,2]
    v=K[1,1]*cam[:,1]/np.maximum(cam[:,2],1e-6)+K[1,2]
    d=ImageDraw.Draw(canvas);last=None
    for i,(a,b,z) in enumerate(zip(u,v,cam[:,2],strict=True)):
        valid=z>.2 and 0<=a<1024 and 0<=b<576
        if valid:
            point=(float(a),float(b))
            if last is not None:d.line([last,point],fill=(70,185,0),width=7)
            if i%4==0:d.ellipse((a-5,b-5,a+5,b+5),fill=(255,255,255),outline=(38,104,0),width=2)
            last=point
        else:last=None
    # BEV preserves the complete trajectory even when its beginning falls below the camera.
    x0,y0=802,326;d.rounded_rectangle((x0,y0,1008,558),radius=8,fill=(255,255,255),outline=(170,180,188))
    xs=np.r_[0,xyz[:,0]];ys=np.r_[0,xyz[:,1]]
    span_x=max(float(xs.max()-xs.min()),15);span_y=max(float(ys.max()-ys.min()),8)
    def bev(x,y):return (905-float(y)*170/span_y,535-float(x-xs.min())*180/span_x)
    d.line([bev(x,y) for x,y in zip(xyz[:visible,0],xyz[:visible,1])],fill=(70,160,0),width=4)
    d.ellipse((900,530,910,540),fill=(20,60,130));d.text((x0+10,y0+7),'BEV · meters',font=small,fill=(40,45,50))
    return canvas

def encode(path,frames,fps=20):
    proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
      '-s','1280x720','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','22',
      '-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
    try:
        for frame in frames:proc.stdin.write(frame.resize((1280,720),Image.Resampling.LANCZOS).tobytes())
    finally:proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('Video encoding failed')

def montage(lang):
    l=labels[lang]
    # Each 40-frame sweep is played in 8 seconds. This is editing speed, not measured inference FPS.
    for i in range(160):
        j=min(i//4,39);canvas=Image.new('RGB',(1024,576),'white')
        left=image(raw[j]).resize((512,288));right=image(enhanced[j]).resize((512,288))
        canvas.paste(left,(0,145));canvas.paste(right,(512,145))
        caption(canvas,l[1],15,98);caption(canvas,l[2],526,98)
        ImageDraw.Draw(canvas).text((20,476),l[5],font=small,fill=(60,65,70))
        yield canvas
    for i in range(160):
        # A fixed novel camera isolates the route from motion of the display camera.
        canvas=projected_path(image(enhanced[20]),meta['held_out'][20],max(2,round(64*(i+1)/160)))
        caption(canvas,l[3]);caption(canvas,l[4],18,74)
        yield canvas
    for i in range(80):
        j=min(i//2,39);canvas=Image.new('RGB',(1024,576),'white')
        for col,(paths,label) in enumerate([(reference,l[0]),(raw,l[1]),(enhanced,l[2])]):
            thumb=image(paths[j]).resize((336,189));canvas.paste(thumb,(col*344,205))
            ImageDraw.Draw(canvas).text((col*344+7,166),label,font=small,fill=(40,45,50))
        yield canvas

for lang in ['en','ko']:
    encode(out/f'reality-view.{lang}.mp4',montage(lang))
    next(montage(lang)).resize((1280,720)).save(out/f'reality-view.{lang}.jpg',quality=90)
poster=next(montage('en'));poster.resize((1280,720)).save(out/'reality-view.jpg',quality=90)
# A dedicated, uncut before/after sweep and path view are useful for inspection.
for name,kind in [('nurec-novel',raw),('harmonizer-novel',enhanced)]:
    encode(out/f'{name}.mp4',(image(kind[min(i//4,39)]) for i in range(160)))
encode(out/'alpamayo-overlay.mp4',(projected_path(image(enhanced[20]),meta['held_out'][20],max(2,round(64*(i+1)/160))) for i in range(160)))
training=json.loads((r/'nurec-result.json').read_text())
prepared=json.loads((r/'prepared.json').read_text());harm=json.loads((r/'harmonizer-result.json').read_text());alpa=json.loads((r/'alpamayo/receipt.json').read_text())
report={'recorded_at':'2026-11-23','scope':'self-authored synthetic road; reconstructed rendering, per-frame enhancement and one trajectory prediction',
 'capture_runtime':meta['runtime'],
 'data_source':'Only our primitive-only USD scene; no NVIDIA PhysicalAI-AV/NuRec dataset content',
 'nurec':{**training,
          'train_views':prepared['train_views'],'held_out_views':prepared['held_out_views'],'seed_gaussians':prepared['seed_gaussians'],
          'resolution':[1024,576],'held_out_camera_height_delta_m':1.,'seed_uses_training_depth_only':True,
          'held_out_mean_psnr_db':float(np.mean([f['nurec_psnr_db'] for f in per_frame]))},
 'harmonizer':harm,'alpamayo':alpa,'comparison':{'alignment':'same K and held-out camera poses; original USD is reference',
  'nurec_mean_psnr_db':float(np.mean([f['nurec_psnr_db'] for f in per_frame])),
  'harmonizer_mean_psnr_db':float(np.mean([f['harmonizer_psnr_db'] for f in per_frame])), 'frames':per_frame},
 'limitations':['Static primitive-only scene; domain shift from real driving data',
  'Non-temporal Harmonizer can alter geometry/appearance and does not guarantee temporal consistency',
  'Alpamayo input is raw Isaac Sim RGB, not enhanced frames or NuRec sensor output',
  'One inference and a display overlay; no controls, vehicle physics or closed-loop safety evaluation',
  'Display playback speed differs from measured model inference throughput'],
 'files':files}
for p in out.glob('*.mp4'):report['files'][p.name]=sha(p)
report['files']['trajectory.json']=sha(out/'trajectory.json')
(out/'recorded.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'comparison':report['comparison']|{'frames':len(per_frame)},'videos':len(list(out.glob('*.mp4')))},indent=2))
