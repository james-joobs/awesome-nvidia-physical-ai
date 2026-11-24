"""CPU regressions for reviewed teachers, cache mapping and mask preservation.

All image, motion and video fixtures are synthetic. No checkpoint is loaded,
no source video is downloaded, and no GPU work is performed.
"""
import hashlib,importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
HAS_ARRAYS=all(importlib.util.find_spec(name) for name in ['numpy','PIL'])
HAS_MASKS=HAS_ARRAYS and importlib.util.find_spec('cv2') is not None

def module(name):
 spec=importlib.util.spec_from_file_location('audit_'+name,HERE/(name+'.py'));obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

class RecipeTests(unittest.TestCase):
 def fixture(self,root):
  helper=module('fresh_interval');root.mkdir(exist_ok=True)
  teachers=[root/'base.bin',root/'offset.bin']
  for i,p in enumerate(teachers):p.write_bytes(f'synthetic-teacher-{i}'.encode())
  spec={'excluded_base_cameras':[],'loss_sampling':'3:5;6:11','generator':{'seed':42},'input_inventory':[{'sha':'unchanged-source'}],'runtime_config_sha256':'runtime','source_code':{'helper':'unchanged'}}
  recipe=root/'recipe.json';helper.write(recipe,spec);state=root/'stages.json';helper.write(state,{'status':'awaiting_teacher_review','stages':{label:{'status':'complete','outputs':helper.inventory([path])} for label,path in zip(['views-base','views-offset'],teachers)}})
  return helper,spec,recipe,state,teachers
 def test_reviewed_exclusion_reuses_only_verified_teachers_and_preserves_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   helper,spec,recipe,state,teachers=self.fixture(Path(td));old=recipe.read_bytes();wanted={**spec,'excluded_base_cameras':[3],'loss_sampling':'3:4;6:10'};helper.preserve_or_update_recipe(recipe,wanted,state)
   self.assertEqual(json.loads(recipe.read_text()),wanted);saved=json.loads(state.read_text())['teacher_curation'][0];receipt=recipe.parent/saved['previous_recipe'];self.assertEqual(receipt.read_bytes(),old);self.assertEqual(saved['previous_recipe_sha256'],hashlib.sha256(old).hexdigest());self.assertEqual(teachers[0].read_bytes(),b'synthetic-teacher-0')
 def test_cannot_change_exclusions_after_fitting_starts(self):
  with tempfile.TemporaryDirectory() as td:
   helper,spec,recipe,state,_=self.fixture(Path(td));before=recipe.read_bytes();s=json.loads(state.read_text());s['stages']['seed20k']={'status':'running'};helper.write(state,s)
   with self.assertRaises(ValueError):helper.preserve_or_update_recipe(recipe,{**spec,'excluded_base_cameras':[3]},state)
   self.assertEqual(recipe.read_bytes(),before)
 def test_review_does_not_allow_new_generation_or_changed_cached_teacher(self):
  for changed in ['generator','input_inventory','runtime_config_sha256','source_code','teacher_bytes']:
   with self.subTest(changed=changed),tempfile.TemporaryDirectory() as td:
    helper,spec,recipe,state,teachers=self.fixture(Path(td));wanted={**spec,'excluded_base_cameras':[3]}
    if changed=='teacher_bytes':teachers[0].write_bytes(b'changed')
    else:wanted[changed]='different'
    with self.assertRaises(ValueError):helper.preserve_or_update_recipe(recipe,wanted,state)

