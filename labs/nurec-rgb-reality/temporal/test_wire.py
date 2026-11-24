import io
import unittest
from unittest.mock import patch
from PIL import Image
from wire import encode_preview


class WireTests(unittest.TestCase):
    def test_encoding_preserves_every_rgb_byte(self):
        image = Image.frombytes('RGB', (32, 16), bytes((i * 73) % 256 for i in range(32 * 16 * 3)))
        for execution in ('baseline', 'exact', 'tuned'):
            with self.subTest(execution=execution):
                mime, raw = encode_preview(image, execution)
                self.assertIn(mime, ('image/png', 'image/webp'))
                self.assertEqual(Image.open(io.BytesIO(raw)).convert('RGB').tobytes(), image.tobytes())

    def test_missing_webp_uses_lossless_png(self):
        image = Image.new('RGB', (8, 8), (3, 127, 250))
        with patch('wire.features.check', return_value=False):
            mime, raw = encode_preview(image, 'exact')
        self.assertEqual(mime, 'image/png')
        self.assertEqual(Image.open(io.BytesIO(raw)).tobytes(), image.tobytes())
