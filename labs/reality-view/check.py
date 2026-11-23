"""Verify published model outputs on a CPU; requires numpy and Pillow, optionally ffmpeg."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

import numpy as np
from PIL import Image


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--decode-video',action='store_true')
    args=parser.parse_args()
    root=args.root
    report=json.loads((root/'recorded.json').read_text())
    for name,digest in report['files'].items():
        path=root/name
        with path.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=digest:raise ValueError(f'Changed evidence file: {name}')
    trajectory=json.loads((root/'evidence/trajectory.json').read_text())
    xyz=np.array(trajectory['xyz_m']);rot=np.array(trajectory['rotation_matrices'])
    assert xyz.shape==(64,3) and rot.shape==(64,3,3)
    assert np.isfinite(xyz).all() and np.isfinite(rot).all()
    assert np.max(np.abs(rot@rot.transpose(0,2,1)-np.eye(3)))<1e-4
    assert np.max(np.abs(np.linalg.det(rot)-1))<1e-4
    recalculated=[]
    for i in [0,20,39]:
        folder=root/'evidence/frames'
        reference=np.asarray(Image.open(folder/f'{i:02d}-reference.png').convert('RGB'),dtype=np.float64)/255
        assert reference.shape==(576,1024,3)
        row={'frame':i}
        for kind in ['nurec','harmonizer']:
            actual=np.asarray(Image.open(folder/f'{i:02d}-{kind}.png').convert('RGB'),dtype=np.float64)/255
            assert actual.shape==reference.shape
            value=-10*math.log10(max(float(np.mean((actual-reference)**2)),1e-12))
            assert abs(value-report['comparison']['frames'][i][kind+'_psnr_db'])<1e-8
            row[kind+'_psnr_db']=round(value,4)
        recalculated.append(row)
    assert report['nurec']['seed_uses_training_depth_only']
    assert report['nurec']['train_views']==120 and report['nurec']['held_out_views']==40
    assert report['alpamayo']['result']['finite']
    assert report['alpamayo']['result']['pred_xyz_shape']==[1,1,1,64,3]
    assert report['harmonizer']['frames']==40
    if args.decode_video:
        if not shutil.which('ffmpeg'):raise RuntimeError('Install ffmpeg to decode videos')
        for name in report['files']:
            if name.endswith('.mp4'):
                subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(root/name),'-f','null','-'],check=True)
    print(json.dumps({'verified_files':len(report['files']),'finite_poses':64,
        'matched_frame_psnr':recalculated,'video_decode':args.decode_video},indent=2))


if __name__=='__main__':main()
