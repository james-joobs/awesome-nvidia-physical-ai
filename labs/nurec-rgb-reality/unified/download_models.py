"""Download only pinned Aether transformer and CogVideoX VAE/text components.

Read upstream MIT and CogVideoX research/commercial terms before use. Public
weights remain outside Git; no base CogVideoX transformer is required.
"""
import argparse
import json
from pathlib import Path
from huggingface_hub import snapshot_download


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path('/workspace/models'));a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    pins=json.loads(Path(__file__).with_name('model-pins.json').read_text())
    for row,name in zip(pins,['aether','cogvideox'],strict=True):
        snapshot_download(row['repo'],revision=row['revision'],local_dir=a.out/name,allow_patterns=row['components'],max_workers=3)
    (a.out/'revisions.json').write_text(json.dumps(pins,indent=2)+'\n')
    print('Pinned public components downloaded; no model inference performed.')


if __name__=='__main__':main()
