"""Install an isolated, pinned inference environment without changing other labs."""
import argparse, platform, shutil, subprocess
from pathlib import Path

REVISION='3d835ec1a5802d64a8b8b15f817a1ab54809bfe4'


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();root=a.root.expanduser().resolve();root.mkdir(parents=True,exist_ok=True)
    if platform.system()!='Linux':raise SystemExit('GPU training requires Linux; saved comparisons can be viewed in a browser on other systems.')
    uv=shutil.which('uv') or str(Path.home()/'.local/bin/uv')
    source=root/'depth-anything-3';python=root/'.venv/bin/python'
    def run(args,**kw):subprocess.run([str(x) for x in args],check=True,**kw)
    if not source.exists():run(['git','clone','https://github.com/ByteDance-Seed/Depth-Anything-3.git',source])
    run(['git','checkout',REVISION],cwd=source)
    if not python.exists():run([uv,'venv','--python','3.11',python.parent.parent])
    run([uv,'pip','install','--python',python,'torch==2.8.0','torchvision==0.23.0','--index-url','https://download.pytorch.org/whl/cu128'])
    run([uv,'pip','install','--python',python,'--no-deps','-e',source])
    run([uv,'pip','install','--python',python,'-r',Path(__file__).with_name('requirements.txt')])
    run([python,'-c','from depth_anything_3.api import DepthAnything3; print("RGB depth inference environment ready")'])


if __name__=='__main__':main()
