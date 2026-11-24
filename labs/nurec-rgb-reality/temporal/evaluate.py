"""Matched optical-flow stability proxies, not unseen-view accuracy or safety."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import cv2
import numpy as np

def backward_map(previous,current):
    gray=lambda x:cv2.cvtColor(x,cv2.COLOR_RGB2GRAY)
    args=(None,.5,4,21,4,7,1.5,cv2.OPTFLOW_FARNEBACK_GAUSSIAN)
    backward=cv2.calcOpticalFlowFarneback(gray(current),gray(previous),*args)
    forward=cv2.calcOpticalFlowFarneback(gray(previous),gray(current),*args)
    h,w=current.shape[:2];yy,xx=np.mgrid[:h,:w].astype(np.float32);mx=xx+backward[...,0];my=yy+backward[...,1]
    inverse=cv2.remap(forward,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    valid=(mx>=1)&(my>=1)&(mx<w-2)&(my<h-2)&(np.linalg.norm(backward+inverse,axis=-1)<1.5)
    return mx,my,valid

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--independent',type=Path,required=True);p.add_argument('--temporal',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    modes={k:json.loads((getattr(a,k)/'result.json').read_text()) for k in ['independent','temporal']}
    x,y=modes['independent'],modes['temporal']
    if x['mode']!='independent' or y['mode']!='temporal' or x['checkpoint_sha256']!=y['checkpoint_sha256']:raise ValueError('Compare the same checkpoint in independent and temporal modes')
    if [r['input_sha256'] for r in x['records']]!=[r['input_sha256'] for r in y['records']]:raise ValueError('The two runs did not receive identical ordered source frames')
    if len(x['records'])<6 or not any(r['history_frames']==4 for r in y['records']):raise ValueError('No actual temporal-context inference was completed')
    def image(path):
        bgr=cv2.imread(str(path))
        if bgr is None:raise ValueError(f'Missing image: {path}')
        return cv2.cvtColor(cv2.resize(bgr,(512,288),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2RGB)
    records=[];previous=None
    for i,row in enumerate(x['records']):
        source=a.input/row['input']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=row['input_sha256']:raise ValueError('A source frame changed after inference')
        frames={'native':image(source),**{k:image(getattr(a,k)/modes[k]['records'][i]['output']) for k in modes}}
        if previous is not None and not y['records'][i]['cut_reset']:
            mx,my,valid=backward_map(previous['native'],frames['native']);scores={}
            for k,frame in frames.items():
                warped=cv2.remap(previous[k],mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
                error=np.abs(frame.astype(np.float32)-warped)/255
                scores[k]={'flow_warp_l1':float(error[valid].mean()) if valid.any() else None,'edge_magnitude':float(np.abs(cv2.Laplacian(cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY),cv2.CV_32F)).mean()/255)}
            records.append({'frame':i,'valid_fraction':float(valid.mean()),'actual_history_frames':y['records'][i]['history_frames'],'scores':scores})
        previous=frames
    contextual=[r for r in records if r['actual_history_frames']==4 and r['valid_fraction']>.1]
    if not contextual:raise ValueError('No valid matched temporal pairs')
    summary={k:{'flow_warp_l1':float(np.mean([r['scores'][k]['flow_warp_l1'] for r in contextual])),'edge_magnitude':float(np.mean([r['scores'][k]['edge_magnitude'] for r in contextual]))} for k in ['native','independent','temporal']}
    report={'schema':1,'frames':len(x['records']),'contextual_pairs':len(contextual),'checkpoint_sha256':x['checkpoint_sha256'],'summary':summary,'method':'Shared backward Farneback flow from the native input; forward/backward round-trip threshold1.5px at512x288; same valid pixels for all modes. Cuts and context-free startup frames excluded from summary.','scope':'Temporal stability proxy; not ground-truth depth, novel-view fidelity, object correctness, or driving safety. Blur or frozen output can reduce warp error; inspect edge sharpness and actual camera response alongside it.','timing':{k:{n:modes[k][n] for n in ['model_median_seconds_after_frame4','model_p95_seconds_after_frame4','peak_allocated_gib']} for k in modes},'pairs':records}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
