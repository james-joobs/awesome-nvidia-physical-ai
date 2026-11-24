import unittest
import numpy as np
from support import visible_depth_agreement

class ProjectionTests(unittest.TestCase):
    def test_ray_distance_and_occlusion(self):
        K=np.array([[1.,0,1],[0,1,1],[0,0,1]])
        depth=np.zeros((3,3));depth[1,1]=2;depth[1,2]=np.sqrt(8)
        points=np.array([[0,0,2],[2,0,2],[0,0,4],[0,0,-2],[99,0,2]])
        actual=visible_depth_agreement(points,np.eye(4),K,depth,0,.001)
        np.testing.assert_array_equal(actual,[True,True,False,False,False])
    def test_camera_translation(self):
        C=np.eye(4);C[0,3]=10;depth=np.ones((1,1))*3
        np.testing.assert_array_equal(visible_depth_agreement([[10,0,3],[0,0,3]],C,np.eye(3),depth,0,.001),[True,False])
    def test_invalid_depth_is_not_observation(self):
        self.assertFalse(visible_depth_agreement([[0,0,1]],np.eye(4),np.eye(3),np.array([[np.nan]]))[0])
if __name__=='__main__':unittest.main()
