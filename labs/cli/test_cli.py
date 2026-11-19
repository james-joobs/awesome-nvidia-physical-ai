"""No-GPU tests of process execution, evidence validation and failure persistence."""

import json
import math
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "cli.py"
HARNESS = runpy.run_path(str(CLI))


class HarnessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "labs").mkdir()
        (self.root / "labs/cli.py").write_bytes(CLI.read_bytes())
        # A real subprocess and synthetic, explicitly test-only data. No GPU imports.
        (self.root / "labs/fake.py").write_text('''import json,sys
from pathlib import Path
out=Path(sys.argv[1])
mode=sys.argv[2]
print("child output must stay out of JSON stdout")
if mode=="fail": sys.exit(7)
if mode=="marker":
    (out/"capture-failed").touch()
else:
    (out/"result.json").write_text(json.dumps({"frames":200,"particles":64,"displayed_particles":0,"mean_particle_displacement_m":1.2}))
''')
        scenarios = []
        for name in ("pass", "fail", "marker"):
            scenarios.append({"id": name, "title": name, "status": "runnable", "validator": "warp",
                              "evidence_mode": "test-only", "headless_evidence_mode": "test-only",
                              "command": ["{python}", "{root}/labs/fake.py", "{output}", name],
                              "headless_args": [], "sources": ["labs/fake.py"], "modules": []})
            # A non-empty list advertises headless support; our fake ignores this argument.
            scenarios[-1]["headless_args"] = ["--headless"]
        (self.root / "labs/scenarios.json").write_text(json.dumps({"scenarios": scenarios}))

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *args):
        result = subprocess.run([sys.executable, str(CLI), "--json", *map(str, args)], capture_output=True, text=True)
        self.assertFalse(result.stderr, result.stderr)
        return result.returncode, json.loads(result.stdout)

    def run_case(self, name, output):
        return self.cli("run", name, "--source", self.root, "--output", output,
                        "--python", sys.executable, "--headless")

    def test_success_integrity_and_output_collision(self):
        output = self.root / "run"
        code, result = self.run_case("pass", output)
        self.assertEqual((code, result["status"]), (0, "passed"))
        self.assertIn("child output", (output / "run.log").read_text())
        manifest = (output / "run.json").read_bytes()
        self.assertEqual(self.cli("verify", output)[0], 0)
        self.assertEqual(self.cli("preview", output)[1]["evidence_mode"], "test-only")
        self.assertEqual(self.run_case("pass", output)[0], 1)
        self.assertEqual(manifest, (output / "run.json").read_bytes())
        (output / "result.json").write_text("{}")
        code, result = self.cli("verify", output)
        self.assertEqual(code, 1)
        self.assertIn("SHA-256 changed", result["error"])

    def test_failed_subprocess_persists_manifest(self):
        output = self.root / "fail"
        code, result = self.run_case("fail", output)
        self.assertEqual((code, result["status"]), (1, "failed"))
        manifest = json.loads((output / "run.json").read_text())
        self.assertEqual(manifest["process_returncode"], 7)
        self.assertFalse((output / "RUNNING").exists())
        self.assertEqual(self.cli("verify", output)[0], 1)

    def test_capture_failure_marker_overrides_zero_exit(self):
        output = self.root / "marker"
        code, result = self.run_case("marker", output)
        self.assertEqual(code, 1)
        self.assertIn("capture-failed", result["error"])
        self.assertEqual(json.loads((output / "run.json").read_text())["process_returncode"], 0)

    def test_dry_run_writes_nothing(self):
        output = self.root / "dry"
        code, result = self.cli("run", "pass", "--source", self.root, "--output", output,
                                "--headless", "--dry-run")
        self.assertEqual((code, result["status"]), (0, "planned"))
        self.assertFalse(output.exists())

    def test_python_venv_symlink_is_preserved(self):
        python = self.root / "venv/bin/python"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)
        code, result = self.cli("run", "pass", "--source", self.root, "--output", self.root / "symlink",
                                "--python", python, "--headless", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(result["command"][0], str(python))

    def test_preflight_failure_is_saved_without_running_child(self):
        registry = self.root / "labs/scenarios.json"
        data = json.loads(registry.read_text())
        data["scenarios"][0]["modules"] = ["this_module_does_not_exist_physical_ai_test"]
        registry.write_text(json.dumps(data))
        output = self.root / "preflight-fail"
        code, result = self.run_case("pass", output)
        self.assertEqual((code, result["status"]), (1, "failed"))
        manifest = json.loads((output / "run.json").read_text())
        self.assertFalse(manifest["preflight"]["ready"])
        self.assertIsNone(manifest["process_returncode"])
        self.assertFalse((output / "result.json").exists())

    def test_json_error_and_prerequisite_registry(self):
        self.assertEqual(self.cli("run", "unknown", "--output", self.root / "unknown")[0], 1)
        code, items = self.cli("list")
        self.assertEqual(code, 0)
        self.assertTrue(any(item["status"] == "prerequisite" for item in items["scenarios"]))

    def test_model_scenarios_require_input_arguments(self):
        for scenario in ("cosmos-i2v", "alpamayo-synthetic"):
            code, result = self.cli("run", scenario, "--output", self.root / scenario)
            self.assertEqual(code, 1)
            self.assertIn("--input is required", result["error"])
            self.assertFalse((self.root / scenario).exists())

    def test_cosmos_receipt_checks_do_not_claim_motion_quality(self):
        output = self.root / "cosmos/workbench"
        output.mkdir(parents=True)
        receipt = output / "sample_outputs.json"
        receipt.write_text(json.dumps({"status": "success", "args": {"num_frames": 49, "fps": 24}}))
        # A synthetic container signature tests the gate, not video decoding.
        movie = output / "vision.mp4"
        movie.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"\x00" * 1200)
        result = HARNESS["validate"](output.parent, {"validator": "cosmos"})
        self.assertTrue(result["passed"])
        self.assertIn("require separate visual review", result["scope"])
        receipt.write_text(json.dumps({"status": "error", "message": "synthetic failure"}))
        with self.assertRaisesRegex(HARNESS["LabError"], "Cosmos sample failed"):
            HARNESS["validate"](output.parent, {"validator": "cosmos"})

    def test_alpamayo_saved_tensor_finiteness_overrides_receipt_claim(self):
        output = self.root / "alpamayo"
        output.mkdir()
        shapes = {"pred_xyz": [1, 1, 1, 64, 3], "pred_rot": [1, 1, 1, 64, 3, 3]}
        record = {name + "_shape": shape for name, shape in shapes.items()}
        record["finite"] = True
        (output / "receipt.json").write_text(json.dumps({"scope": "synthetic interface test", "result": record}))

        def tensor_file(nonfinite=False):
            header, numeric = {}, b""
            for name, shape in shapes.items():
                count = math.prod(shape)
                values = [0.] * count
                if nonfinite and name == "pred_xyz":
                    values[0] = float("nan")
                block = struct.pack("<" + "f" * count, *values)
                header[name] = {"dtype": "F32", "shape": shape, "data_offsets": [len(numeric), len(numeric) + len(block)]}
                numeric += block
            data = json.dumps(header).encode()
            (output / "output.safetensors").write_bytes(struct.pack("<Q", len(data)) + data + numeric)

        tensor_file()
        self.assertTrue(HARNESS["validate"](output, {"validator": "alpamayo"})["passed"])
        tensor_file(nonfinite=True)
        with self.assertRaisesRegex(HARNESS["LabError"], "Nonfinite"):
            HARNESS["validate"](output, {"validator": "alpamayo"})

    def test_cosmos_adapter_command_environment_and_explicit_filters(self):
        backend = self.root / "backend"
        package = backend / "cosmos_framework/scripts"
        package.mkdir(parents=True)
        (package / "inference.py").write_text("import json,os,sys; print(json.dumps({'args':sys.argv[1:],'path':os.environ['PATH']}))")
        adapter = CLI.parent / "cli/run_cosmos_backend.py"
        for disabled in (False, True):
            output = self.root / ("filters-off" if disabled else "filters-default")
            command = [sys.executable, str(adapter), "--backend", str(backend), "--input", str(self.root / "input.json"),
                       "--model", str(self.root / "model"), "--output", str(output), "--seed", "19"]
            result = subprocess.run(command + (["--no-guardrails"] if disabled else []), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            child = json.loads(result.stdout)
            self.assertEqual("--no-guardrails" in child["args"], disabled)
            saved = json.loads((output / "backend-command.json").read_text())
            self.assertEqual(saved["seed"], 19)
            self.assertTrue(child["path"].startswith(str(Path(sys.executable).parent)))


if __name__ == "__main__":
    unittest.main()
