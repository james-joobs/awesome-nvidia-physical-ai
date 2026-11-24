"""CPU checks for input preservation, package integrity and honest prerequisites."""
import copy,gzip,hashlib,importlib.util,json,shutil,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('human_pipeline',HERE/'pipeline.py');pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)


def fixture(root):
 data=root/'data';data.mkdir();files={}
 values={'gaussians.f32.gz':struct.pack('<14f',0,0,1,.01,.01,.01,0,0,0,1,.8,.5,.5,.5),'motion.f32.gz':struct.pack('<4f',.1,0,0,0),'variance.f32.gz':struct.pack('<4f',100,0,0,0),'sh.f16.gz':struct.pack('<48e',*([0]*48))}
 for name,raw in values.items():
  (data/name).write_bytes(gzip.compress(raw));files[name]={'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest()}
 meta={'gaussians':1,'frames':1,'fps':1,'duration':1,'files':files,'parity_samples':[{'index':0,'time':0,'position':[0,0,1],'opacity':.8}]};(data/'meta.json').write_text(json.dumps(meta));(root/'source.mp4').write_bytes(b'nonempty-test-only-media')
 m={'duration':1,'source':{'url':'source.mp4'},'segments':[{'id':'test','start':0,'duration':1,'root':'data/'}]};(root/'manifest.json').write_text(json.dumps(m));return m


class PackageTests(unittest.TestCase):
 def test_valid_numeric_package_is_read_only(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);fixture(root);before=sorted(str(p.relative_to(root)) for p in root.rglob('*'));r=pipeline.check_package(root,True);self.assertTrue(r['pass']);self.assertEqual(before,sorted(str(p.relative_to(root)) for p in root.rglob('*')));self.assertEqual(r['videos_fully_decoded'],[])
 def test_reject_path_escape(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);m=fixture(root);m['segments'][0]['root']='../outside';(root/'manifest.json').write_text(json.dumps(m))
   with self.assertRaises(ValueError):pipeline.check_package(root)
 def test_reject_changed_array(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);fixture(root);(root/'data/motion.f32.gz').write_bytes(gzip.compress(struct.pack('<4f',.2,0,0,0)))
   with self.assertRaises(AssertionError):pipeline.check_package(root)
 def test_deep_check_rejects_nonfinite_half_precision_colors(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);fixture(root);raw=struct.pack('<48e',float('nan'),*([0]*47));path=root/'data/sh.f16.gz';path.write_bytes(gzip.compress(raw));meta_path=root/'data/meta.json';meta=json.loads(meta_path.read_text());meta['files']['sh.f16.gz']['raw_sha256']=hashlib.sha256(raw).hexdigest();meta_path.write_text(json.dumps(meta))
   with self.assertRaisesRegex(ValueError,'Nonfinite values in sh.f16.gz'):pipeline.check_package(root,True)
 def test_reject_empty_timeline(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'manifest.json').write_text(json.dumps({'segments':[]}))
   with self.assertRaises(ValueError):pipeline.check_package(root)
 def test_control_asset_native_parity(self):
  sample=HERE.parents[1]/'site/public/showcase/human-4d-control'
  if not (sample/'manifest.json').exists():self.skipTest('Published control package not present in this checkout')
  before=hashlib.sha256((sample/'checks.json').read_bytes()).hexdigest() if (sample/'checks.json').exists() else None;r=pipeline.check_package(sample,True);self.assertLess(r['segments'][0]['native_numeric_max_position_error'],1e-4)
  after=hashlib.sha256((sample/'checks.json').read_bytes()).hexdigest() if (sample/'checks.json').exists() else None;self.assertEqual(before,after)


class RunnerTests(unittest.TestCase):
 def extension_fixture(self,root,fail_at=None):
  # Stub only the expensive training subprocess. These tests establish timeline
  # and preservation behavior; they do not claim to train a Gaussian model.
  (root/'seed.npz').write_bytes(b'preserved-seed-fixture');(root/'input.json').write_text(json.dumps({'frames':957}))
  initial={'segments':[{'id':'s00','start_frame':0,'valid_frames':121,'model':'seed.npz','sha256':pipeline.sha(root/'seed.npz')}],'covered_frames':121};(root/'models.json').write_text(json.dumps(initial))
  args=SimpleNamespace(root=root,config=None,package_dir=None,mode='reconstruction',stage='extend');runner=pipeline.Runner(args);runner.workspace=lambda:None
  calls=[]
  def trained_interval(runtime,script,*argv):
   options=dict(zip(argv[::2],argv[1::2]));start=int(options['--start']);name=options['--name'];case=root/'multiview-prior'/name;case.mkdir(parents=True);model=case/'final.npz';model.write_bytes(f'interval-fixture-{start}'.encode());flags=dict.fromkeys(pipeline.FRESH_STAGES,True)
   if start==fail_at:flags.pop('geometry')
   (case/'selected.json').write_text(json.dumps({'start_frame':start,'valid_frames':min(120,957-start),'actual_done_flags':flags,'final_model':str(model.relative_to(root)),'final_sha256':pipeline.sha(model)}));calls.append(start)
  runner.script=trained_interval
  return runner,initial,calls
 def test_full_extension_covers_real_frames_and_preserves_short_outputs(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);runner,initial,calls=self.extension_fixture(root);old_dir=runner.render_dir();old_dir.mkdir(parents=True);(old_dir/'comparison.mp4').write_bytes(b'old-short-render');runner.args.stage='render';old_journal=runner.journal_path();runner.args.stage='extend';runner.extend();m=runner.verify_models()
   self.assertEqual(calls,[120,240,360,480,600,720,840]);self.assertEqual([s['valid_frames'] for s in m['segments']],[120]*7+[117]);self.assertEqual(m['covered_frames'],957);self.assertEqual(sum(s['valid_frames'] for s in m['segments'])/m['fps'],31.9);self.assertEqual((root/'seed.npz').read_bytes(),b'preserved-seed-fixture');self.assertEqual((old_dir/'comparison.mp4').read_bytes(),b'old-short-render');self.assertNotEqual(old_dir,runner.render_dir());self.assertTrue(json.loads((root/'extension-progress.json').read_text())['complete']);runner.verify_stage('extend')
   runner.args.stage='render';self.assertNotEqual(old_journal,runner.journal_path());(root/m['segments'][1]['model']).write_bytes(b'changed');self.assertRaises(pipeline.PrerequisiteError,runner.verify_models)
 def test_partial_extension_never_publishes_a_full_timeline(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);runner,initial,calls=self.extension_fixture(root,fail_at=240)
   with self.assertRaises(pipeline.PrerequisiteError):runner.extend()
   self.assertEqual(json.loads((root/'models.json').read_text()),initial);progress=json.loads((root/'extension-progress.json').read_text());self.assertFalse(progress['complete']);self.assertEqual(len(progress['segments']),2)
 def test_extension_recovers_after_final_inventory_before_outer_journal(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);runner,initial,calls=self.extension_fixture(root);runner.extend();digest=pipeline.sha(root/'models.json');progress=json.loads((root/'extension-progress.json').read_text());progress['complete']=False;(root/'extension-progress.json').write_text(json.dumps(progress));runner.extend()
   self.assertEqual(len(calls),7);self.assertEqual(pipeline.sha(root/'models.json'),digest);self.assertTrue(json.loads((root/'extension-progress.json').read_text())['complete'])
 def test_changed_seed_stops_before_starting_expensive_intervals(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);runner,initial,calls=self.extension_fixture(root);(root/'seed.npz').write_bytes(b'changed-seed')
   with self.assertRaises(pipeline.PrerequisiteError):runner.extend()
   self.assertEqual(calls,[]);self.assertEqual(json.loads((root/'models.json').read_text()),initial)
 def test_cached_render_requires_verified_metadata_and_video_hash(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);runner,initial,calls=self.extension_fixture(root);out=runner.render_dir();out.mkdir(parents=True);(out/'comparison.mp4').write_bytes(b'not-a-video');(out/'rendered.json').write_text('{}')
   with self.assertRaises(pipeline.PrerequisiteError):runner.verify_stage('render')
 def test_setup_missing_environment_is_error(self):
  with tempfile.TemporaryDirectory() as tmp:
   result=subprocess.run([sys.executable,str(HERE/'pipeline.py'),'--root',tmp,'setup'],capture_output=True,text=True);self.assertEqual(result.returncode,2);self.assertIn('no runtimes have been installed',result.stderr);self.assertTrue((Path(tmp)/'runtime.json').exists());j=json.loads((Path(tmp)/'stages/reconstruction-setup.json').read_text());self.assertEqual(j['status'],'failed')
 def test_portrait_prepare_preserves_original(self):
  ffmpeg=shutil.which('ffmpeg')
  if not ffmpeg:self.skipTest('FFmpeg unavailable')
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);source=base/'own.mp4';subprocess.run([ffmpeg,'-v','error','-f','lavfi','-i','testsrc2=size=360x640:rate=30','-t','4.2','-c:v','libx264','-pix_fmt','yuv420p',str(source)],check=True);digest=hashlib.sha256(source.read_bytes()).hexdigest();out=base/'run';cmd=[sys.executable,str(HERE/'pipeline.py'),'--root',str(out),'prepare','--video',str(source)];subprocess.run(cmd,check=True,capture_output=True);self.assertEqual(hashlib.sha256((out/'original.mp4').read_bytes()).hexdigest(),digest);meta=json.loads((out/'input.json').read_text());self.assertEqual(meta['frames'],126);self.assertEqual(meta['width'],360);self.assertEqual(meta['height'],640);self.assertEqual(len(list((out/'frames').glob('*.jpg'))),126)
   (out/'frames/000001.jpg').unlink();bad=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(bad.returncode,2);self.assertIn('cache is incomplete',bad.stderr)

if __name__=='__main__':unittest.main()
