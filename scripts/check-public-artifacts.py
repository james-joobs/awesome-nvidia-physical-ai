#!/usr/bin/env python3
"""Reject private infrastructure data in files prepared for publication.

Run with scripts/requirements-publication.txt installed. This complements secret
scanning: it checks tracked/new publishable files, image metadata, ONNX strings,
compressed archives, and decoded binary USD layers. Matches are never printed.
"""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import zipfile

from PIL import Image
from pxr import Sdf

RULES = {
    "private home directory": re.compile(rb"/(?:home|Users)/[A-Za-z0-9_.-]+(?:/|\b)"),
    "GPU hardware identifier": re.compile(rb"GPU-[a-f0-9]{8}-[a-f0-9-]{20,}", re.I),
    "private key": re.compile(rb"-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----"),
    "credential-bearing URL": re.compile(rb"(?:https?|ssh|ftp)://[^\s/@:]+:[^\s/@]+@"),
}
PRIVATE_KEYS = {"host", "hostname", "host_name", "remote_originals", "sensor_gap_original", "gpu_uuid", "machine_id", "serial_number"}
BAD_NAMES = re.compile(r"(^|/)(?:\.env(?:\.(?!example$|sample$|template$).*)?|id_rsa|id_ed25519|\.netrc|credentials(?:\.json)?)$|\.(?:pem|p12|pfx)$", re.I)
MAX_MEMBER = 64 * 1024 * 1024
MAX_ARCHIVE = 256 * 1024 * 1024


def private_names():
    """The trusted CI supplies the private-name denylist without publishing it."""
    return [v.strip().lower().encode() for v in re.split(r"[,;\n]", os.environ.get("PUBLICATION_PRIVATE_NAMES", "")) if v.strip()]


def inspect_bytes(data, label, *, names=(), depth=0):
    findings = set()
    for rule, pattern in RULES.items():
        if pattern.search(data):
            findings.add((label, rule))
    lowered = data.lower()
    if any(name in lowered for name in names):
        findings.add((label, "private machine name"))
    suffix = PurePosixPath(label.split("!", 1)[-1]).suffix.lower()
    if suffix == ".json":
        def visit(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key.lower() in PRIVATE_KEYS and child not in (None, "", "omitted"):
                        findings.add((label, "private machine/storage field"))
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        try:
            visit(json.loads(data))
        except (ValueError, UnicodeDecodeError):
            findings.add((label, "unreadable JSON"))
    if suffix in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        with Image.open(io.BytesIO(data)) as image:
            metadata = {k: str(v) for k, v in image.info.items() if k != "icc_profile"}
            exif = image.getexif()
            metadata["exif"] = {str(k): str(v) for k, v in exif.items()}
            if 0x8825 in exif:
                findings.add((label, "GPS metadata"))
            if 0x8769 in exif:
                metadata["exif_details"] = str(exif.get_ifd(0x8769))
            encoded = json.dumps(metadata, ensure_ascii=False).encode()
            findings |= inspect_text(encoded, label + "!metadata", names)
    if suffix in (".zip", ".npz", ".usdz"):
        if depth >= 3:
            raise ValueError("archive nesting limit")
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if sum(entry.file_size for entry in entries) > MAX_ARCHIVE:
                raise ValueError("archive size limit")
            for entry in entries:
                if entry.is_dir():
                    continue
                if entry.file_size > MAX_MEMBER:
                    raise ValueError("archive member size limit")
                findings |= inspect_text(entry.filename.encode(), label + "!entry-name", names)
                findings |= inspect_bytes(archive.read(entry), label + "!" + entry.filename, names=names, depth=depth + 1)
    if data.startswith(b"PXR-USDC"):
        # Read a layer only, never compose its references or execute scene scripts.
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "layer.usdc"
            file.write_bytes(data)
            layer = Sdf.Layer.FindOrOpen(str(file))
            if layer is None:
                raise ValueError("cannot decode USD layer")
            findings |= inspect_text(layer.ExportToString().encode(), label + "!decoded-layer", names)
    return findings


def inspect_text(data, label, names=()):
    findings = {(label, rule) for rule, pattern in RULES.items() if pattern.search(data)}
    if any(name in data.lower() for name in names):
        findings.add((label, "private machine name"))
    return findings


def publishable_paths(root):
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    return sorted(set(p for p in raw.decode().split("\0") if p))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    names = private_names()
    findings = set()
    paths = publishable_paths(args.root)
    for path in paths:
        file = args.root / path
        if not file.is_file():
            continue
        if BAD_NAMES.search(path):
            findings.add((path, "credential-like filename"))
        try:
            findings |= inspect_bytes(file.read_bytes(), path, names=names)
        except Exception:
            # Do not log exceptions containing private paths or raw metadata.
            findings.add((path, "artifact inspection failed"))
    for path, rule in sorted(findings):
        print(f"BLOCKED {path}: {rule}")
    if findings:
        print(f"Publication blocked: {len(findings)} issue(s); matched values withheld.")
        return 1
    print(f"Publication checks passed for {len(paths)} files (private-name denylist {'enabled' if names else 'unavailable'}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
