"""Detect/segment real RGB road users and project approximate ground contacts.

Runs on the same single GPU after reconstruction. Reads only reconstructed RGB
images/cameras; never imports PandaSet annotations, LiDAR or sensor metadata.
"""
import argparse
from collections import Counter
import hashlib,json,math,time
from pathlib import Path
import numpy as np
from PIL import Image
import pycolmap
import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn_v2, MaskRCNN_ResNet50_FPN_V2_Weights
from torchvision.transforms.functional import pil_to_tensor
from input_guard import verify_rgb_inputs
from perception_geometry import ground_contact,rle_encode,associate

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--score',type=float,default=.8);a=p.parse_args();root=a.root;work=root/'work';out=root/'viewer';verify_rgb_inputs(work)
if not 0<a.score<1:raise ValueError('Score must be between 0 and 1')
geometry=json.loads((out/'cameras.json').read_text());T=np.array(geometry['world_to_viewer']);scale=np.linalg.norm(T[0,:3]);R=T[:3,:3]/scale
model=pycolmap.Reconstruction(str(work/'undistorted/sparse/0'));images={im.name:im for im in model.images.values()};cams=sorted({Path(n).parts[0] for n in images});frames=[]
weights=MaskRCNN_ResNet50_FPN_V2_Weights.COCO_V1
checkpoint=Path(torch.hub.get_dir())/'checkpoints'/Path(weights.url).name
expected_sha256='73cbd0190fcbe3ba339921fbce2c3a0b6bb9126c9a133c85e43a2a8e060a109e'
if not checkpoint.exists():
 checkpoint.parent.mkdir(parents=True,exist_ok=True);torch.hub.download_url_to_file(weights.url,str(checkpoint),hash_prefix=expected_sha256)
if hashlib.sha256(checkpoint.read_bytes()).hexdigest()!=expected_sha256:raise ValueError('Detector checkpoint hash differs from the pinned public weights')
categories=weights.meta['categories'];keep={'person','car','truck','bus','bicycle','motorcycle'}
torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=True;torch.cuda.reset_peak_memory_stats();start=time.perf_counter();net=maskrcnn_resnet50_fpn_v2(weights=weights,min_size=640,max_size=1024,box_score_thresh=a.score).eval().cuda();timings=[];counts=Counter();localized=0;file_hashes={}
with torch.inference_mode():
 for fi,front in enumerate(geometry['frames']):
  stem=Path(front['image']).stem;frame={'index':fi,'time_seconds':front['time_seconds'],'views':{}}
  for camera in cams:
   name=f'{camera}/{stem}.jpg'
   if name not in images:continue
   im=images[name];cam=model.cameras[im.camera_id];M=np.eye(4);M[:3]=im.cam_from_world().matrix();C=np.linalg.inv(M);position=(T@np.r_[C[:3,3],1])[:3];rotation=R@C[:3,:3];K=cam.calibration_matrix()
   path=work/'undistorted/images'/name;rgb=Image.open(path).convert('RGB');tensor=pil_to_tensor(rgb).float().cuda()/255;torch.cuda.synchronize();before=time.perf_counter();pred=net([tensor])[0];torch.cuda.synchronize();timings.append(time.perf_counter()-before)
   boxes=pred['boxes'].cpu().numpy();scores=pred['scores'].cpu().numpy();labels=pred['labels'].cpu().numpy();masks=pred['masks'].cpu().numpy();rows=[]
   for bi,(box,score,label) in enumerate(zip(boxes,scores,labels)):
    cls=categories[int(label)]
    if cls not in keep or score<a.score:continue
    x0=max(0,int(math.floor(box[0])));y0=max(0,int(math.floor(box[1])));x1=min(rgb.width,int(math.ceil(box[2])));y1=min(rgb.height,int(math.ceil(box[3])))
    if x1-x0<8 or y1-y0<8:continue
    mask=masks[bi,0]>.5;yy,xx=np.where(mask)
    if len(xx)<15:continue
    bottom=np.quantile(yy,.98);band=yy>=bottom;pixel=[float(np.median(xx[band])),float(np.median(yy[band]))]
    contact=ground_contact(pixel,K.tolist(),rotation.tolist(),position.tolist())
    # Edge-truncated objects have an unreliable ground-contact pixel.
    if y1>=rgb.height-2 or x0<=1 or x1>=rgb.width-1:contact=None
    tiny=Image.fromarray((mask[y0:y1,x0:x1]*255).astype('uint8'));tiny.thumbnail((96,160),Image.Resampling.NEAREST);bits=np.asarray(tiny)>0
    row={'class':cls,'score':round(float(score),4),'bbox':[round(float(x),2) for x in box],'camera':camera,'mask':{'origin':[x0,y0],'extent':[x1-x0,y1-y0],'size':list(tiny.size),'counts':rle_encode(bits.ravel())},'contact_pixel':[round(x,2) for x in pixel],'ground_position':contact,'track_id':None};rows.append(row);counts[cls]+=1;localized+=contact is not None
   target=out/'camera'/camera/f'{stem}.jpg';target.parent.mkdir(parents=True,exist_ok=True);rgb.thumbnail((640,640),Image.Resampling.LANCZOS);rgb.info.clear();rgb.save(target,quality=84);relative=target.relative_to(out).as_posix();file_hashes[relative]=hashlib.sha256(target.read_bytes()).hexdigest()
   frame['views'][camera]={'image':relative,'image_size':[cam.width,cam.height],'detections':rows}
  frames.append(frame)
  print('PERCEPTION_FRAME',fi+1,'/',len(geometry['frames']),sum(len(v['detections']) for v in frame['views'].values()),flush=True)
