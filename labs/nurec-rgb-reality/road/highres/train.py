"""Fit a static RGB Gaussian scene on an RTX GPU and export browser assets."""
import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import pycolmap
from scipy.spatial import cKDTree
import torch
from gsplat import DefaultStrategy, rasterization

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bake_surroundings import bake_sky  # noqa: E402

SH0 = .28209479177387814


def ground_alignment(sfm, rows, labels):
    names = {r["file"]: i for i,r in enumerate(rows)}
    all_sfm = list(sfm.points3D.values())
    road = []
    for point in all_sfm:
        road_votes = 0
        for entry in point.track.elements:
            image = sfm.images[entry.image_id]
            point2d = image.points2D[entry.point2D_idx]
            i = names[image.name]
            x,y = np.rint(point2d.xy).astype(int)
            label = labels[i]
            if 0 <= x < label.shape[1] and 0 <= y < label.shape[0] and label[y,x] == 0:
                road_votes += 1
        if road_votes >= 3 and road_votes >= .75*len(point.track.elements):
            road.append(point.xyz)
    if len(road)<50:
        raise ValueError(f"Too few road tracks for scene alignment: {len(road)}")
    road = np.array(road)
    cams = np.array([r["camera_pose"] for r in rows if r["camera"] == 1])
    up_guess = -np.median(cams[:,:3,1],axis=0)
    up_guess /= np.linalg.norm(up_guess)
    rng = np.random.default_rng(8)
    triplets = road[rng.integers(len(road),size=(800,3))]
    normals = np.cross(triplets[:,1]-triplets[:,0],triplets[:,2]-triplets[:,0])
    normals /= np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-10)
    normals *= np.sign(normals @ up_guess)[:,None]
    offsets = (normals*triplets[:,0]).sum(axis=1)
    heights = np.median(cams[:,:3,3] @ normals.T-offsets,axis=0)
    agreement = np.abs(road @ normals.T-offsets) < np.maximum(.06*heights,1e-4)
    score=agreement.sum(axis=0)
    score[(heights<=0)|(normals@up_guess<.96)] = 0
    hits = agreement[:,score.argmax()]
    if hits.sum()<30:
        raise ValueError("Unable to fit stable ground")
    rough_up=normals[score.argmax()]
    centroid=road[hits].mean(axis=0)
    _,matrix=np.linalg.eigh(np.cov((road[hits]-centroid).T))
    up=matrix[:,0]*np.sign(matrix[:,0]@rough_up)
    forward=cams[-1,:3,3]-cams[0,:3,3]
    forward-=up*(up@forward)
    forward/=np.linalg.norm(forward)
    side=np.cross(up,forward)
    world = np.stack([forward,side,up])
    height=float(np.median((cams[:,:3,3]-centroid)@up))
    scale=1.8/height  # Sets the display scale. The rig is otherwise up to a similarity transform.
    origin=cams[0,:3,3]-up*((cams[0,:3,3]-centroid)@up)
    xyz=(np.array([p.xyz for p in all_sfm])-origin)@world.T*scale
    source_color=np.array([p.color for p in all_sfm])
    poses=np.stack([np.vstack([r["camera_pose"],[0,0,0,1]]) for r in rows])
    poses[:,:3,:3]=world @ poses[:,:3,:3]
    poses[:,:3,3]=(poses[:,:3,3]-origin)@world.T*scale
    return xyz, source_color, poses, int(hits.sum())


