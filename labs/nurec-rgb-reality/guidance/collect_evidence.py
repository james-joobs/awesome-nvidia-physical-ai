"""Collect portable numeric evidence, excluding runtime logs and machine paths."""
import argparse, hashlib, json, shutil
from pathlib import Path
import numpy as np


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--production',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=a.root;out=a.output;out.mkdir(parents=True,exist_ok=True)
    def write(name,data):(out/name).write_text(json.dumps(data,indent=2)+'\n')
    shutil.copyfile(root/'comparison.json',out/'comparison.json')
    report=json.loads((root/'priors-base.json').read_text())
    summary={k:v for k,v in report.items() if k!='frames'}
    summary['median_sfm_fit_relative_error']=float(np.median([r['median_relative_error'] for r in report['frames']]))
    summary['alignment_metric_scope']='Residual on training correspondences used by the robust fit, not independent depth accuracy'
    summary['median_valid_depth_fraction']=float(np.median([r['valid_depth_fraction'] for r in report['frames']]))
    write('priors-summary.json',summary)
    rows=json.loads((root/'rgb-cameras.json').read_text())['frames'];r=next(r for r in rows if r['image']=='front_camera/39.jpg');C=np.array(r['camera_to_world']);K=np.array(r['K']);u,v=512,450
    with np.load(root/'priors-base'/r['camera']/f"{r['timestamp_us']}.npz") as z:distance=float(z['distance'][v,u]);normal=z['normals'][v,u].tolist()
    ray=np.array([(u-K[0,2])/K[0,0],(v-K[1,2])/K[1,1],1]);zdepth=distance/np.linalg.norm(ray);position=C[:3,3]+C[:3,:3]@(ray*zdepth)
    write('input-output-sample.json',{'image':r['image'],'image_sha256':r['sha256'],'rgb_shape':[r['height'],r['width'],3],'pixel_uv':[u,v],
        'K':K.tolist(),'ray_distance_relative_units':distance,'z_depth_relative_units':float(zdepth),'world_normal':normal,'world_position_relative_units':position.tolist(),
        'native_label_shapes':{'distance':[1,r['height'],r['width'],1],'normal':[1,r['height'],r['width'],3]},
        'scope':'Actual training-pixel prediction; relative units, not measured meters; normal derived from the same predicted depth'})
    receipts={}
    for f in sorted((root/'results').glob('*.json')):
        r=json.loads(f.read_text());receipts[r['case']]={k:v for k,v in r.items() if k not in ['artifact','overrides']}
    write('matched-runs.json',receipts)
    if a.production:
        r=json.loads((a.production/'results/depth.json').read_text())
        write('production-model.json',{'training':{k:v for k,v in r.items() if k not in ['artifact','overrides']},
            'split':json.loads((a.production/'split.json').read_text()),'seed':json.loads((a.production/'dense-seed.json').read_text()),
            'export':json.loads((a.production/'exported.json').read_text()),
            'comparison_scope':'All-RGB production fit with denser initialization, more steps and a larger Gaussian budget. Not a loss-only ablation or an independent held-out score.'})
    print('GUIDANCE_EVIDENCE_COLLECTED',flush=True)


if __name__=='__main__':main()
