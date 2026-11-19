"""Run the pinned Infinigen house-tour example with explicit CPU rendering and denoising.

Usage after installing the official source in its own Python 3.11 environment:
  python run.py --source /path/to/infinigen --seed 0 --frames 1 48 --save_blend runs/house.blend
  python run.py --source /path/to/infinigen --seed 0 --frames 1 48 --load_blend runs/house.blend --output runs/house
"""
import argparse
import importlib.util
import os
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument("--source",type=Path,required=True)
    args,remaining=parser.parse_known_args()
    os.environ.setdefault("OMP_NUM_THREADS","12")
    from infinigen2.exporters.render_cycles import DenoiseMode
    from infinigen2.exporters.util.format import ExportType, RenderPass
    path=args.source/"examples/house_tour/render.py"
    spec=importlib.util.spec_from_file_location("official_house_tour",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original=module.render_cycles

    def render(**kwargs):
        import bpy
        bpy.context.scene.render.threads_mode="FIXED"
        bpy.context.scene.render.threads=12
        kwargs["render_passes"]=[RenderPass(ExportType.IMAGE_DENOISED,p.path,p.data_type) if p.type==ExportType.IMAGE else p for p in kwargs["render_passes"]]
        return original(**kwargs,device_type="CPU",denoise_mode=DenoiseMode.OPENIMAGEDENOISE)

    module.render_cycles=render
    sys.argv=[str(path),*remaining]
    module.main()


if __name__=="__main__":
    main()
