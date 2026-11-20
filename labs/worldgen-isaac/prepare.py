"""Calibrate WorldGen's arbitrary scale and prepare a small textured USD mesh input.

CPU-only. The anchor is an explicit assumption, not recovered metric geometry.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image


def prepare(source, output, camera_height=1.5, stride=4):
    output.mkdir(parents=True,exist_ok=True)
    depth=np.load(source/'distance.npy');h,w=depth.shape
    rgb=Image.open(source/'panorama.png').convert('RGB')
    assert rgb.size==(w,h) and np.isfinite(depth).all() and depth.min()>0
    phi,theta=np.meshgrid((np.arange(w)+.5)/w*2*np.pi-np.pi,(np.arange(h)+.5)/h*np.pi-np.pi/2)
    rays=np.stack([np.cos(theta)*np.sin(phi),np.sin(theta),np.cos(theta)*np.cos(phi)],-1)
    points=rays*depth[...,None]
    candidate=points[(theta>.8)&(theta<1.35)&(depth<3)][::8]
    # Near-camera lower hemisphere supplies a repeatable, visible floor patch.
    selected=np.ones(len(candidate),dtype=bool)
    for _ in range(5):
        q=candidate[selected]
        A=np.column_stack([q[:,0],q[:,2],np.ones(len(q))])
        a,b,c=np.linalg.lstsq(A,q[:,1],rcond=None)[0]
        residual=candidate[:,1]-(a*candidate[:,0]+b*candidate[:,2]+c)
        selected=np.abs(residual)<.025
    up=np.array([a,-1.,b]);up/=np.linalg.norm(up)
    d=c/np.linalg.norm([a,-1,b])
    scale=camera_height/d
    right=np.array([1.,0,0]);right-=up*right.dot(up);right/=np.linalg.norm(right)
    forward=np.cross(up,right)
    R=np.stack([right,forward,up])
    origin=-d*up
    world=(points-origin)@R.T*scale
    ys=np.arange(0,h,stride);xs=np.arange(0,w,stride)
    small=world[np.ix_(ys,xs)]
    sy,sx=small.shape[:2]
    # Preserve the panorama seam. Each UV is at the center of its source pixel.
    yy,xx=np.meshgrid(ys,xs,indexing='ij')
    uv=np.stack([(xx+.5)/w,1-(yy+.5)/h],-1)
    ids=np.arange(sy*sx).reshape(sy,sx)
    tl=ids[:-1,:-1];tr=ids[:-1,1:];bl=ids[1:,:-1];br=ids[1:,1:]
    faces=np.concatenate([np.stack([tl,bl,tr],-1).reshape(-1,3),np.stack([tr,bl,br],-1).reshape(-1,3)])
    # The unwrapped seam remains an explicit small gap instead of an incorrect UV bridge.
    np.savez_compressed(output/'room-mesh.npz',points=small.reshape(-1,3).astype('f4'),indices=faces.astype('i4'),uv=uv.reshape(-1,2).astype('f4'))
    rgb.save(output/'panorama.jpg',quality=94)
    residual_m=((candidate-origin)@up*scale)[selected]
    manifest={'source':'WorldGen robot-lab, seed 42; generated 2026-11-20',
        'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ['distance.npy','panorama.png']},
        'metric_scale':'assumed camera-to-floor height; not a measured scale recovery',
        'assumed_camera_height_m':camera_height,'meters_per_worldgen_unit':float(scale),
        'source_floor_plane':{'normal':up.tolist(),'offset':float(d),'inliers':int(selected.sum()),'candidates':len(candidate),'threshold_source_units':.025},
        'source_to_isaac':{'rotation_rows':R.tolist(),'source_origin':origin.tolist(),'formula':'p_isaac = scale * R @ (p_source - source_origin); Z up, metersPerUnit=1'},
        'floor_inlier_rms_m':float(np.sqrt(np.mean(residual_m**2))),
        'full_bounds_m':[world.reshape(-1,3).min(0).tolist(),world.reshape(-1,3).max(0).tolist()],
        'render_mesh':{'stride':stride,'vertices':len(small.reshape(-1,3)),'triangles':len(faces),'collision_enabled':False,'small_uv_seam_gap':True},
        'physics_proxy':{'floor_center':[0,0,-.05],'floor_size':[5,4,.1],
            'obstacle_center':[0,0,.3],'obstacle_size':[.45,.8,.6],
            'scope':'authored test floor and added crate only; not automatically inferred furniture collisions'},
        'robot':{'type':'authored differential-drive AMR','body_size':[.55,.40,.18],'wheel_radius_m':.11,'wheel_base_m':.52,'mass_chassis_kg':8},
        'route':{'start':[-1.3,0,.24],'goal':[1.3,0],'detour_waypoints':[[-.85,0],[-.85,-.95],[.85,-.95],[1.3,0]]}}
    (output/'calibration.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'scale':scale,'floor_rms_m':manifest['floor_inlier_rms_m'],'mesh':manifest['render_mesh']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--camera-height',type=float,default=1.5);p.add_argument('--stride',type=int,default=4)
    a=p.parse_args();prepare(a.source,a.output,a.camera_height,a.stride)
