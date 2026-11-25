"""Export a permission-cleared, model-only Pages preview from a local4D package.

The original RGB/audio and side-by-side recordings are deliberately excluded.
A separate local permission receipt is required; its contents are not published.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,math
from pathlib import Path
import numpy as np


def read(path):return json.loads(path.read_text())
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def safe(root,name):
    path=(root/name).resolve()
    if not path.is_relative_to(root.resolve()):raise ValueError('Asset path leaves package')
    return path

def select(fields,motion,variance,count):
    if len(fields)<=count:return np.arange(len(fields))
    # Reserve temporal and body-height coverage rather than globally discarding
    # all small face/hand Gaussians. Retained parameters remain unchanged.
    rng=np.random.default_rng(42)
    bins=np.minimum(31,np.maximum(0,(motion[:,3]/max(float(motion[:,3].max()),1e-5)*31).astype(int)))
    height=fields[:,1];lo,hi=np.quantile(height,[.005,.995])
    bins=bins*16+np.minimum(15,np.maximum(0,((height-lo)/max(hi-lo,1e-5)*15).astype(int)))
    weight=np.sqrt(np.maximum(fields[:,10],1e-5))
    score=np.log(np.maximum(rng.random(len(fields)),1e-12))/weight
    selected=[]
    for b in np.unique(bins):
        ids=np.flatnonzero(bins==b);quota=max(1,int(len(ids)*count/len(fields)))
        selected.extend(ids[np.argpartition(score[ids],-quota)[-quota:]])
    selected=np.asarray(selected,dtype=int)
    if len(selected)<count:
        left=np.setdiff1d(np.arange(len(fields)),selected,assume_unique=True);n=count-len(selected)
        selected=np.r_[selected,left[np.argpartition(score[left],-n)[-n:]]]
    elif len(selected)>count:selected=selected[np.argpartition(score[selected],-count)[-count:]]
    return np.sort(selected)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--permission-receipt',type=Path,required=True);p.add_argument('--max-gaussians',type=int,default=400000);a=p.parse_args()
    receipt=read(a.permission_receipt)
    if receipt.get('derived_results_publication_authorized') is not True:raise ValueError('Confirm derivative-publication permission before exporting')
    if a.out.exists():raise ValueError('Choose a fresh output folder; original results are preserved')
    if a.max_gaussians<1000:raise ValueError('Preview Gaussian limit is too small')
    src=a.input.resolve();manifest=read(src/'manifest.json')
    if manifest.get('source',{}).get('attribution_url')!='https://www.youtube.com/shorts/rWS8uli1-m0':raise ValueError('This case-study exporter requires the documented reference and its matching permission receipt')
    a.out.mkdir(parents=True)
    records=[];segments=[]
    for item in manifest['segments']:
        folder=safe(src,item['root']);meta=read(folder/'meta.json');n=meta['gaussians']
        arrays={}
        for name,columns,dtype in [('gaussians.f32.gz',14,'<f4'),('motion.f32.gz',4,'<f4'),('variance.f32.gz',4,'<f4'),('sh.f16.gz',48,'<f2')]:
            raw=gzip.decompress((folder/name).read_bytes())
            if hashlib.sha256(raw).hexdigest()!=meta['files'][name]['raw_sha256']:raise ValueError('Input array hash differs')
            arrays[name]=np.frombuffer(raw,dtype).reshape(n,columns)
        ids=select(arrays['gaussians.f32.gz'],arrays['motion.f32.gz'],arrays['variance.f32.gz'],a.max_gaussians)
        dest=a.out/'browser'/item['id'];dest.mkdir(parents=True);files={}
        for name,array in arrays.items():
            raw=np.ascontiguousarray(array[ids]).tobytes();packed=gzip.compress(raw,compresslevel=9,mtime=0);(dest/name).write_bytes(packed)
            files[name]=dict(bytes=len(packed),raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest())
        fields=arrays['gaussians.f32.gz'][ids];motion=arrays['motion.f32.gz'][ids];variance=arrays['variance.f32.gz'][ids]
        samples=[];rng=np.random.default_rng(42)
        for index,t in zip(rng.integers(0,len(ids),40),rng.uniform(0,meta['duration'],40)):
            dt=float(t)-float(motion[index,3]);samples.append(dict(index=int(index),time=float(t),position=(fields[index,:3].astype(float)+motion[index,:3]*dt).tolist(),opacity=float(fields[index,10]*math.exp(-.5*dt*dt*float(variance[index,0])))))
        meta.update(gaussians=len(ids),files=files,parity_samples=samples,preview=dict(original_gaussians=n,retained_gaussians=len(ids),selection='Seed42 temporal/body-height strata with opacity-weighted sampling; retained parameters unchanged',not_full_model=True))
        write(dest/'meta.json',meta);segment={k:item[k] for k in ['id','start','duration']};segment['root']=f"browser/{item['id']}/";segments.append(segment)
        records.append(dict(id=item['id'],original_gaussians=n,gaussians=len(ids),compressed_bytes=sum(f['bytes'] for f in files.values()),source_meta_sha256=hashlib.sha256((folder/'meta.json').read_bytes()).hexdigest()));print('MODEL_PREVIEW',item['id'],n,len(ids),flush=True)
    source=dict(youtube_id='rWS8uli1-m0',title='YouTube original · 지숭이_Jisoong',credit='지숭이_Jisoong — 체포하겠어🚨🚨',attribution_url='https://www.youtube.com/shorts/rWS8uli1-m0',delivery='Official YouTube embed only; no source RGB or audio bundled')
    write(a.out/'manifest.json',dict(schema=1,title='Monocular human4D Gaussian reconstruction',fps=manifest['fps'],duration=manifest['duration'],representation='native-conditional-4d',sample_kind='permission-cleared-reconstruction',source=source,camera=manifest['camera'],segments=segments,poster='poster.jpg',comparison='orbit.mp4',permission=dict(scope='Derived3D/4D results',confirmed_by='Project maintainer',confirmed_date=receipt['date'],source_footage_redistributed=False),provenance='RGB-estimated GEM-X/SOMA motion, generated multiview priors and native conditional4D Gaussian fitting. Browser preview uses a reduced subset; full-quality native rendering is provided as video. Unobserved sides and back are inferred, not captured ground truth.'))
    published=read(a.out/'manifest.json');published['source']['title_ko']='원본 YouTube · 지숭이_Jisoong';published['provenance_ko']='RGB에서 GEM-X/SOMA로 추정한 동작, 생성한 다중 시점 자료, conditional 4D Gaussian 학습을 연결했습니다. 브라우저는 입자 수를 줄인 미리보기이며, 전체 모델의 고화질 결과는 영상으로 제공합니다. 관측하지 않은 측면·후면은 추정입니다.';write(a.out/'manifest.json',published)
    write(a.out/'export.json',dict(schema=1,frames=round(manifest['duration']*manifest['fps']),fps=manifest['fps'],duration=manifest['duration'],segments=records,source_rgb_included=False,source_audio_included=False,preview_limit=a.max_gaussians,scope='Permission-cleared derivative model preview. Not a license grant for further reuse. Full original models are preserved locally.'))
    (a.out/'NOTICE.txt').write_text('Source reference: 지숭이_Jisoong — 체포하겠어🚨🚨\nhttps://www.youtube.com/shorts/rWS8uli1-m0\nDerivative3D/4D demonstration published with permission confirmed by the project maintainer on '+receipt['date']+'. Original footage/audio are not bundled. Further reuse rights are not specified.\nOur pipeline code: MIT. Third-party model/data terms remain separate; see labs/human-4d-gaussian/SOURCES.md. Browser model is a reduced preview, not an exact copy of the full learned Gaussian set.\n')


if __name__=='__main__':main()