@unittest.skipUnless(HAS_ARRAYS,'NumPy and Pillow are required for the seed data helper')
class SeedPlanTests(unittest.TestCase):
 def test_relabel_of_cached_seed_data_is_rejected_before_pixels_change(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);images=root/'data/images/03';images.mkdir(parents=True);pixels=images/'000000.jpg';pixels.write_bytes(b'old-camera-three-pixels');prior={'source_frames':list(range(121)),'explicitly_rejected_generated_camera_ids':[]};(root/'PROVENANCE.json').write_text(json.dumps(prior));before=pixels.read_bytes()
   with self.assertRaises(ValueError):module('seed_train').validate_data_plan(root,{'source_frames':list(range(121)),'excluded_generated_camera_ids':[3]})
   self.assertEqual(pixels.read_bytes(),before);self.assertFalse((root/'data-plan.json').exists())
 def test_actual_seed_cli_rejects_relabel_before_gpu_imports_or_pixel_writes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);case=root/'multiview-prior/s01';out=case/'reconstruction';images=out/'data/images/03';images.mkdir(parents=True);pixels=images/'000000.jpg';pixels.write_bytes(b'previous-teacher-three');source_ids=list(range(121));(case/'adapter.json').write_text(json.dumps({'source_frames':source_ids,'source_crop':{}}));(case/'generation.json').write_text('{}');(case/'soma-conditioning.npz').write_bytes(b'fingerprinted-only');(out/'PROVENANCE.json').write_text(json.dumps({'source_frames':source_ids,'explicitly_rejected_generated_camera_ids':[]}))
   result=subprocess.run([sys.executable,str(HERE/'seed_train.py'),'--root',str(root),'--name','s01','--exclude-generated-cameras','3','--prepare-only'],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('camera exclusion/slot mapping',result.stderr);self.assertNotIn('No module named',result.stderr);self.assertEqual(pixels.read_bytes(),b'previous-teacher-three');self.assertFalse((out/'data-plan.json').exists())
 def test_matching_plan_resumes_but_different_generation_does_not(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);helper=module('seed_train');plan={'source_frames':list(range(121)),'excluded_generated_camera_ids':[3],'generation_sha256':'first'};helper.validate_data_plan(root,plan);helper.validate_data_plan(root,plan)
   with self.assertRaises(ValueError):helper.validate_data_plan(root,{**plan,'generation_sha256':'second'})

@unittest.skipUnless(HAS_MASKS,'NumPy, Pillow and OpenCV are required for synthetic mask regressions')
class MaskTests(unittest.TestCase):
 def fixture(self,root):
  import numpy as np
  from PIL import Image
  T,H,W=123,960,540;names=[f'Joint{i}' for i in range(77)]
  for i,n in enumerate(['Head','HeadEnd','Jaw','LeftEye','RightEye'],6):names[i]=n
  for side,start in [('Left',14),('Right',42)]:
   for j in range(25):names[start+j]=side+'Hand'+('' if j==0 else f'Finger{j}')
  # Deliberately move head joints away from positions6/7. The metadata remains
  # consistent with this synthetic geometry; the repair must use their names.
  names[6],names[70]=names[70],names[6];names[7],names[71]=names[71],names[7]
  joints=np.tile(np.array([-.4,.6,1.],np.float32),(T,77,1));head=np.array([0.,-.36,1.],np.float32)
  for i,n in enumerate(names):
   if n in ['Head','HeadEnd','Jaw','LeftEye','RightEye']:joints[:,i]=head
   elif n.startswith(('LeftHand','RightHand')):joints[:,i]=[0.,.24,1.]
  K=np.tile(np.array([[500.,0,270],[0,500,480],[0,0,1.]],np.float32),(T,1,1));corners=np.array([[x,y,z] for x in [-.02,.02] for y in [-.02,.02] for z in [-.02,.02]],np.float32);vertices=np.tile((head+corners)[None],(T,1,1))
  for folder in ['rig','frames','masks']:(root/folder).mkdir()
  np.savez_compressed(root/'rig/geometry.npz',joints=joints,K=K,vertices=vertices);(root/'rig/rig.json').write_text(json.dumps({'public_joint_names':names}));(root/'input.json').write_text(json.dumps({'frames':T,'width':W,'height':H}));(root/'input.mp4').write_bytes(b'synthetic-source-fingerprint-only')
  image=np.full((H,W,3),[30,145,70],np.uint8);base=np.zeros((H,W),np.uint8);base[180:420,180:360]=255;base[420:850,230:310]=255;bad=base.copy();bad[270:330,240:300]=0
  for i in range(T):Image.fromarray(image).save(root/f'frames/{i+1:06d}.jpg');Image.fromarray(bad if i==61 else base).save(root/f'masks/{i+1:06d}.png')
  case=root/'multiview-prior/s01';case.mkdir(parents=True);ids=np.arange(121);np.savez_compressed(case/'soma-conditioning.npz',frame_ids=ids,world_origin=np.zeros(3));(case/'adapter.json').write_text(json.dumps({'source_frames':ids.tolist(),'source_crop':{'left':0,'top':0,'width':W,'height':H}}))
  originals=root/'roi/source-frames';originals.mkdir(parents=True)
  for t in range(121):Image.fromarray(image).save(originals/f'{t+1:06d}.png')
  request={'source_frame_ids':ids.tolist(),'size':[W,H],'source_sha256':hashlib.sha256((root/'input.mp4').read_bytes()).hexdigest()};(originals.parent/'frame-request.json').write_text(json.dumps(request))
  data=root/'selected-data';data.mkdir();observed=[0,5,6,13,14,15];cameras=[]
  for cid in range(16):
   matrix=np.eye(4)
   if cid not in observed:matrix[0,3]=cid+1
   cameras.append({'camera_id':cid,'K':K[0].tolist(),'camera_to_world':matrix.tolist(),'image_width':704,'image_height':1280,'supervision':'observed' if cid in observed else 'generated'})
   (data/f'images/{cid:02}').mkdir(parents=True);folder=data/f'fmasks/{cid:02}';folder.mkdir(parents=True);Image.fromarray(bad if cid in observed else np.full((H,W),73,np.uint8)).resize((704,1280)).save(folder/'000061.png')
  (data/'cameras.json').write_text(json.dumps({'cameras':cameras}));(data/'metadata.json').write_text(json.dumps({'source_identity':'synthetic regression only'}));return originals,data,observed
 def run_repair(self,root,originals,data,out):
  return subprocess.run([sys.executable,str(HERE/'repair_foreground.py'),'--root',str(root),'--name','s01','--frame','61','--data',str(data),'--original-frames',str(originals),'--out',str(out)],capture_output=True,text=True)
 def test_named_head_repair_updates_all_six_copies_without_changing_inputs(self):
  import numpy as np
  from PIL import Image
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);originals,data,observed=self.fixture(root);before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()};out=root/'repair';result=self.run_repair(root,originals,data,out);self.assertEqual(result.returncode,0,result.stderr)
   report=json.loads((out/'PREPARED.json').read_text());self.assertEqual(report['observed_cameras_corrected'],observed);self.assertEqual(report['head_joint_names'],['Head','HeadEnd']);self.assertGreater(report['changed_working_pixels'],0);corrected=np.asarray(Image.open(out/'corrected-mask/000062.png'));self.assertTrue((corrected[270:330,240:300]>0).all())
   copies=[(out/f'data/fmasks/{i:02}/000061.png').read_bytes() for i in observed];self.assertTrue(all(x==copies[0] for x in copies))
   for i in set(range(16))-set(observed):self.assertEqual((out/f'data/fmasks/{i:02}/000061.png').read_bytes(),(data/f'fmasks/{i:02}/000061.png').read_bytes())
   for p,h in before.items():self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),h,str(p))
 def test_wrong_original_interval_cache_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);originals,data,_=self.fixture(root);receipt=originals.parent/'frame-request.json';request=json.loads(receipt.read_text());request['source_frame_ids'][0]=1;receipt.write_text(json.dumps(request));result=self.run_repair(root,originals,data,root/'repair');self.assertNotEqual(result.returncode,0);self.assertIn('different source/window',result.stderr);self.assertFalse((root/'repair').exists())
 def test_mask_review_flags_synthetic_head_hole_and_never_edits_masks(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);self.fixture(root);before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'masks').glob('*.png')};out=root/'diagnostics';result=subprocess.run([sys.executable,str(HERE/'inspect_masks.py'),'--root',str(root),'--out',str(out),'--max-contacts','1'],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr);report=json.loads((out/'coverage.json').read_text());self.assertEqual([r['frame'] for r in report['flagged_frames']],[61]);self.assertFalse(report['source_masks_modified'])
   for p,h in before.items():self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),h)

