"""Run the official 4LC construction/readout library with caller-supplied RGB-D.

Uses no WorldMirror, Wan video generator or 4LC-Video control checkpoint.
RGB coverage and actual Aether latent reuse are separate experiments.
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
import torch

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--upstream',type=Path,required=True);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--aether',type=Path);a=p.parse_args()
    if a.out.exists():raise ValueError('Choose fresh output')
    a.out.mkdir(parents=True);sys.path.insert(0,str(a.upstream/'alc/src'))
    from latent_cache import LatentCache,LatentCacheConfig,Representation
    device='cuda';torch.set_num_threads(8);data=np.load(a.input)
    H,W=data['depth'].shape[1:];times=torch.arange(17,device=device)[None]*.3
    def tensor(x):return torch.as_tensor(x,device=device)
    class PixelEncoder:
        representation=Representation((H,W),(1,1),(0,0),3,'selected')
        def encode(self,frames,*,device):return frames.to(device)
    cache=LatentCache(LatentCacheConfig(image_size=(H,W),target_chunk_size=1,motion_mask_dilation=0,temporal_motion_propagation=False),{'rgb':(PixelEncoder(),'rgb')})
    torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize();start=time.perf_counter()
    for camera in range(6):
        ids=np.arange(camera,102,6);z=data['depth'][ids];conf=data['confidence'][ids]
        valid=np.isfinite(z)&(z>.25)&(z<70)&~data['foreground'][ids]&(conf>=np.percentile(conf,15,axis=(1,2))[:,None,None])
        K=data['intrinsics'][ids].copy();K[:,0,:]/=W*3;K[:,1,:]/=H*3
        cache.construct(frames={'rgb':tensor(data['rgb'][ids][None]).float()/255},depth=tensor(z[None]).float(),valid=tensor(valid[None]),intrinsics=tensor(K[None]).float(),c2w=tensor(data['poses'][ids][None]).float(),times=times,frame_indices=torch.arange(17,device=device)[None],num_frames=17,fps=10/3,timeline_times=times,tag=f'camera-{camera}')
    torch.cuda.synchronize();construction=time.perf_counter()-start
    # Fixed scene time; sweep the camera sideways around the real front view.
    pose=data['poses'][8*6+1];path=np.repeat(pose[None],17,axis=0)
    path[:,:3,3]+=np.linspace(-1.5,1.5,17)[:,None]*pose[:3,0]
    intr=data['intrinsics'][[8*6+1]].copy();intr[:,0,:]/=W*3;intr[:,1,:]/=H*3
    qK=tensor(np.repeat(intr[None],17,axis=1)).float();qC=tensor(path[None]).float();qT=torch.full((1,17),2.4,device=device)
    torch.cuda.synchronize();start=time.perf_counter()
    front=cache.read(cache.entries[1],qT,qK,qC,static=True)['rgb'];torch.cuda.synchronize();front_s=time.perf_counter()-start
    start=time.perf_counter();composed=cache.compose(qT,qK,qC,order='earliest_first',coverage_threshold=1.);torch.cuda.synchronize();compose_s=time.perf_counter()-start
    result=composed.readouts['rgb'];coverage=[]
    for i in range(17):
        left=(front.features[0,i].clamp(0,1).cpu().numpy()*255).astype('u1');right=(result.features[0,i].clamp(0,1).cpu().numpy()*255).astype('u1')
        Image.fromarray(np.concatenate([left,right],axis=1)).resize((W*4,H*2),Image.Resampling.NEAREST).save(a.out/f'{i:02d}.png')
        coverage.append({'frame':i,'front_camera_cache':float(front.coverage[0,i].float().mean()),'six_camera_static_history':float(result.coverage[0,i].float().mean())})
    report={'schema':1,'implementation':'ZGCA-HMI-Lab/4LC standalone latent-cache','uses_4lc_video_generator':False,'uses_worldmirror':False,'uses_lidar':False,'learned_worldvae':False,'rgb_feature':'RGB pixels; not a learned encoder','input_views':102,'scene_time':2.4,'query_path':'17 lateral translations from -1.5 to +1.5 relative display units around source frame 8','grid':[H,W],'construction_seconds':construction,'front_read_seconds':front_s,'six_camera_compose_seconds':compose_s,'peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,'coverage':coverage,'coverage_is_reprojection_occupancy_not_accuracy':True}
    if a.aether:
        g=np.load(a.aether/'geometry.npz');latent=np.load(a.aether/'joint-latent.npy').astype('f4')
        features=tensor(latent[:,:,:32].transpose(0,1,3,4,2));_,T,h,w,C=features.shape;ids=np.arange(0,17,4)
        class JointEncoder:
            representation=Representation((h,w),(8,8),(4,4),C,'selected')
            def encode(self,frames,*,device):return features.to(device)
        HH,WW=g['depth'].shape[1:];K=g['intrinsics'][ids].copy();K[:,0,:]/=WW;K[:,1,:]/=HH
        latent_cache=LatentCache(LatentCacheConfig(image_size=(HH,WW),target_chunk_size=1,motion_mask_dilation=0,temporal_motion_propagation=False),{'joint':(JointEncoder(),'rgb')})
        tt=tensor(ids[None]*.3).float();zz=g['depth'][ids];valid=np.isfinite(zz)&(zz>.1)&(zz<80)
        entry=latent_cache.construct(frames={'rgb':tensor(g['observed_rgb'][ids][None]).float()/255},depth=tensor(zz[None]).float(),valid=tensor(valid[None]),intrinsics=tensor(K[None]).float(),c2w=tensor(g['camera_pose'][ids][None]).float(),times=tt,frame_indices=torch.arange(5,device=device)[None],num_frames=5,fps=1/1.2,timeline_times=tt)
        torch.cuda.synchronize();start=time.perf_counter();query=latent_cache.read(entry,tt,tensor(K[None]).float(),tensor(g['camera_pose'][ids][None]).float())['joint'];torch.cuda.synchronize()
        report['actual_aether_latent_cache']={'source_joint_shape':list(latent.shape),'cached_channels':32,'readout_shape':list(query.features.shape),'query_seconds':time.perf_counter()-start,'coverage':float(query.coverage.float().mean()),'semantics':'Jointly denoised RGB/disparity feature blocks; camera channels define geometry and are not projected as view-invariant features','not_worldvae':True}
        np.savez_compressed(a.out/'latent-readout.npz',features=query.features.cpu().numpy(),coverage=query.coverage.cpu().numpy())
    (a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
