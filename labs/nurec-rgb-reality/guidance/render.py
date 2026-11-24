"""Run native NuRec rendering without its identity-resize rounding error.

The pinned runtime can turn a 1024x569 native camera into 1023x569 through
floating-point aspect-ratio truncation. For an exactly matching resolution,
keep the original intrinsics. No prediction or reference pixels are resized.
All other resolutions use the unmodified native implementation.
"""
import json, os
import nre.render.render as native

original=native.transform_intrinsics_to_resolution


def preserve_identity(camera_intrinsics,resolution):
    if tuple(camera_intrinsics.resolution.astype(int))==tuple(resolution):
        return camera_intrinsics
    return original(camera_intrinsics,resolution)


native.transform_intrinsics_to_resolution=preserve_identity
from nre.utils.io.export.render import render
render.main(args=json.loads(os.environ['RGB_RENDER_ARGS']),standalone_mode=False)
