"""CPU checks for input preservation, package integrity and honest prerequisites."""
import copy,gzip,hashlib,importlib.util,json,shutil,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
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
