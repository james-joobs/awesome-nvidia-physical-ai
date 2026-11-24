"""Track the input person silhouette with SAM2; no synthesized viewpoints."""
import argparse,torch,json,numpy as np,time,os
from pathlib import Path
from PIL import Image
from sam2.build_sam import build_sam2_video_predictor

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();r=a.root;torch.set_num_threads(8);d=torch.load(r/'motion.pt',map_location='cpu',weights_only=False);boxes=np.asarray(d['tracking']['boxes_xyxy']);input_meta=json.loads((r/'input.json').read_text());boxes=boxes*np.array([540/input_meta['width'],960/input_meta['height'],540/input_meta['width'],960/input_meta['height']]);T=len(boxes);assert len(list((r/'frames').glob('*.jpg')))==T
 model=build_sam2_video_predictor('configs/sam2.1/sam2.1_hiera_l.yaml',str(r/'checkpoints/sam2.1_hiera_large.pt'),device='cuda');output=r/'masks';output.mkdir(exist_ok=True);fractions=[];start=time.monotonic()
 with torch.inference_mode(),torch.autocast('cuda',dtype=torch.bfloat16):
  state=model.init_state(video_path=str(r/'frames'),offload_video_to_cpu=True,offload_state_to_cpu=True,async_loading_frames=True)
  for frame in range(0,T,120):model.add_new_points_or_box(state,frame_idx=frame,obj_id=1,box=boxes[frame])
  for frame,ids,logits in model.propagate_in_video(state):
   assert list(ids)==[1];mask=(logits[0,0]>0).cpu().numpy();Image.fromarray(mask.astype(np.uint8)*255).save(output/f'{frame+1:06d}.png');fractions.append(float(mask.mean()))
   if frame%60==0:print('MASK_FRAME',frame,T,flush=True)
 assert len(fractions)==T
 (r/'segmentation.json').write_text(json.dumps({'frames':T,'model':'facebook/sam2.1-hiera-large','prompt':'NVIDIA GEM-X/YOLOX primary-person boxes every120 normalized frames','source_rgb_size':[540,960],'foreground_fraction_min':min(fractions),'foreground_fraction_max':max(fractions),'seconds':time.monotonic()-start,'uses_synthesized_frames':False},indent=2)+'\n');print('MASKS_READY',T,flush=True)
if __name__=='__main__':main()
