"""Fetch one PandaSet scene from a pinned community mirror, with ZIP CRC checks.

The original LICENSE.txt is preserved. Data rights come from that file, not the
mirror's uploader or this repository's code license. No NVIDIA AV data is used.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import time
from urllib.request import Request,urlopen
import zlib

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--scene',default='001')
parser.add_argument('--inspect',action='store_true',help='Only calibration, terms and three front-camera samples')
parser.add_argument('--index',type=Path,required=True,help='ZIP central-directory index created by index_zip.py')
args=parser.parse_args()
index=json.loads(args.index.read_text());members=[m for m in index['members'] if m['name'].startswith(f'pandaset/{args.scene}/') and not m['name'].endswith('/')]
if not members:raise ValueError('Scene does not exist in the pinned archive')
url=f"https://huggingface.co/datasets/georghess/pandaset/resolve/{index['revision']}/pandaset.zip?download=true&fetch={int(time.time())}"

def fetch_range(start,end):
 for retry in range(5):
  try:
   with urlopen(Request(url,headers={'Range':f'bytes={start}-{end}'}),timeout=120) as response:
    if response.status!=206 or not response.headers.get('Content-Range','').startswith(f'bytes {start}-'):raise ValueError('Server returned the wrong byte range')
    payload=response.read()
   if len(payload)!=end-start+1:raise ValueError('Truncated download')
   return payload
  except Exception:
   if retry==4:raise
   time.sleep(1+retry)


def save_member(member,block=None,origin=0):
 offset=member['offset']
 header=(block[offset-origin:offset-origin+30] if block is not None else fetch_range(offset,offset+29))
 fields=struct.unpack('<4s5H3L2H',header)
 if fields[0]!=b'PK\x03\x04' or fields[3] != member['type']:raise ValueError('ZIP local header disagrees with index')
 start=offset+30+fields[-2]+fields[-1];length=member['compressed']
 compressed=block[start-origin:start-origin+length] if block is not None else fetch_range(start,start+length-1)
 if member['type']==8:data=zlib.decompress(compressed,-15)
 elif member['type']==0:data=compressed
 else:raise ValueError('Unsupported compression')
 if len(data)!=member['size'] or zlib.crc32(data)!=member['crc32']:raise ValueError('ZIP CRC/size mismatch')
 relative=PurePosixPath(member['name']).relative_to('pandaset')
 if '..' in relative.parts:raise ValueError('Unsafe member path')
 target=args.output/str(relative);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 return {'file':str(relative),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

args.output.mkdir(parents=True,exist_ok=True)
if args.inspect:
 selected=[m for m in members if m['name'].endswith('.json') or m['name'].endswith('LICENSE.txt') or any(m['name'].endswith(f'front_camera/{i:02d}.jpg') for i in [0,40,79])]
 with ThreadPoolExecutor(max_workers=8) as pool:receipts=list(pool.map(save_member,selected))
else:
 # A scene occupies one contiguous region of this ZIP. Download it once, rather than making thousands of per-file requests.
 origin=min(m['offset'] for m in members)
 following=[m['offset'] for m in index['members'] if m['offset']>max(v['offset'] for v in members)]
 end=min(following)-1 if following else max(m['offset']+m['compressed']+1024 for m in members)
 chunk=8*1024*1024;ranges=[(i,min(i+chunk-1,end)) for i in range(origin,end+1,chunk)]
 with ThreadPoolExecutor(max_workers=6) as pool:parts=list(pool.map(lambda bounds:fetch_range(*bounds),ranges))
 block=b''.join(parts)
 receipts=[save_member(m,block,origin) for m in members]
receipt={'source':'PandaSet by Scale AI and Hesai','mirror':'https://huggingface.co/datasets/georghess/pandaset',
 'mirror_status':'community mirror; not affiliated with the original creators','revision':index['revision'],
 'scene':args.scene,'archive_lfs_sha256':'6e2f978fe8e98a8708ca00acae86415096868eccc2effe9826db57514582433e',
 'verification':'per-member ZIP CRC and size checked; SHA-256 recorded after download; full archive SHA-256 not checked for this range download',
 'files':receipts}
(args.output/f'{args.scene}-download.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(f'PandaSet scene {args.scene}: {len(receipts)} files verified',flush=True)
