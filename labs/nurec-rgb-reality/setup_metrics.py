"""Cache the public NuRec metric dependency before offline container execution."""
import argparse,hashlib
from pathlib import Path
from urllib.request import urlopen
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();path=a.root/'runtime-home/.cache/torch/hub/checkpoints/alexnet-owt-7be5be79.pth';sha='7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02';path.parent.mkdir(parents=True,exist_ok=True)
if not path.exists():
 tmp=path.with_suffix('.download')
 with urlopen('https://download.pytorch.org/models/alexnet-owt-7be5be79.pth') as response,tmp.open('wb') as out:
  while block:=response.read(1024*1024):out.write(block)
 with tmp.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha
 tmp.rename(path)
with path.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha
print('NuRec metric dependency checksum verified; weights stay outside Git.')
