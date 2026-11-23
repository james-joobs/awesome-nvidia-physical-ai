"""Ensure the public RGB-only boundary fails closed for mixed or changed inputs."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from input_guard import verify_rgb_inputs

class InputBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'images/camera').mkdir(parents=True)
        self.data = b'pixel-only fixture; decoding belongs to image ingestion'
        (self.root/'images/camera/000.jpg').write_bytes(self.data)
        self.manifest = dict(images=[dict(image='camera/000.jpg', sha256=hashlib.sha256(self.data).hexdigest())], external_sensor_inputs=[], supplied_camera_poses=False, supplied_intrinsics=False, supplied_depth=False, supplied_ground_plane=False)
        self.save()
    def tearDown(self):
        self.temp.cleanup()
    def save(self):
        (self.root/'input-manifest.json').write_text(json.dumps(self.manifest))
    def test_pixels_accepted(self):
        self.assertEqual(len(verify_rgb_inputs(self.root)['images']), 1)
    def test_depth_sidecar_rejected(self):
        (self.root/'images/depth.npy').write_bytes(b'depth must not enter reconstruction')
        with self.assertRaises(ValueError): verify_rgb_inputs(self.root)
    def test_pose_sidecar_rejected(self):
        (self.root/'images/camera/poses.json').write_text('{}')
        with self.assertRaises(ValueError): verify_rgb_inputs(self.root)
    def test_changed_pixels_rejected(self):
        (self.root/'images/camera/000.jpg').write_bytes(b'changed')
        with self.assertRaises(ValueError): verify_rgb_inputs(self.root)
    def test_external_calibration_rejected(self):
        self.manifest['supplied_intrinsics'] = True; self.save()
        with self.assertRaises(ValueError): verify_rgb_inputs(self.root)
    def test_escape_symlink_rejected(self):
        (self.root/'outside.jpg').write_bytes(self.data)
        path=self.root/'images/camera/000.jpg'; path.unlink(); path.symlink_to(self.root/'outside.jpg')
        with self.assertRaises(ValueError): verify_rgb_inputs(self.root)

if __name__ == '__main__': unittest.main()
