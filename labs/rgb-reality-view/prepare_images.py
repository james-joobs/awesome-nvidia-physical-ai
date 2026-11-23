"""Create a pixel-only input folder. Never read depth, poses, GPS or LiDAR files."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageOps
EXTENSIONS={'.jpg','.jpeg','.png','.webp'}
def prepare(source,output,stride=1,max_side=1024):
 source=Path(source);output=Path(output);images=output/'images'
 if images.exists() and any(images.rglob('*')):raise ValueError('Use a fresh output folder to prevent mixing RGB and previous reconstruction inputs')
 images.mkdir(parents=True,exist_ok=True);rows=[]
 folders=sorted({p.parent for p in source.rglob('*') if p.is_file() and p.suffix.lower() in EXTENSIONS})
 for folder in folders:
  files=sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS)[::stride]
  camera=folder.relative_to(source).as_posix().replace('/','_') if folder!=source else 'camera'
  for i,p in enumerate(files):
   im=ImageOps.exif_transpose(Image.open(p)).convert('RGB');im.thumbnail((max_side,max_side),Image.Resampling.LANCZOS)
   target=images/camera/f'{p.stem}.jpg';target.parent.mkdir(parents=True,exist_ok=True)
   # Fresh RGB pixels: do not copy EXIF, GPS, camera K, ICC or other sidecars.
   im.info.clear();im.save(target,format='JPEG',quality=96)
   rows.append({'image':target.relative_to(images).as_posix(),'width':im.width,'height':im.height,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
 if len(rows)<8:raise ValueError('At least eight overlapping RGB frames are needed')
 manifest={'schema':1,'input':'RGB pixels only','external_sensor_inputs':[],'supplied_camera_poses':False,'supplied_intrinsics':False,'supplied_depth':False,'supplied_ground_plane':False,'stride':stride,'max_side':max_side,'images':rows}
 (output/'input-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('RGB_ONLY_INPUT',len(rows),'images',flush=True)
 return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--stride',type=int,default=1);p.add_argument('--max-side',type=int,default=1024);a=p.parse_args();prepare(a.input,a.output,a.stride,a.max_side)
