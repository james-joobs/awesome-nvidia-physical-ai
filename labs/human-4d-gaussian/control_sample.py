"""Build a public, known-geometry SOMA control sample.

This is skinning and rendering, NOT monocular reconstruction or a trained 4DGS.
Only the pinned official example motion and neutral native SOMA identity are used.
No footage, motion estimate, appearance, or geometry from a private clip is read.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,sys,time
from pathlib import Path
import numpy as np

SOMA_REVISION='01ab5b5c0876058bd27d34b1607d74b2e55e0cf4'
MOTION_SHA256='c09372492aaacdca3ca7ec5d737263d8e6042b66fdd29318d91848427fa40695'
SOURCE=f'https://github.com/NVlabs/SOMA-X/blob/{SOMA_REVISION}/assets/example_animation.usd'

def write_json(path,value):
 Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def packed(path,array):
 raw=np.ascontiguousarray(array).tobytes()
 with Path(path).open('wb') as stream:
  with gzip.GzipFile(filename='',fileobj=stream,mode='wb',mtime=0) as handle:handle.write(raw)
 return {'bytes':Path(path).stat().st_size,'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest()}

def framing(vertices):
 H,W=768,640
 f=H/(2*np.tan(np.deg2rad(21)))
 target_y=float(np.quantile(vertices[:,:,1],.995))*.52
 radial=np.linalg.norm(vertices[:,:,[0,2]],axis=-1)
 horizontal=float(radial.max())*np.sqrt(1+(f/(W*.46))**2)
 vertical=float(np.max(radial+np.abs(vertices[:,:,1]-target_y)*(f/(H*.46))))
 radius=float(np.ceil(max(horizontal,vertical)*10)/10+.1)
 return {'position':[0.,target_y,radius],'target':[0.,target_y,0.],'fov':42.,'source_width':W,'source_height':H}

def export(args):
 import torch
 sys.path.insert(0,str(args.soma_source.resolve()))
 from soma import SOMALayer
 import soma.geometry.lbs_warp as native_lbs
 torch.set_num_threads(8)
 motion=args.motion or args.soma_source/'assets/example_animation.usd'
 if hashlib.sha256(motion.read_bytes()).hexdigest()!=MOTION_SHA256:
  raise ValueError('The public control builder accepts only the pinned official SOMA example motion.')
 out=args.out;data=out/'data';data.mkdir(parents=True,exist_ok=True)
 model=SOMALayer(data_root=args.assets_dir,device='cuda',identity_model_type='soma',lod='mid',mode='warp',correctives_model_path=None)
 poses,translation,fps=model.load_motion(motion)
 # In-place presentation preserves the official rotations/vertical motion.
 translation=translation.clone();translation[:,0]=0;translation[:,2]=0
 model.prepare_identity(torch.zeros(1,model.identity_model.num_identity_coeffs,device='cuda'))
 capture=[];original=native_lbs.linear_blend_skinning
 def record(vertices,weights,indices,matrices):
  capture.append(tuple(x.detach().cpu().numpy().copy() for x in [vertices,weights,indices,matrices]))
  return original(vertices,weights,indices,matrices)
 native_lbs.linear_blend_skinning=record
 vertices=[];matrices=[];rest=weights=indices=None;started=time.monotonic()
 try:
  for start in range(0,len(poses),32):
   capture.clear()
   with torch.inference_mode():result=model.pose(poses[start:start+32].to('cuda'),transl=translation[start:start+32].to('cuda'),pose2rot=False,apply_correctives=False)
   if not capture:raise RuntimeError('Expected actual native Warp skinning.')
   bind,bw,bi,D=capture[-1]
   if rest is None:rest=bind[0];weights=bw;indices=bi
   assert np.max(abs(bind-rest[None]))<1e-4
   vertices.append(result.vertices.detach().cpu().numpy());matrices.append(D)
   print('PUBLIC_SOMA_POSE',min(start+32,len(poses)),len(poses),flush=True)
 finally:native_lbs.linear_blend_skinning=original
 V=np.concatenate(vertices);D=np.concatenate(matrices);faces=model.faces.detach().cpu().numpy().astype(np.int32)
 ground=float(V[:,:,1].min());V[:,:,1]-=ground;D[:,:,1,3]-=ground
 T,N=V.shape[:2];bones=D.shape[1];influences=weights.shape[1]
 assert bones<=256 and np.allclose(weights.sum(-1),1,atol=1e-5)
 # Neutral procedural colors; these are not textures inferred from a person.
 height=(rest[:,1]-rest[:,1].min())/np.ptp(rest[:,1]);x=abs(rest[:,0])
 color=np.tile([.16,.24,.31],(N,1));color[height>.45]=[.25,.55,.17];color[(x>.28)&(height>.45)]=[.55,.63,.67];color[x>.64]=[.82,.62,.20];color[height>.81]=[.62,.70,.73];color[height<.07]=[.11,.15,.18]
 cross=np.cross(rest[faces[:,1]]-rest[faces[:,0]],rest[faces[:,2]]-rest[faces[:,0]]);normal=np.zeros_like(rest);length=np.zeros(N);count=np.zeros(N)
 for k in range(3):
  np.add.at(normal,faces[:,k],cross)
  edge=np.linalg.norm(rest[faces[:,k]]-rest[faces[:,(k+1)%3]],axis=-1);np.add.at(length,faces[:,k],edge);np.add.at(count,faces[:,k],1)
 normal/=np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-8);light=np.array([.3,.6,.9]);light/=np.linalg.norm(light);color*=.65+.35*np.maximum(normal@light,0)[:,None]
 radius=np.clip(length/np.maximum(count,1)*.72,.0025,.017).astype(np.float32)
 fields=np.c_[rest,np.repeat(radius[:,None],3,axis=1),np.tile([0,0,0,1],(N,1)),np.full(N,.92),color].astype(np.float32)
 rng=np.random.default_rng(42);parity=[];error=0.
 for frame,index in zip(rng.integers(0,T,40),rng.integers(0,N,40)):
  mats=D[frame,indices[index]];point=((mats[:,:3,:3]@rest[index,:,None])[...,0]+mats[:,:3,3]);position=(point*weights[index,:,None]).sum(0);err=float(np.linalg.norm(position-V[frame,index]));error=max(error,err)
  parity.append({'frame':int(frame),'time':float(frame/fps),'index':int(index),'position':position.tolist()})
 assert error<1e-4,(error,'Export must match native SOMA vertices.')
 files={}
 for name,value in [('gaussians.f32.gz',fields),('bone-indices.u16.gz',indices.astype(np.uint16)),('bone-weights.f32.gz',weights.astype(np.float32)),('bone-matrices.f32.gz',D.astype(np.float32))]:files[name]=packed(data/name,value)
 camera=framing(V)
 meta={'schema':1,'representation':'soma-skinned-gaussians','gaussians':N,'frames':T,'fps':float(fps),'duration':float(T/fps),'bones':bones,'influences':influences,'matrix_layout':'row-major','units':'meters','files':files,'camera':camera,'parity_samples':parity,'native_skinning_max_error_m':error,'source':SOURCE,'source_motion_sha256':MOTION_SHA256,'license':'Apache-2.0 (SOMA motion/geometry); repository MIT wrapper code','scope':'Synthetic known-geometry control. Not learned from RGB. No private-person data. Isotropic Gaussian sizes are held fixed while centers use exact native LBS.','motion_transform':'Official local rotations/vertical motion; horizontal root translation removed; global floor shifted to zero.','appearance':'Neutral shape coefficients=0, procedural matte colors and baked rest-space shading; no real-person likeness or copied texture.'}
 write_json(data/'meta.json',meta)
 np.savez_compressed(out/'control-reference.npz',vertices=V,faces=faces,fields=fields,matrices=D,indices=indices,weights=weights)
 write_json(out/'PROVENANCE.json',{'schema':1,'source':SOURCE,'source_code_revision':SOMA_REVISION,'motion_sha256':MOTION_SHA256,'identity':'Native SOMA neutral, all identity coefficients zero, correctives disabled','private_data_used':False,'frames':T,'fps':float(fps),'seconds_export':time.monotonic()-started,'max_native_skinning_error_m':error,'camera':camera,'synthetic_control':True})
 print('PUBLIC_CONTROL_EXPORT_READY',json.dumps({'frames':T,'points':N,'bones':bones,'bytes':sum(x['bytes'] for x in files.values()),'max_error_m':error}),flush=True)

def render(args):
 import subprocess,torch
 import torch.nn.functional as F
 from PIL import Image,ImageDraw,ImageFont
 from gsplat import rasterization
 if args.nvdiffrast_dir:sys.path.insert(0,str(args.nvdiffrast_dir))
 import nvdiffrast.torch as dr
 torch.set_num_threads(8);out=args.out;meta=json.loads((out/'data/meta.json').read_text());z=np.load(out/'control-reference.npz');V=torch.tensor(z['vertices'],device='cuda');faces=torch.tensor(z['faces'],device='cuda',dtype=torch.int32);fields=torch.tensor(z['fields'],device='cuda');N=len(fields);T=len(V);meta['camera']=framing(z['vertices']);write_json(out/'data/meta.json',meta);provenance=json.loads((out/'PROVENANCE.json').read_text());provenance['camera']=meta['camera'];write_json(out/'PROVENANCE.json',provenance);H,W=meta['camera']['source_height'],meta['camera']['source_width'];f=H/(2*np.tan(np.deg2rad(42/2)));K=torch.tensor([[f,0,W/2],[0,f,H/2],[0,0,1]],device='cuda',dtype=torch.float32);target=np.asarray(meta['camera']['target']);radius=meta['camera']['position'][2]
 ctx=dr.RasterizeCudaContext();font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
 def encoder(path,width,height):return subprocess.Popen([str(args.ffmpeg),'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(meta['fps']),'-i','pipe:0','-an','-c:v','libx264','-crf','20','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
 source=encoder(out/'source.mp4',W,H);comparison=encoder(out/'comparison.mp4',W*2,H+48)
 def view(angle):
  eye=target+np.array([radius*np.sin(angle),0,radius*np.cos(angle)]);zaxis=target-eye;zaxis/=np.linalg.norm(zaxis);xaxis=np.cross(zaxis,[0,1,0]);xaxis/=np.linalg.norm(xaxis);yaxis=np.cross(zaxis,xaxis);c2w=np.eye(4);c2w[:3,:3]=np.stack([xaxis,yaxis,zaxis],-1);c2w[:3,3]=eye;return torch.tensor(np.linalg.inv(c2w),device='cuda',dtype=torch.float32)
 front=view(0);colors=fields[:,11:14].contiguous();quats=fields[:,[9,6,7,8]].contiguous();scales=fields[:,3:6].contiguous();opacities=fields[:,10].contiguous()
 with torch.no_grad():
  for t in range(T):
   # Reference RGB comes from the actual posed triangle mesh.
   cv=V[t]@front[:3,:3].T+front[:3,3];depth=cv[:,2];clip=torch.stack([2*K[0,0]/W*cv[:,0],-2*K[1,1]/H*cv[:,1],(20.1/19.9)*depth-4/19.9,depth],-1)[None]
   rast,_=dr.rasterize(ctx,clip.contiguous(),faces,resolution=[H,W]);rgb,_=dr.interpolate(colors[None],rast,faces);alpha=(rast[...,3:]>0).float();reference=(rgb*alpha+.96*(1-alpha))[0].flip(0);ref=(reference.clamp(0,1).cpu().numpy()*255).astype(np.uint8)
   camera=view(2*np.pi*t/max(1,T-1));image,a,_=rasterization(V[t].contiguous(),quats,scales,opacities,colors,camera[None],K[None],W,H,render_mode='RGB',packed=True,near_plane=.1,far_plane=20.);image=image[0]+.96*(1-a[0]);gaussian=(image.clamp(0,1).cpu().numpy()*255).astype(np.uint8)
   source.stdin.write(ref.tobytes());canvas=Image.new('RGB',(W*2,H+48),'white');canvas.paste(Image.fromarray(ref),(0,28));canvas.paste(Image.fromarray(gaussian),(W,28));draw=ImageDraw.Draw(canvas);draw.text((10,8),'KNOWN SOMA MESH / SYNTHETIC RGB',fill='#36454f',font=font);draw.text((W+10,8),'SKINNED GAUSSIANS / 3D CAMERA ORBIT',fill='#36454f',font=font);draw.text((10,H+31),'Synthetic control / official SOMA motion / no RGB reconstruction or private footage',fill='#627078',font=font);comparison.stdin.write(np.asarray(canvas).tobytes())
   if t==0:canvas.save(out/'poster.jpg',quality=95)
   if t%120==0:print('PUBLIC_CONTROL_RENDER',t,T,flush=True)
 source.stdin.close();comparison.stdin.close();assert source.wait()==0 and comparison.wait()==0
 manifest={'schema':1,'sample_kind':'soma-synthetic-control','title':'SOMA synthetic control','duration':meta['duration'],'fps':meta['fps'],'source':{'url':'source.mp4','title':'Known SOMA mesh RGB','credit':'NVIDIA SOMA-X official example motion; neutral SOMA geometry; our procedural matte render','license':'Apache-2.0 (upstream SOMA assets); MIT wrapper code','attribution_url':SOURCE},'segments':[{'id':'control','start':0,'duration':meta['duration'],'root':'data/'}],'provenance':'Synthetic control sample with known rig/geometry, not a monocular reconstruction; separate from the referenced YouTube video.','representation':'soma-skinned-gaussians','poster':'poster.jpg','comparison':'comparison.mp4'}
 write_json(out/'manifest.json',manifest);print('PUBLIC_CONTROL_MEDIA_READY',flush=True)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['export','render'],required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--soma-source',type=Path);p.add_argument('--assets-dir',type=Path);p.add_argument('--motion',type=Path);p.add_argument('--ffmpeg',type=Path,default=Path('ffmpeg'));p.add_argument('--nvdiffrast-dir',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 if a.stage=='export':
  if not a.soma_source or not a.assets_dir:p.error('export requires --soma-source and --assets-dir')
  export(a)
 else:render(a)
if __name__=='__main__':main()
