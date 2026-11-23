"""Package the NuRec-exported Gaussian model, RGB perception and Alpamayo output.

NuRec trains on normalized RGB-derived coordinates; its world-space PLY therefore
already uses the viewer's relative coordinate frame. Do not apply COLMAP's
world-to-viewer normalization a second time. Third-party rasterization can differ
from the native NuRec renderer; the native before/after recordings are separate.
"""
import argparse,json,shutil,subprocess,gzip,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();root=a.root;lab=Path(__file__).resolve().parent;shared=lab.parent/'rgb-reality-view';out=root/'viewer';out.mkdir(exist_ok=True);source=root/'rig-source/viewer'
model=root/'gaussians/background/model.ply'
if not model.exists():raise RuntimeError('Run the official NuRec export-gaussian-plys command first')
subprocess.run(['npm','exec','--yes','--package=@playcanvas/splat-transform@3.12.0','--','splat-transform','-w',str(model),'--filter-harmonics','1',str(out/'road.spz'),'--spz-version','3'],check=True)
g=json.loads((source/'cameras.json').read_text());g['world_to_viewer']=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];g['backend']='NuRec 26.04';g['native_renderer']='NuRec gsplat';g['browser_renderer']='Spark / Three.js, converted 3DGS preview';g['trained_gaussians']=struct.unpack('<III',gzip.decompress((out/'road.spz').read_bytes())[:12])[2];g['reconstruction_title']='RGB only · NuRec';g['pipeline_notice']='NuRec-trained Gaussian preview in a browser rasterizer; native NuRec and Harmonizer outputs are recorded separately'
if (source/'perception.json').exists():shutil.copy2(source/'perception.json',out/'perception.json');shutil.copytree(source/'camera',out/'camera',dirs_exist_ok=True);g['perception_file']='perception.json'
policy=root/'alpamayo-result.json'
if policy.exists():
 full=json.loads(policy.read_text());(out/'alpamayo.json').write_text(json.dumps({'schema':1,'model':full['model'],'scope':full['scope'],'keyframes':full['keyframes']},separators=(',',':'))+'\n');g['policy_file']='alpamayo.json'
(out/'cameras.json').write_text(json.dumps(g,indent=2)+'\n')
for name in ['viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js']:shutil.copy2(shared/name,out/name)
shutil.copy2(shared/'assets/volvo-s90.glb',out/'volvo-s90.glb');shutil.copy2(shared/'assets/VEHICLE-LICENSE.txt',out/'VEHICLE-LICENSE.txt')
if (root/'PANDASET-DATA-LICENSE.txt').exists():shutil.copy2(root/'PANDASET-DATA-LICENSE.txt',out/'PANDASET-DATA-LICENSE.txt')
credit=(shared/'assets/EXAMPLE-ATTRIBUTION.txt').read_text().replace('3DGRUT learned a static scene.','NuRec learned a static scene using its 3DGUT preset.');credit+='\nNuRec 26.04 native reconstruction/rendering; browser preview converted with the official export-gaussian-plys command.\nHarmonizer comparison footage: Built on NVIDIA Cosmos; NVIDIA Open Model License.\nAlpamayo 2 Edge: actual source-RGB inference, adapted virtual-camera layout and assumed camera-height scale; no vehicle control.\n'
(out/'ATTRIBUTION.txt').write_text(credit);print('NUREC_BROWSER_READY',flush=True)