def write_ply(path, params):
    arrays = [params[k].detach().cpu().numpy().reshape(len(params["means"]),-1)
              for k in ("means","scales","quats","opacities","sh0")]
    data = np.concatenate(arrays,axis=1).astype("<f4")
    fields = ["x","y","z","scale_0","scale_1","scale_2","rot_0","rot_1","rot_2","rot_3","opacity",
              "f_dc_0","f_dc_1","f_dc_2"]
    header = ["ply","format binary_little_endian 1.0",f"element vertex {len(data)}"]
    with path.open("wb") as file:
        file.write(("\n".join(header+[f"property float {f}" for f in fields]+["end_header",""])).encode())
        file.write(data.tobytes())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--sfm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--steps",type=int,default=7600)
    args=parser.parse_args()
    args.output.mkdir(parents=True)
    src=json.loads((args.input/"input.json").read_text())
    rec=json.loads((args.sfm/"cameras.json").read_text())
    rows=rec.pop("records")
    if len(rows)<35:
        raise ValueError("Too few registered views for the scene")
    labels=[cv2.imread(str(args.sfm/"labels"/r["file"].replace(".jpg",".png")),0) for r in rows]
    xyz, seed_color, poses, road_inliers=ground_alignment(pycolmap.Reconstruction(args.sfm),rows,labels)
    keep=(np.linalg.norm(xyz,axis=1)<220)&(xyz[:,2]>-5)
    xyz,seed_color=xyz[keep],seed_color[keep]
    nearest=cKDTree(xyz).query(xyz,k=4)[0][:,1:].mean(axis=1)
    scale=np.clip(nearest*.78,.035,1.7)
    init_colors=(seed_color/255)**.86
    torch.manual_seed(30)
    quat=np.zeros((len(xyz),4),np.float32)
    quat[:,0]=1

    def param(x):
        return torch.nn.Parameter(torch.as_tensor(x,dtype=torch.float32,device="cuda"))

    params=torch.nn.ParameterDict({
        "means":param(xyz), "scales":param(np.log(scale[:,None]).repeat(3,axis=1)),
        "quats":param(quat),"opacities":param(np.full(len(xyz),-1.8)),
        "sh0":param((init_colors[:,None]-.5)/SH0),
    })
    lr={"means":.0012,"scales":.006,"quats":.0015,"opacities":.045,"sh0":.006}
    opts={key:torch.optim.Adam([p],lr=lr[key],eps=1e-12) for key,p in params.items()}
    schedule=torch.optim.lr_scheduler.ExponentialLR(opts["means"], gamma=.13**(1/args.steps))
    strategy=DefaultStrategy(refine_start_iter=160,refine_stop_iter=round(args.steps*.82),
                             refine_every=90,reset_every=20000,grow_grad2d=.00026,
                             prune_opa=.012,verbose=True)
    strategy.check_sanity(params,opts)
    state=strategy.initialize_state(scene_scale=28.0)

    data=[]
    withheld = []
    for i,r in enumerate(rows):
        image=Image.open(args.input/"images"/r["file"]).convert("RGB")
        image.thumbnail((1152,750),Image.Resampling.LANCZOS)
        width,height=image.size
        rgb=np.array(image)
        # A uniform tone curve brightens the underexposed clip without frame-wise pumping.
        toned=np.rint(255*(rgb/255)**.86).astype(np.uint8)
        label=cv2.resize(labels[i],(width,height),interpolation=cv2.INTER_NEAREST)
        dynamic=(label>=11).astype(np.uint8)
        valid=(cv2.dilate(dynamic,np.ones((13,13),np.uint8))==0)&(label!=10)
        valid[round(height*.84):] = False
        k=np.diag([width/r["size"][0],height/r["size"][1],1])@r["K"]
        sky = cv2.erode((label==10).astype(np.uint8), np.ones((13,13),np.uint8)).astype(bool)
        pack=(i,width,height,toned,valid,k,sky)
        if r["frame"] in (41,59,77,89) and r["camera"] in (1,2):
            withheld.append(pack)
        else:
            data.append(pack)
    if not withheld:
        raise ValueError("No withheld photos registered")
    n_init=len(xyz)
    views=torch.tensor(np.linalg.inv(poses),dtype=torch.float32,device="cuda")
    rng=np.random.default_rng(18)
    torch.cuda.reset_peak_memory_stats()
    t0=time.perf_counter()

    def render(pack):
        i,width,height,_,_,k,_=pack
        image, alpha, info = rasterization(params["means"],params["quats"],params["scales"].exp(),
                             params["opacities"].sigmoid(),params["sh0"],views[i:i+1],
                             torch.as_tensor(k,dtype=torch.float32,device="cuda")[None],
                             width,height,sh_degree=0,near_plane=.1,far_plane=230,
                             packed=True)
        backdrop = torch.tensor([.57,.65,.73],device="cuda")
        return image+(1-alpha)*backdrop, alpha, info

    for step in range(args.steps):
        if step % len(data) == 0:
            order=rng.permutation(len(data))
        pack=data[order[step%len(data)]]
        _,_,_,image,valid,_,sky=pack
        output,alpha,info=render(pack)
        strategy.step_pre_backward(params,opts,state,step,info)
        target=torch.as_tensor(image,device="cuda").float()/255
        mask=torch.as_tensor(valid,device="cuda")
        color_loss=(output[0]-target).abs().mean(-1)
        loss=color_loss[mask].mean()+.002*(1-alpha[0,:,:,0][mask]).mean()
        if sky.any():
            sky_mask = torch.as_tensor(sky,device="cuda")
            loss += .12*alpha[0,:,:,0][sky_mask].mean()
        loss.backward()
        strategy.step_post_backward(params,opts,state,step,info,packed=True)
        for optimizer in opts.values():
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)
        schedule.step()
        if (step+1)%200==0:
            print(f"{step+1}/{args.steps} splats {len(params['means'])} loss {loss.item():.5f}",flush=True)

    torch.cuda.synchronize()
    timing=time.perf_counter()-t0
    peak=torch.cuda.max_memory_allocated()/2**30
    errors=[]
    with torch.no_grad():
        for pack in withheld:
            i,_,_,rgb,valid,_,_=pack
            predicted=render(pack)[0][0].cpu().numpy()
            mse=np.mean(((predicted-rgb/255)[valid])**2)
            errors.append(float(-10*np.log10(max(mse,1e-10))))
            Image.fromarray(np.rint(np.clip(predicted,0,1)*255).astype(np.uint8)).save(args.output/f"heldout-{i}.jpg",quality=89)
    write_ply(args.output/"scene.ply",params)
    intrinsics=np.stack([r["K"] for r in rows])
    panoramas = []
    label_small = []
    k_small = []
    train_views = sorted(pack[0] for pack in data)
    for i in train_views:
        p=rows[i]
        image=cv2.imread(str(args.input/"images"/p["file"]))
        panoramas.append(cv2.cvtColor(cv2.resize(image,(768,498)),cv2.COLOR_BGR2RGB))
        label_small.append(cv2.resize(labels[i],(768,498),interpolation=cv2.INTER_NEAREST))
        k_small.append(np.diag([768/p["size"][0],498/p["size"][1],1])@intrinsics[i])
    sky=bake_sky(np.array(panoramas),np.array(label_small),poses[train_views],np.array(k_small),args.output)
    front=[{"frame":r["frame"],"pose":poses[i].tolist(),"camera":r["camera"]}
           for i,r in enumerate(rows) if r["camera"]==1]
    np.savez_compressed(args.output/"geometry.npz",poses=poses,intrinsics=intrinsics,indices=train_views)
    report={**rec,"dataset":src["source"],"revision":src["revision"],"scene":src["scene"],
            "native_size":src["images"][0]["native_size"],"camera_sampling_hz":10/(src["frames"][1]-src["frames"][0]),
            "ground_inliers":road_inliers,"scaling":"relative, normalized to a median 1.8 front camera height",
            "input_channels":"camera RGB and camera intrinsics; ego poses reconstructed from images",
            "initial_splats":n_init,"gaussians":len(params["means"]),"steps":args.steps,
            "sky_alpha_loss":0.12,"training_seconds":round(timing,3),"max_allocated_gib":round(peak,3),
            "device":torch.cuda.get_device_name(),"train_views":len(data),
            "heldout_views":len(withheld),"heldout_static_psnr_mean":float(np.mean(errors)),
            "heldout_scope":"withheld from Gaussian fit and sky/road textures; available for camera recovery; non-sky background pixels",
            "front_path":front,"sky":sky}
    (args.output/"fit.json").write_text(json.dumps(report,indent=2)+"\n")
    print({key:value for key,value in report.items() if key!="front_path"})


if __name__=="__main__":
    main()
