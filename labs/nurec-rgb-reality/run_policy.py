"""Actual Alpamayo 2 Edge inference on real RGB with explicit domain/scale assumptions."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from safetensors.torch import load_file
from alpamayo2_edge.checkpoint import load_model
from alpamayo2_edge.inference import run_data
from alpamayo2_edge.sample import CAMERA_PIXEL_BOUNDS
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--model',type=Path,required=True);a=p.parse_args();root=a.root;expected={'00000.safetensors':'d13c1a427218baf7b7d365098c0f5496c0e5e6a6bf662836b8eebbe7eb7cfe7f','00001.safetensors':'cfe424a7320ce729cd927b5ceaab4323a62443b50f461a2f5c0dd0b10634e0b5'}
for file,sha in expected.items():
 with (a.model/file).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha
start=time.perf_counter();torch.cuda.reset_peak_memory_stats();model,info=load_model(str(a.model.resolve()),device='cuda',dtype='bfloat16',attn_implementation='sdpa',local_files_only=True);records=[]
settings=dict(seed=43,top_p=.98,top_k=None,temperature=.6,num_traj_sets=1,num_traj_samples=1,max_generation_length=192,diffusion_kwargs={'inference_step':10})
for folder in sorted((root/'policy').iterdir()):
 m=json.loads((folder/'input.json').read_text());images=np.stack([np.array(Image.open(folder/r['image']).convert('RGB')) for r in m['shots']]);data={'image_frames':torch.from_numpy(images).permute(0,3,1,2).unsqueeze(1).contiguous(),'camera_indices':torch.tensor([r['camera_id'] for r in m['shots']],dtype=torch.int64),'absolute_timestamps':torch.tensor([r['timestamp_us'] for r in m['shots']],dtype=torch.int64),'ego_history_xyz':torch.tensor([m['history_xyz_m']],dtype=torch.float32),'ego_history_rot':torch.tensor([m['history_rot']],dtype=torch.float32),'camera_pixel_bounds':CAMERA_PIXEL_BOUNDS,'nav_text':[m['navigation']]};dest=root/'alpamayo'/folder.name;result=run_data(model,data,'pandaset-rgb-'+folder.name,dest,settings,'cuda');tensors=load_file(str(dest/'output.safetensors'));xyz=tensors['pred_xyz'][0,0,0].numpy();rot=tensors['pred_rot'][0,0,0].numpy();R=np.array(m['world_anchor_rotation']);P=np.array(m['world_anchor_position_relative_units']);world=(xyz/m['assumed_camera_height_m'])@R.T+P
 records.append({'keyframe':folder.name,'t0_seconds':m['t0_seconds'],'prediction':result,'xyz_m_assumed_scale':xyz.tolist(),'rotations':rot.tolist(),'world_xyz_relative_units':world.tolist(),'anchor_relative_units':P.tolist(),'assumed_camera_height_m':m['assumed_camera_height_m']})
report={'source':'NVlabs/alpamayo2-edge','source_revision':'02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e','model':'nvidia/Alpamayo2-Edge','model_revision':'b92b6aa326bd3e2235db28f248ad5a30b5890e64','weights_verified':expected,'gpu_count':1,'torch_peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,'wall_seconds_including_load':time.perf_counter()-start,'scope':'Actual inference on source RGB, with explicitly adapted virtual-camera layout and assumed metric scale. No source pose labels, measured speed, future trajectory labels or vehicle control. This is not a policy evaluation.','input_shapes':{k:list(v.shape) for k,v in data.items() if isinstance(v,torch.Tensor)},'keyframes':records};(root/'alpamayo-result.json').write_text(json.dumps(report,indent=2)+'\n');print('ALPAMAYO_RGB_COMPLETE',len(records),flush=True)
