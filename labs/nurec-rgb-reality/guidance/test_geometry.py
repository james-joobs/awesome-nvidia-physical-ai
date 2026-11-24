"""Check geometric conventions and robust prior alignment against known surfaces."""
import unittest
import numpy as np
from geometry import align_depth, normals_from_z


class GeometryTests(unittest.TestCase):
    def test_scale_shift_with_outliers(self):
        x=np.linspace(.5,8,240);y=2.3*x+.7;y[::9]+=30
        a,b,_=align_depth(x,y)
        self.assertAlmostEqual(a,2.3,places=2)
        self.assertAlmostEqual(b,.7,places=2)

    def test_alignment_rejects_missing_correspondences(self):
        with self.assertRaises(ValueError):align_depth([1,np.nan,-1],[2,3,4])

    def test_front_plane_faces_the_camera(self):
        K=np.array([[100,0,4],[0,100,4],[0,0,1]],float)
        n,rays=normals_from_z(np.full((9,9),3.),K,np.ones((9,9),bool))
        np.testing.assert_allclose(n[4,4],[0,0,-1],atol=1e-6)
        np.testing.assert_allclose(rays[4,4],[0,0,1],atol=1e-6)
        self.assertTrue(np.all(n[0]==0))

    def test_sloped_plane_and_invalid_boundaries(self):
        K=np.array([[80,0,4],[0,80,4],[0,0,1]],float);yy,xx=np.mgrid[:9,:9]
        target=np.array([.2,.1,-1.]);target/=np.linalg.norm(target)
        rays=np.stack([(xx-4)/80,(yy-4)/80,np.ones((9,9))],axis=-1)
        depth=-3/(rays@target);valid=np.ones((9,9),bool)
        n,_=normals_from_z(depth,K,valid)
        np.testing.assert_allclose(n[4,4],target,atol=1e-6)
        valid[4,4]=False;n,_=normals_from_z(depth,K,valid)
        self.assertTrue(np.all(n[4,3:6]==0))
        self.assertTrue(np.all(n[3:6,4]==0))


if __name__=='__main__':unittest.main()
