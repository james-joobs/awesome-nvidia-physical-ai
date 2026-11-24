import math,unittest
from context import reset_reasons

def view(angle=0,x=0,frame=13,projection=None):
    return {'forward':[math.sin(math.radians(angle)),0,math.cos(math.radians(angle))],'camera':[x,0,3],'frame':frame,'variant':'guided','projection':projection or [64,1,1,.5]}

class ContextTests(unittest.TestCase):
    def test_smooth_orbit_keeps_context(self):self.assertEqual(reset_reasons(view(),view(3,.2)),[])
    def test_interactive_jump_does_not_reuse_old_car_pose(self):self.assertIn('camera_rotation',reset_reasons(view(),view(30)))
    def test_large_translation_resets(self):self.assertIn('camera_translation',reset_reasons(view(),view(x=1)))
    def test_resize_or_lens_change_resets(self):self.assertIn('projection_changed',reset_reasons(view(),view(projection=[30,1,1,.5])))
    def test_backward_seek_resets(self):self.assertIn('timeline_jump',reset_reasons(view(frame=13),view(frame=12)))
if __name__=='__main__':unittest.main()
