"""Attach independently generated RGB priors to NuRec's native loss inputs.

This adapter imports the separately licensed, pinned NuRec runtime. It does not
copy or redistribute runtime source. Native distance/normal losses and rendering
remain responsible for optimization and backpropagation.
"""
import functools, json, os, sys
from pathlib import Path
import cv2
import numpy as np
import torch
from ncore.data import FrameTimepoint
from nre.datasets.ncore import NCOREDataset
from nre.utils.types import RayFlags
sys.path.insert(0,'/lab/guidance')
from normal_loss import rgb_normal_cosine

root=Path(os.environ.get('NUREC_RGB_ROOT','/work'))
prior_folder=root/os.environ.get('RGB_PRIOR_FOLDER','priors-base')
original=NCOREDataset.get_camera_data_batch


@functools.lru_cache(maxsize=64)
def load_prior(sensor,stamp):
    path=prior_folder/sensor/f'{stamp}.npz'
    if not path.is_file():raise FileNotFoundError('A required RGB prior is missing; regenerate the matching training split')
    with np.load(path) as values:return values['distance'],values['normals']


def get_camera_data_batch(self,sensor_id,sensor_frame_idx,sampled_pixels=None):
    batch=original(self,sensor_id,sensor_frame_idx,sampled_pixels)
    sensor=self.datasource.camera_sensors[sensor_id]
    stamp=int(sensor.get_frame_timestamp_us(sensor_frame_idx,frame_timepoint=FrameTimepoint.END))
    distance,normals=load_prior(sensor_id,stamp)
    distance=distance[...,None]
    if sampled_pixels is not None:
        distance=sampled_pixels.apply_to_array(distance,interpolation=cv2.INTER_NEAREST)
        normals=sampled_pixels.apply_to_array(normals,interpolation=cv2.INTER_NEAREST)
    # NuRec's field is called metric_distance, but these numbers remain in its
    # scene units after scale conversion; they are not measured metric depth.
    scale=self.datasource.world_to_nre.target_scale
    batch.labels.metric_distance=torch.from_numpy(np.ascontiguousarray(distance*scale,dtype=np.float32)).unsqueeze(0)
    batch.labels.normals=torch.from_numpy(np.ascontiguousarray(normals,dtype=np.float32)).unsqueeze(0)
    valid=torch.linalg.vector_norm(batch.labels.normals,dim=-1,keepdim=True)>.5
    batch.labels.flags |= valid.to(torch.int32)*RayFlags.VALID_NORMAL.value
    return batch


NCOREDataset.get_camera_data_batch=get_camera_data_batch
from libs.losses.models.render_losses import DistanceLoss, NormalLoss


def report_native_loss(cls,label):
    forward=cls.forward
    checked=False
    def instrument(self,results,target,model):
        nonlocal checked
        result=forward(self,results,target,model)
        if not checked and torch.is_grad_enabled() and result is not None:
            value=results.rendered_cam.distance if label=='depth' else results.rendered_cam.normal
            assert value is not None and value.requires_grad, f'{label} must be differentiable'
            assert torch.isfinite(value).all(), f'{label} contains non-finite render values'
            labels=target.data.camera.labels
            count=int((labels.metric_distance>0).sum()) if label=='depth' else int((torch.linalg.vector_norm(labels.normals,dim=-1)>.5).sum())
            assert count>0,'Empty guidance mask'
            print('RGB_GUIDANCE_NATIVE_LOSS',json.dumps({'kind':label,'valid_pixels':count,'differentiable':True,'finite':True}),flush=True)
            checked=True
        return result
    cls.forward=instrument


report_native_loss(DistanceLoss,'depth')
report_native_loss(NormalLoss,'normal')
from nre.run.main import main
case=os.environ.get('RGB_GUIDANCE_CASE','depth-normal')
print('RGB_GUIDANCE_TRAIN',case,str(prior_folder.name),flush=True)
overrides=json.loads(os.environ.get('RGB_GUIDANCE_OVERRIDES','[]'))
main.main(args=['--config-name','geometry-guided.yaml',*overrides],standalone_mode=False)
