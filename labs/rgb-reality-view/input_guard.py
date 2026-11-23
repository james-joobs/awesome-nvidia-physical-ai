"""Enforce the RGB-only contract before feature matching or training."""
import hashlib,json
from pathlib import Path

def verify_rgb_inputs(root):
 root=Path(root);manifest=json.loads((root/'input-manifest.json').read_text());images=root/'images';listed={row['image'] for row in manifest['images']};actual={p.relative_to(images).as_posix() for p in images.rglob('*') if p.is_file()}
 if actual!=listed or any(Path(p).suffix.lower() not in {'.jpg','.jpeg','.png'} for p in actual):raise ValueError('RGB input directory contains unexpected files; reconstruction stopped')
 if len(listed)!=len(manifest['images']):raise ValueError('Duplicate RGB input names')
 for row in manifest['images']:
  path=images/row['image']
  if not path.resolve().is_relative_to(images.resolve()):raise ValueError('RGB path leaves the image folder')
  if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('RGB input hash changed')
 if manifest['external_sensor_inputs'] or any(manifest[k] for k in ['supplied_camera_poses','supplied_intrinsics','supplied_depth','supplied_ground_plane']):raise ValueError('This pipeline accepts RGB pixels only')
 return manifest