@unittest.skipUnless(HAS_ARRAYS and shutil.which('ffmpeg'),'Pillow and FFmpeg are required for teacher contact regressions')
class ContactTests(unittest.TestCase):
 def test_complete_synthetic_contact_remains_manual_review_only(self):
  from PIL import Image
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'bin').mkdir();(root/'bin/ffmpeg').symlink_to(shutil.which('ffmpeg'));video=root/'complete.mp4';subprocess.run([shutil.which('ffmpeg'),'-v','error','-f','lavfi','-i','color=c=green:s=64x96:r=30','-frames:v','121','-c:v','libx264',str(video)],check=True);case=root/'multiview-prior/s01';case.mkdir(parents=True);(case/'generation.json').write_text(json.dumps({'target_videos':[str(video)]*6}));(case/'adapter.json').write_text(json.dumps({'source_frames':list(range(121)),'cameras':[{'yaw_degrees':i*60} for i in range(6)]}));contact=root/'contact.jpg';result=subprocess.run([sys.executable,str(HERE/'inspect_teachers.py'),'--root',str(root),'--name','s01','--out',str(contact)],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
   with Image.open(contact) as picture:self.assertEqual(picture.size,(1584,1524))
   self.assertIn('MANUAL_REVIEW_ONLY',result.stdout)
 def test_incomplete_video_cannot_be_reported_as_complete_three_time_review(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'bin').mkdir();(root/'bin/ffmpeg').symlink_to(shutil.which('ffmpeg'));video=root/'short.mp4';subprocess.run([shutil.which('ffmpeg'),'-v','error','-f','lavfi','-i','color=c=green:s=64x96:r=30','-frames:v','60','-c:v','libx264',str(video)],check=True);case=root/'multiview-prior/s01';case.mkdir(parents=True);(case/'generation.json').write_text(json.dumps({'target_videos':[str(video)]*6}));(case/'adapter.json').write_text(json.dumps({'source_frames':list(range(121)),'cameras':[{'yaw_degrees':i*60} for i in range(6)]}));result=subprocess.run([sys.executable,str(HERE/'inspect_teachers.py'),'--root',str(root),'--name','s01','--out',str(root/'contact.jpg')],capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertIn('missing requested',result.stderr);self.assertFalse((root/'contact.jpg').exists())

if __name__=='__main__':unittest.main()
