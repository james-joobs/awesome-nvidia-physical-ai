"""Fetch only PandaSet JPEG RGB frames and original terms from a pinned mirror.

No intrinsics, poses, timestamps, LiDAR, depth or annotation files are fetched.
The community mirror is not an official publisher; original terms are preserved.
"""
import argparse,hashlib,json,struct,time,zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path,PurePosixPath
from urllib.request import Request,urlopen
from index_zip import RemoteZip,REVISION,SIZE
from prepare_images import prepare
import zipfile
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--scene',default='001');p.add_argument('--stride',type=int,default=3);a=p.parse_args();root=a.root;root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(RemoteZip()) as z:infos=z.infolist()
url=f'https://huggingface.co/datasets/georghess/pandaset/resolve/{REVISION}/pandaset.zip?download=true&rgb={int(time.time())}'
cameras={'front_camera','front_left_camera','front_right_camera','left_camera','right_camera','back_camera'}
selected=[]
for i in infos:
 parts=PurePosixPath(i.filename).parts
 if len(parts)==5 and parts[:3]==('pandaset',a.scene,'camera') and parts[3] in cameras and parts[4].endswith('.jpg') and int(Path(parts[4]).stem)%a.stride==0:selected.append(i)
license_info=next(i for i in infos if i.filename==f'pandaset/{a.scene}/LICENSE.txt')
def fetch(start,end):
 for retry in range(5):
  try:
   with urlopen(Request(url,headers={'Range':f'bytes={start}-{end}'}),timeout=120) as res:
    if res.status!=206 or res.headers.get('Content-Range')!=f'bytes {start}-{end}/{SIZE}':raise ValueError('Wrong archive byte range')
    data=res.read(end-start+2)
   if len(data)!=end-start+1:raise ValueError('Truncated archive member')
   return data
  except Exception:
   if retry==4:raise
   time.sleep(1+retry)
def read_member(i):
 fields=struct.unpack('<4s5H3L2H',fetch(i.header_offset,i.header_offset+29))
 if fields[0]!=b'PK\x03\x04':raise ValueError('Invalid ZIP header')
 start=i.header_offset+30+fields[-2]+fields[-1];data=fetch(start,start+i.compress_size-1)
 data=zlib.decompress(data,-15) if i.compress_type==8 else data if i.compress_type==0 else None
 if data is None or len(data)!=i.file_size or zlib.crc32(data)!=i.CRC:raise ValueError('ZIP CRC/size mismatch')
 return data
terms=read_member(license_info);(root/'PANDASET-DATA-LICENSE.txt').write_bytes(terms)
def save(i):
 relative=PurePosixPath(i.filename).relative_to(f'pandaset/{a.scene}/camera');target=root/'downloaded-rgb'/str(relative);target.parent.mkdir(parents=True,exist_ok=True);data=read_member(i);target.write_bytes(data);return {'file':str(relative),'bytes':len(data),'zip_crc32':i.CRC,'sha256':hashlib.sha256(data).hexdigest()}
with ThreadPoolExecutor(max_workers=8) as pool:receipt=list(pool.map(save,selected))
(root/'download-result.json').write_text(json.dumps({'source':'PandaSet by Scale AI and Hesai','mirror':'https://huggingface.co/datasets/georghess/pandaset','mirror_status':'unofficial community mirror','revision':REVISION,'files':receipt,'downloaded_modalities':['RGB JPEG'],'did_not_download':['LiDAR','depth','poses','intrinsics','GPS','IMU','timestamps','annotations'],'verification':'Per-file CRC and size checked, per-file SHA-256 recorded; full archive SHA-256 not checked for range download'},indent=2)+'\n')
prepare(root/'downloaded-rgb',root/'work',stride=1)
print('RGB_EXAMPLE_COMPLETE',len(receipt),'RGB frames; original terms retained',flush=True)
