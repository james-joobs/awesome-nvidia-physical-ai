import unittest
import numpy as np
from export_viewer import align_to_reference


class AlignmentTests(unittest.TestCase):
    def test_recovers_one_global_similarity_without_per_frame_correction(self):
        p=np.repeat(np.eye(4)[None],5,axis=0);p[:,:3,3]=[[0,0,0],[1,0,0],[2,.1,0],[3,.3,.1],[4,.4,.2]]
        R=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
        ref=p.copy();ref[:,:3,:3]=R;ref[:,:3,3]=p[:,:3,3]@R.T*3+[10,-4,2]
        actual,scale,report=align_to_reference(p,ref)
        np.testing.assert_allclose(actual,ref,atol=1e-12);self.assertAlmostEqual(scale,3);self.assertLess(report['camera_center_rmse_percent_path'],1e-10)

    def test_does_not_hide_local_camera_error(self):
        p=np.repeat(np.eye(4)[None],4,axis=0);p[:,2,3]=np.arange(4);ref=p.copy();p[2,0,3]=1
        _,_,report=align_to_reference(p,ref);self.assertGreater(report['camera_center_rmse_reference_units'],.4)

    def test_rejects_unidentifiable_scale(self):
        p=np.repeat(np.eye(4)[None],3,axis=0)
        with self.assertRaises(ValueError):align_to_reference(p,p)


if __name__=='__main__':unittest.main()
