"""Compare unenhanced NuRec renderings with held-out RGB at matched poses."""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, sobel


def ssim_map(a,b):
    def blur(x):return gaussian_filter(x,sigma=(1.5,1.5,0),truncate=3.5)
    ma,mb=blur(a),blur(b);va=blur(a*a)-ma*ma;vb=blur(b*b)-mb*mb;cov=blur(a*b)-ma*mb
    return (((2*ma*mb+.01**2)*(2*cov+.03**2))/((ma*ma+mb*mb+.01**2)*(va+vb+.03**2))).mean(axis=-1)


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--perception',type=Path);a=p.parse_args();root=a.root
    split=json.loads((root/'split.json').read_text());cameras=json.loads((root/'all-cameras.json').read_text())['frames']
    camera_meta={r['image']:r for r in cameras};detections={}
    if a.perception:
        for f in json.loads(a.perception.read_text())['frames']:
            for camera,v in f['views'].items():detections[(camera,Path(v['image']).stem)]=v['detections']
    cases=[]
    for folder in sorted((root/'evaluation').iterdir()):
        if not (folder/'views.json').exists():continue
        rows=[];receipt=json.loads((root/'results'/f'{folder.name}.json').read_text())
        for camera in json.loads((folder/'views.json').read_text()):
            candidates=sorted((folder/camera['camera']).rglob('*.png'))
            assert len(candidates)==len(camera['images']),f'Expected a single native RGB output per held-out view: {camera["camera"]}'
            for source,prediction in zip(camera['images'],candidates):
                reference=root/'rgb'/source;meta=camera_meta[source];assert meta['timestamp_us'] in split['held_out_timestamp_us']
                truth=np.asarray(Image.open(reference).convert('RGB'),np.float64)/255
                actual=np.asarray(Image.open(prediction).convert('RGB'),np.float64)/255
                assert truth.shape==actual.shape,'Never resize or crop one side to conceal a camera mismatch'
                error=(truth-actual)**2;mask=np.ones(truth.shape[:2],bool)
                for d in detections.get((camera['camera'],Path(source).stem),[]):
                    x0,y0,x1,y1=d['bbox'];mask[max(0,int(y0)-4):min(len(mask),int(math.ceil(y1))+4),max(0,int(x0)-4):min(mask.shape[1],int(math.ceil(x1))+4)]=False
                similarity=ssim_map(truth,actual)
                edge=np.mean([np.abs(sobel(truth,axis=k)-sobel(actual,axis=k)).mean() for k in [0,1]])
                rows.append({'image':source,'timestamp_us':meta['timestamp_us'],'psnr_db':-10*math.log10(max(float(error.mean()),1e-12)),
                    'ssim':float(similarity[5:-5,5:-5].mean()),'background_psnr_db':-10*math.log10(max(float(error[mask].mean()),1e-12)),
                    'background_ssim':float(similarity[mask].mean()),'background_fraction':float(mask.mean()),'rgb_gradient_mae':float(edge),
                    'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'native_render_sha256':hashlib.sha256(prediction.read_bytes()).hexdigest()})
        assert len(rows)==split['held_out_images']==24
        keys=['psnr_db','ssim','background_psnr_db','background_ssim','rgb_gradient_mae']
        means={k:float(np.mean([r[k] for r in rows])) for k in keys}
        cases.append({'case':folder.name,'training_steps':receipt['steps'],'gaussian_limit':receipt['gaussian_limit'],'loss_weights':receipt['loss_weights'],
            'training_seconds':receipt['training_seconds'],'artifact_sha256':receipt['artifact_sha256'],'views':len(rows),'mean_per_image':means,'frames':rows})
    report={'schema':1,'split':split,'comparison':'Same RGB-derived cameras, training-only re-triangulated/colorized seed, seed=42, held-out RGB timestamps, no Harmonizer or image enhancement',
        'metric_scope':'Per-image PSNR/SSIM averaged over all 24 matched native views. Background scores exclude detector road-user boxes; these are estimates, not ground-truth masks. Camera estimation uses all RGB views offline.',
        'ssim_definition':'RGB channels averaged; Gaussian sigma=1.5, truncate=3.5, C1=.01^2, C2=.03^2; full-image mean excludes a 5-pixel border',
        'cases':cases}
    (root/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    for case in cases:print(case['case'],json.dumps(case['mean_per_image']),flush=True)


if __name__=='__main__':main()
