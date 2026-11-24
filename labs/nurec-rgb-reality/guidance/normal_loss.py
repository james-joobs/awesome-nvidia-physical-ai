"""Channel-preserving cosine loss for NuRec's native [N,1] reduction mask."""
import torch.nn.functional as F
from libs.losses.models.registry import register_loss_fn


@register_loss_fn('rgb_normal_cosine')
def rgb_normal_cosine(prediction,target,**kwargs):
    assert prediction.shape==target.shape and prediction.shape[-1]==3
    # A plain [N] result broadcasts against [N,1] to a quadratic [N,N] array.
    return 1-(F.normalize(prediction,dim=-1)*F.normalize(target,dim=-1)).sum(dim=-1,keepdim=True)
