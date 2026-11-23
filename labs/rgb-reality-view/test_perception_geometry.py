import unittest
from perception_geometry import ground_contact,rle_encode,associate

class PerceptionGeometry(unittest.TestCase):
    def test_known_contact(self):
        p=ground_contact([60,50],[[100,0,50],[0,100,50],[0,0,1]],[[1,0,0],[0,-1,0],[0,0,-1]],[0,0,1])
        self.assertEqual(p,[.1,0.,0.])
    def test_horizon_and_behind_rejected(self):
        self.assertIsNone(ground_contact([50,50],[[100,0,50],[0,100,50],[0,0,1]],[[1,0,0],[0,1,0],[0,0,1]],[0,0,1]))
    def test_far_contact_rejected(self):
        self.assertIsNone(ground_contact([10000,50],[[100,0,50],[0,100,50],[0,0,1]],[[1,0,0],[0,-1,0],[0,0,-1]],[0,0,1]))
    def test_mask_rle_roundtrip(self):
        bits=[1,1,0,0,1,0,1];counts=rle_encode(bits);decoded=[]
        for i,n in enumerate(counts):decoded.extend([i%2]*n)
        self.assertEqual(bits,decoded)
    def test_merge_only_across_cameras_and_do_not_extrapolate(self):
        def d(cam,x):return dict(camera=cam,ground_position=[x,0,0],score=.9,**{'class':'car'})
        a,b,c=d('front',0),d('left',.1),d('front',.2)
        frames=[{'views':{'a':{'detections':[a,c]},'b':{'detections':[b]}}},{'views':{'a':{'detections':[d('front',.15)]}}},{'views':{}}]
        associate(frames)
        self.assertEqual(len(frames[0]['objects']),2)
        self.assertEqual(a['track_id'],b['track_id'])
        self.assertEqual(len(frames[2]['objects']),0)

if __name__=='__main__':unittest.main()