tracks=associate(frames);checkpoint=Path(torch.hub.get_dir())/'checkpoints'/Path(weights.url).name
payload={'schema':1,'detector':'TorchVision Mask R-CNN ResNet50 FPN v2 / COCO_V1','score_threshold':a.score,'mask_threshold':.5,'classes':sorted(keep),'camera_names':cams,'default_camera':'left_camera' if 'left_camera' in cams else cams[0],'localization':'RGB-derived estimated K/poses + mask contact ray intersected with an RGB-derived road plane; relative units, not 3D ground truth','association':'Greedy class/position association over this short clip; IDs may switch, no identity or velocity claim','frames':frames}
(out/'perception.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
geometry['perception_file']='perception.json';(out/'cameras.json').write_text(json.dumps(geometry,indent=2)+'\n')
receipt={'recorded_date':'2026-11-23','inputs':['undistorted RGB pixels','COLMAP cameras estimated only from RGB','road plane estimated only from RGB feature tracks'],'uses_source_annotations':False,'uses_lidar':False,'uses_supplied_calibration':False,'torch':torch.__version__,'torchvision':'0.23.0','gpu':'NVIDIA GeForce RTX 5090','gpu_count':1,'weights_url':weights.url,'weights_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'weights_distribution':'public upstream download; not bundled','code_license':'TorchVision BSD-3-Clause; model-specific weights terms not separately stated on the upstream model page; training-data rights remain separate','camera_images':len(timings),'frames':len(frames),'detections_by_class':dict(counts),'localized_detection_observations':localized,'unlocalized_detection_observations':sum(counts.values())-localized,'short_clip_track_ids':tracks,'wall_seconds':time.perf_counter()-start,'cuda_forward_seconds_first':timings[0],'cuda_forward_seconds_mean_after_first':float(np.mean(timings[1:])),'timing_scope':'CUDA forward only excludes image decode, transfer and output packaging. Full wall time includes model load and packaging; not a real-time end-to-end FPS claim.','torch_peak_allocated_mib':torch.cuda.max_memory_allocated()/2**20,'torch_peak_reserved_mib':torch.cuda.max_memory_reserved()/2**20,'perception_sha256':hashlib.sha256((out/'perception.json').read_bytes()).hexdigest(),'rgb_preview_sha256':file_hashes}
(root/'perception-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PERCEPTION_COMPLETE',json.dumps({k:v for k,v in receipt.items() if k!='rgb_preview_sha256'}),flush=True)
