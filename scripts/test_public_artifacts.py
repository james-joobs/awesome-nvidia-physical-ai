"""Regression tests for leaks hidden in published formats."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from PIL import Image, PngImagePlugin
from pxr import Sdf

spec = importlib.util.spec_from_file_location("publication", Path(__file__).with_name("check-public-artifacts.py"))
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


def private_path():
    return "/".join(("", "home", "example-user", "private-run", "source.blend"))


class PublicationTests(unittest.TestCase):
    def test_debug_strings_in_binary_model(self):
        data = b"\x08\x01" + private_path().encode() + b"\x00"
        self.assertTrue(publication.inspect_bytes(data, "policy.onnx"))

    def test_compressed_png_metadata_is_inspected(self):
        stream = io.BytesIO()
        info = PngImagePlugin.PngInfo()
        info.add_text("File", private_path(), zip=True)
        Image.new("RGB", (8, 8), "white").save(stream, format="PNG", pnginfo=info)
        self.assertNotIn(private_path().encode(), stream.getvalue())
        self.assertTrue(publication.inspect_bytes(stream.getvalue(), "input.png"))

    def test_hardware_identifier_and_machine_fields(self):
        identifier = "GPU-" + "12345678-1234-1234-1234-123456789abc"
        self.assertTrue(publication.inspect_bytes(json.dumps({"detail": identifier}).encode(), "receipt.json"))
        self.assertTrue(publication.inspect_bytes(b'{"host":"example-private-node"}', "receipt.json"))
        self.assertFalse(publication.inspect_bytes(b'{"gpu":"RTX 5090","status":"success"}', "receipt.json"))

    def test_private_name_in_markdown(self):
        self.assertTrue(publication.inspect_bytes(b"Executed on example-private-node.", "guide.md", names=[b"example-private-node"]))

    def test_nested_archive_metadata(self):
        image = io.BytesIO()
        info = PngImagePlugin.PngInfo(); info.add_text("File", private_path(), zip=True)
        Image.new("RGB", (8, 8), "white").save(image, format="PNG", pnginfo=info)
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("images/input.png", image.getvalue())
        self.assertTrue(publication.inspect_bytes(data.getvalue(), "scene.zip"))

    def test_binary_usd_layer_documentation(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "scene.usdc"
            layer = Sdf.Layer.CreateNew(str(file)); layer.documentation = private_path(); layer.Save()
            self.assertTrue(publication.inspect_bytes(file.read_bytes(), "scene.usdc"))

    def test_bad_archives_fail_instead_of_passing(self):
        with self.assertRaises(zipfile.BadZipFile):
            publication.inspect_bytes(b"not a zip", "scene.zip")


if __name__ == "__main__":
    unittest.main()
