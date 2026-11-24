"""One-stage-at-a-time entry point for the RGB geometry guidance lab.

First complete the parent RGB reconstruction through the prepare/perceive
stages. Keep each comparison/production experiment in its own output folder.
"""
import argparse, os, subprocess
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--base',type=Path,required=True)
    p.add_argument('--production',action='store_true');p.add_argument('--variant',choices=['all','baseline','depth','depth-normal','depth-normal-soft'],default='all')
    p.add_argument('stage',choices=['setup','inputs','prepare','priors','dense','train','evaluate','export','package','serve']);a=p.parse_args()
    root=a.root.expanduser().resolve();base=a.base.expanduser().resolve();here=Path(__file__).resolve().parent;python=root/'.venv/bin/python'
    env={**os.environ,'NUREC_RGB_ROOT':str(root),'CUDA_VISIBLE_DEVICES':'0','OMP_NUM_THREADS':'8'}
    def run(args):subprocess.run([str(v) for v in args],check=True,env=env)
    if a.stage=='setup':run(['python3',here/'setup.py','--root',root])
    elif a.stage=='inputs':run([python,here/'make_inputs.py','--root',root,'--base',base,*(['--no-holdout'] if a.production else [])])
    elif a.stage=='prepare':run(['bash',here.parent/'run.sh','prepare'])
    elif a.stage=='priors':run(['flock',env.get('GPU_LOCK','/tmp/rgb-reality-view.gpu.lock'),python,here/'infer_priors.py','--root',root,'--perception',base/'rig-source/viewer/perception.json'])
    elif a.stage=='dense':run([python,here/'dense_seed.py','--root',root])
    elif a.stage=='train':
        if a.production and a.variant=='all':raise SystemExit('Choose a single --variant for the production model, e.g. depth.')
        run([python,here/'run_experiment.py','--root',root,'--variant',a.variant,*(['--steps','32000','--max-gaussians','1200000','--seed-file','seed-dense.ply','--no-render'] if a.production else [])])
    elif a.stage=='evaluate':run([python,here/'evaluate.py','--root',root,'--perception',base/'rig-source/viewer/perception.json'])
    elif a.stage=='export':
        if a.variant=='all':raise SystemExit('Choose a completed --variant to export.')
        run([python,here/'export_model.py','--root',root,'--variant',a.variant])
    elif a.stage=='package':run([python,here/'package_viewer.py','--root',root,'--base',base])
    elif a.stage=='serve':run(['python3',here.parent.parent/'rgb-reality-view/serve.py','--root',root/'viewer','--port','8093'])


if __name__=='__main__':main()
