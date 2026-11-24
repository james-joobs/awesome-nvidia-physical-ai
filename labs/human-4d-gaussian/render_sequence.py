"""Render actual native 4D intervals beside matched observed RGB frames."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
import numpy as np

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--ffmpeg',required=True);a=p.parse_args();r=a.root;w=r/'multiview-prior';sys.path.insert(0,str(w/'4danyone'))
 import torch
 from PIL import Image,ImageDraw,ImageFont,ImageOps
 from fdanyone.reconstruction.checkpoint import load_render_model
 from fdanyone.reconstruction.rasterizer import Camera,render
 torch.set_num_threads(8);manifest=json.loads((r/'models.json').read_text());segments=manifest['segments'];total=manifest['covered_frames'];out=r/'renders';out.mkdir(exist_ok=True);H,W=640,360;f=H/(2*np.tan(np.deg2rad(21)));adapter=np.load(w/'pilot/soma-conditioning.npz');g=np.load(r/'rig/geometry.npz');j=(g['joints'][:total]-adapter['world_origin'])@adapter['cv_to_world'];center=np.array([np.median(j[:,0,0]),(np.quantile(j[:,:,1],.995)+np.quantile(j[:,:,1],.005))/2,np.median(j[:,0,2])]);radial=np.linalg.norm(j[:,:,[0,2]]-center[[0,2]],axis=-1)+.12;radius=float(np.ceil(max(np.quantile(radial,.995)*(1+f/(W*.44)),np.quantile(radial+abs(j[:,:,1]-center[1])*f/(H*.44),.995),2.7)*10)/10+.1)
 try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
 except OSError:font=ImageFont.load_default()
 pipe=subprocess.Popen([a.ffmpeg,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*2}x{H+56}','-r','30','-i','pipe:0','-an','-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'comparison.mp4')],stdin=subprocess.PIPE)
 active=None;model=None;rendered=0
 try:
  with torch.no_grad():
   for t in range(total):
    segment=next(s for s in segments if s['start_frame']<=t<s['start_frame']+s['valid_frames'])
    if segment['id']!=active:
     if model is not None:del model;torch.cuda.empty_cache()
     meta,model=load_render_model(r/segment['model'],'cuda');cfg=meta['config'];active=segment['id']
    angle=2*np.pi*t/max(total-1,1);eye=center+np.array([radius*np.sin(angle),0,radius*np.cos(angle)]);z=center-eye;z/=np.linalg.norm(z);x=np.cross(z,[0,1,0]);x/=np.linalg.norm(x);y=np.cross(z,x);C=np.eye(4);C[:3,:3]=np.stack([x,y,z],-1);C[:3,3]=eye;camera=Camera({'name':'orbit','K':[[f,0,W/2],[0,f,H/2],[0,0,1]],'w2c':np.linalg.inv(C).tolist(),'width':W,'height':H},'cuda',far=cfg['far'],near=cfg['near'],space_scale=cfg['space_scale'],image_scale=1.)
    rgb,alpha,_=render(model,camera,(t-segment['start_frame'])/30,marginal_threshold=cfg['marginal_threshold']);prediction=((rgb+.96*(1-alpha)).clamp(0,1).permute(1,2,0).cpu().numpy()*255).astype('uint8');source=ImageOps.contain(Image.open(r/f'frames/{t+1:06d}.jpg').convert('RGB'),(W,H));canvas=Image.new('RGB',(W*2,H+56),'white');canvas.paste(source,((W-source.width)//2,28+(H-source.height)//2));canvas.paste(Image.fromarray(prediction),(W,28));draw=ImageDraw.Draw(canvas);draw.text((8,8),'OBSERVED RGB / SAME TIME',font=font,fill='#36454f');draw.text((W+8,8),'NATIVE 4DGS / CAMERA ORBIT',font=font,fill='#36454f');draw.text((8,H+35),'Generated unseen appearance / RGB-inferred motion and geometry',font=font,fill='#627078');pipe.stdin.write(np.asarray(canvas).tobytes());rendered+=1
    if t==0:canvas.save(out/'poster.jpg',quality=95)
    if t%120==0:print('NATIVE_SEQUENCE_FRAME',t,total,flush=True)
 finally:
  pipe.stdin.close();code=pipe.wait()
 if code or rendered!=total:raise RuntimeError(f'Incomplete native rendering: {rendered}/{total}, encoder exit={code}')
 (out/'rendered.json').write_text(json.dumps({'frames':rendered,'fps':30,'duration':rendered/30,'panels':'Equal-size observed RGB and actual native 4D Gaussian orbit, matched times','camera':{'target':center.tolist(),'radius':radius,'fov':42},'not_browser_mouse_recording':True},indent=2)+'\n')
if __name__=='__main__':main()
