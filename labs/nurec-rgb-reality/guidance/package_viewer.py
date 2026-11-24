"""Package a guided model alongside a completed parent viewer for local use."""
import argparse, gzip, hashlib, json, shutil, struct
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--root',type=Path,required=True);a=p.parse_args();root=a.root
    source=a.base/'viewer';out=root/'viewer'
    if not (source/'road.spz').is_file():raise SystemExit('Complete the parent pipeline export stage first; it supplies RGB previews, cameras, policy and the baseline model.')
    shutil.copytree(source,out,dirs_exist_ok=True);shutil.copyfile(root/'guided.spz',out/'guided.spz')
    shared=Path(__file__).resolve().parents[2]/'rgb-reality-view'
    for name in ['viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js']:
        shutil.copyfile(shared/name,out/name)
    export=json.loads((root/'exported.json').read_text())
    guidance={'schema':1,'default':'guided','chase_offset':[-3.4,-1.8,1.0],'variants':[
        {'id':'guided','file':'guided.spz','gaussians':export['gaussians'],'sha256':export['sha256'],
         'label_en':'Depth-guided · dense seed / 32k steps','label_ko':'깊이 기반 · 조밀한 초기화 / 32,000단계',
         'note_en':'All-RGB production fit; denser seed and larger training budget. Not a loss-only comparison.',
         'note_ko':'전체 RGB로 학습한 표시용 모델입니다. 초기 점군과 학습량도 늘려 loss만 비교한 결과와 구분합니다.'},
        {'id':'original','file':'road.spz','label_en':'Original · 450k Gaussians','label_ko':'기존 · Gaussian 45만 개',
         'note_en':'Original all-RGB NuRec model; 16k steps, no geometric guidance.',
         'note_ko':'기하 제약 없이 전체 RGB로 16,000단계 학습한 기존 NuRec 모델입니다.'}]}
    for v in guidance['variants']:
        v['sha256']=hashlib.file_digest((out/v['file']).open('rb'),'sha256').hexdigest()
        with gzip.open(out/v['file'],'rb') as f:v['gaussians']=struct.unpack('<III',f.read(12))[2]
    (out/'guidance.json').write_text(json.dumps(guidance,ensure_ascii=False,indent=2)+'\n')
    config=json.loads((out/'cameras.json').read_text());config['guidance_file']='guidance.json';(out/'cameras.json').write_text(json.dumps(config,indent=2)+'\n')
    print('GUIDED_VIEWER_READY',flush=True)


if __name__=='__main__':main()
