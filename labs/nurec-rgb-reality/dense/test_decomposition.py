"""Geometry/provenance regressions for the new foreground split."""
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
import numpy as np
from fuse import decode_mask

class DecompositionTest(unittest.TestCase):
    def test_non_square_rle_layout(self):
        image=np.asarray(decode_mask({'size':[3,2],'counts':[1,2,2,1],'origin':[1,1],'extent':[3,2]},(5,4)))
        np.testing.assert_array_equal(image[1:3,1:4]>0,[[False,True,True],[False,False,True]])
        self.assertFalse(image[0].any())

    def test_two_view_support_and_depth_protect_background(self):
        for views,removed in [(1,0),(2,1)]:
            with self.subTest(views=views),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);names=['x','y','z','opacity'];data=np.zeros(3,dtype=[(n,'<f4') for n in names]);data['z']=[2,6,2];data['x']=[0,0,2];data['opacity']=[.3,.5,.7]
                header='ply\nformat binary_little_endian 1.0\nelement vertex 3\n'+''.join('property float '+n+'\n' for n in names)+'end_header\n';(root/'input.ply').write_bytes(header.encode()+data.tobytes())
                fg=np.zeros((102,4,4),bool);fg[:views,2,2]=True
                K=np.repeat(np.array([[[6,0,6],[0,6,6],[0,0,1]]]),102,axis=0)
                np.savez(root/'input.npz',depth=np.full((102,4,4),2.),foreground=fg,intrinsics=K,poses=np.repeat(np.eye(4)[None],102,axis=0))
                subprocess.run([sys.executable,str(Path(__file__).with_name('mask_gaussians.py')),'--ply',str(root/'input.ply'),'--cache-input',str(root/'input.npz'),'--out',str(root/'out')],check=True,stdout=subprocess.DEVNULL)
                report=json.loads((root/'out/result.json').read_text());self.assertEqual(report['removed_gaussians'],removed)
                raw=(root/'out/static-background.ply').read_bytes().split(b'end_header\n',1)[1]
                np.testing.assert_array_equal(np.frombuffer(raw,dtype=data.dtype),data[removed:])

if __name__=='__main__':unittest.main()
