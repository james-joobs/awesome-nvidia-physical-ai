"""RGB-derived geometric priors in the existing relative coordinate frame."""
import numpy as np


def align_depth(prediction, target, iterations=8):
    """Robust positive scale/shift fit to training-view SfM z depths only."""
    x, y = np.asarray(prediction, float), np.asarray(target, float)
    valid = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    x, y = x[valid], y[valid]
    if len(x) < 30:
        raise ValueError('At least 30 valid training correspondences are required')
    keep = (y < np.percentile(y, 95)) & (y > np.percentile(y, 5))
    x, y = x[keep], y[keep]
    a, b = float(np.median(y / x)), 0.0
    A = np.stack([x, np.ones_like(x)], axis=1)
    for _ in range(iterations):
        residual = a*x + b - y
        sigma = max(float(np.median(np.abs(residual))) * 1.4826, .01*np.median(y))
        weights = np.minimum(1., 1.5*sigma/np.maximum(np.abs(residual), 1e-12))
        fit = np.linalg.lstsq(A*np.sqrt(weights[:, None]), y*np.sqrt(weights), rcond=None)[0]
        if fit[0] <= 0 or abs(fit[1]) > np.median(y):
            break
        a, b = map(float, fit)
    # Remove gross outliers after robust fitting so their residual influence
    # does not bias a clean, well-conditioned scale/shift estimate.
    residual=np.abs(a*x+b-y)
    threshold=max(3*1.4826*float(np.median(residual)),.03*float(np.median(y)))
    inliers=residual<threshold
    if inliers.sum()>=30:
        fit=np.linalg.lstsq(A[inliers],y[inliers],rcond=None)[0]
        if fit[0]>0 and abs(fit[1])<=np.median(y):a,b=map(float,fit)
    return a, b, {'samples': len(x), 'inliers': int(inliers.sum()), 'median_relative_error': float(np.median(np.abs(a*x+b-y)/y))}


def normals_from_z(depth, K, valid):
    """Camera-facing unit normals from z-depth; invalid boundaries stay zero."""
    h, w = depth.shape
    yy, xx = np.mgrid[:h, :w]
    rays = np.stack([(xx-K[0, 2])/K[0, 0], (yy-K[1, 2])/K[1, 1], np.ones((h, w))], axis=-1)
    points = rays * depth[..., None]
    dx = points[1:-1, 2:] - points[1:-1, :-2]
    dy = points[2:, 1:-1] - points[:-2, 1:-1]
    n = np.cross(dy, dx)
    length = np.linalg.norm(n, axis=-1, keepdims=True)
    n /= np.maximum(length, 1e-10)
    local = valid[1:-1, 1:-1] & valid[1:-1, 2:] & valid[1:-1, :-2] & valid[2:, 1:-1] & valid[:-2, 1:-1]
    z = depth[1:-1, 1:-1]
    jump = np.maximum(np.abs(depth[1:-1, 2:]-depth[1:-1, :-2]), np.abs(depth[2:, 1:-1]-depth[:-2, 1:-1]))
    local &= (length[..., 0] > 1e-10) & (jump < .08*np.maximum(z, 1e-3))
    out = np.zeros((h, w, 3), np.float32)
    out[1:-1, 1:-1] = np.where(local[..., None], n, 0)
    return out, rays.astype(np.float32)
