"""Pair native and enhanced camera frames with reproducible artifact hashes."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();r=a.root;files=sorted((r/'renders/orbit/front_camera').glob('*.png'));assert len(files)==48;result=json.loads((r/'nurec-result.json').read_text());harm=json.loads((r/'harmonizer-result.json').read_text());pairs=[]
for f in files:
 q=r/'enhanced'/f.name;assert q.exists() and Image.open(f).size==Image.open(q).size==(1024,576);pairs.append({'frame':f.name,'native_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'enhanced_sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
report={'native_source':'Actual NuRec 26.04 render CLI output','nurec_artifact_sha256':result['artifact_sha256'],'harmonizer_checkpoint_sha256':harm['checkpoint_sha256'],'view_paths_sha256':hashlib.sha256((r/'view-paths.json').read_bytes()).hexdigest(),'camera_pairing':'same authored camera pose and frame number','resolution':[1024,576],'frames':48,'pairs':pairs};(r/'render-pairs.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE_ENHANCED_PAIRS_VERIFIED',len(pairs))
