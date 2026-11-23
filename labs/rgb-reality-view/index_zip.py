"""Read only the central directory of the pinned public PandaSet ZIP mirror."""
import argparse,io,json,time,zipfile
from urllib.request import Request,urlopen
REVISION='e2e123aea3b3132c67f4b395ec6120f63e190271'
SIZE=44520528731
URL=f'https://huggingface.co/datasets/georghess/pandaset/resolve/{REVISION}/pandaset.zip?download=true&index={int(time.time())}'
class RemoteZip(io.RawIOBase):
 def __init__(self):self.pos=0
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.pos
 def seek(self,offset,whence=0):
  self.pos=offset if whence==0 else self.pos+offset if whence==1 else SIZE+offset
  if self.pos<0:raise ValueError('Invalid ZIP offset')
  return self.pos
 def read(self,n=-1):
  n=min(SIZE-self.pos,n if n>=0 else SIZE-self.pos)
  if n<=0:return b''
  if n>64*1024*1024:raise ValueError('Unexpected large ZIP metadata read')
  start=self.pos;end=start+n-1
  for attempt in range(5):
   try:
    with urlopen(Request(URL,headers={'Range':f'bytes={start}-{end}'}),timeout=120) as response:
     if response.status!=206 or response.headers.get('Content-Range')!=f'bytes {start}-{end}/{SIZE}':raise ValueError('Server returned a different byte range')
     data=response.read(n+1)
    if len(data)!=n:raise ValueError('Truncated ZIP metadata')
    self.pos+=n;return data
   except Exception:
    if attempt==4:raise
    time.sleep(1+attempt)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
 with zipfile.ZipFile(RemoteZip()) as archive:
  entries=[{'name':i.filename,'size':i.file_size,'compressed':i.compress_size,'crc32':i.CRC,'offset':i.header_offset,'type':i.compress_type} for i in archive.infolist()]
 with open(args.output,'w') as f:json.dump({'revision':REVISION,'archive_size':SIZE,'members':entries},f)
 print(f'Indexed {len(entries)} ZIP members without downloading the 44.5 GB archive')
