"""Generate a real WorldGen panorama, DA-2 distance field, Gaussian PLY and mesh.

Use the dedicated Python 3.11 runtime in setup.sh. FLUX approvals are required.
The image adapter uses known pinhole calibration instead of treating a normal
camera photograph as an equirectangular panorama. No model weights are changed.
"""
import argparse
import hashlib
import importlib.metadata
import json
import resource
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from huggingface_hub import snapshot_download
from plyfile import PlyData, PlyElement


def project_image(image, intrinsics, width, height, device="cuda"):
    """Inverse-project the panorama's rays into the calibrated source camera."""
    from worldgen.utils.general_utils import pano_unit_rays
    source = np.array(image.convert("RGB"))
    sh, sw = source.shape[:2]
    K = np.asarray(intrinsics, dtype=float)
    rays = pano_unit_rays(height, width, device)
    z = rays[..., 2]
    u = K[0, 0] * rays[..., 0] / z.clamp(min=1e-6) + K[0, 2]
    v = K[1, 1] * rays[..., 1] / z.clamp(min=1e-6) + K[1, 2]
    valid = (z > 0) & (u >= 0) & (u <= sw-1) & (v >= 0) & (v <= sh-1)
    grid = torch.stack((u/(sw-1)*2-1, v/(sh-1)*2-1), dim=-1)
    rgb = torch.tensor(source, device=device, dtype=torch.float32).permute(2, 0, 1)[None]/255
    mapped = F.grid_sample(rgb, grid[None], mode="bilinear", align_corners=True, padding_mode="zeros")[0].permute(1, 2, 0)
    mapped = (mapped * valid[..., None] * 255).round().clamp(0, 255).to(torch.uint8).cpu().numpy()
    mask = (~valid).to(torch.uint8).cpu().numpy()*255
    return Image.fromarray(mapped), Image.fromarray(mask), float(valid.float().mean())


def export_ply(splat, path):
    """Export standard 3DGS fields: log scale, logit opacity and wxyz rotation."""
    fields = ["x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2", "opacity",
              "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3"]
    values = np.concatenate((splat.centers, np.zeros_like(splat.centers),
        (splat.rgbs-.5)/.28209479177387814,
        np.log(np.clip(splat.opacities, 1e-6, 1-1e-6)/np.clip(1-splat.opacities, 1e-6, 1)),
        np.log(np.maximum(splat.scales, 1e-5)), splat.rotations), axis=1).astype(np.float32)
    assert np.isfinite(values).all(), "Non-finite Gaussian attributes"
    assert np.allclose(np.linalg.norm(splat.rotations, axis=1), 1, atol=1e-3)
    vertices = np.empty(len(values), dtype=[(field, "f4") for field in fields])
    for i, field in enumerate(fields):
        vertices[field] = values[:, i]
    PlyData([PlyElement.describe(vertices, "vertex")], text=False).write(path)
    return {"gaussians": len(values), "all_finite": True,
            "bounds": [splat.centers.min(0).tolist(), splat.centers.max(0).tolist()]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--intrinsics", type=Path)
    parser.add_argument("--pins", type=Path, default=Path(__file__).with_name("model-pins.json"))
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    assert args.width % 32 == 0
    if args.image and not args.intrinsics:
        parser.error("The image route requires the camera's intrinsics JSON")
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    pins = json.loads(args.pins.read_text())
    snapshots = {r["repo"]: snapshot_download(r["repo"], revision=r["revision"],
        ignore_patterns=r.get("omitted") or None, max_workers=3) for r in pins["models"]}
    from da2.model.spherevit import SphereViT
    import da2.model.dinov2.attention as da2_attention
    # DA-2 already provides this PyTorch SDPA fallback. Old xFormers has no sm_120 kernel.
    da2_attention.XFORMERS_AVAILABLE = False
    from nunchaku import NunchakuFluxTransformer2dModel
    from worldgen import WorldGen
    import worldgen.worldgen as wg
    from worldgen.pano_depth import DA2_CONFIG, pred_pano_depth
    from worldgen.pano_gen import gen_pano_image, gen_pano_fill_image
    from worldgen.models.flux_pano_gen_pipeline import FluxPipeline
    from worldgen.models.flux_pano_fill_pipeline import FluxFillPipeline
    from worldgen.utils.lora_utils import load_and_fix_lora
    import open3d as o3d

    torch.backends.cudnn.enabled = False
    torch.manual_seed(args.seed)
    torch.cuda.reset_peak_memory_stats()
    mode = "i2s" if args.image else "t2s"
    base = "black-forest-labs/FLUX.1-Fill-dev" if args.image else "black-forest-labs/FLUX.1-dev"
    quant = "mit-han-lab/svdq-fp4-flux.1-fill-dev" if args.image else "mit-han-lab/svdq-fp4-flux.1-dev"
    lora_file = "worldgen_img2scene.safetensors" if args.image else "worldgen_text2scene.safetensors"

    def depth_model(device):
        return SphereViT.from_pretrained(snapshots["haodongli/DA-2"], config=DA2_CONFIG).eval().to(device)

    def panorama_model(lora_path=None, device="cuda", low_vram=True):
        transformer = NunchakuFluxTransformer2dModel.from_pretrained(snapshots[quant], offload=True)
        pipe_type = FluxFillPipeline if args.image else FluxPipeline
        pipe = pipe_type.from_pretrained(snapshots[base], transformer=transformer, torch_dtype=torch.bfloat16)
        state_dict, _ = load_and_fix_lora(str(Path(snapshots["LeoXie/WorldGen"])/"models--WorldGen-Flux-Lora"/lora_file))
        transformer.update_lora_params(state_dict)
        pipe.enable_model_cpu_offload()
        pipe.enable_vae_tiling()
        return pipe

    # Keep the upstream WorldGen generation, depth, splat and mesh implementations.
    # The builders above select immutable model snapshots and FP4/offload explicitly.
    wg.build_depth_model = depth_model
    wg.build_pano_gen_model = panorama_model
    wg.build_pano_fill_model = panorama_model
    started = time.monotonic()
    model = WorldGen(mode=mode, resolution=args.width, device=torch.device("cuda"), low_vram=True)
    loaded_seconds = time.monotonic()-started
    print("Models loaded:", mode, "RTX 5090 / FP4 / CPU offload", flush=True)
    height = args.width//2
    stage = time.monotonic()
    conditioning = None
    with torch.inference_mode():
        if args.image:
            image = Image.open(args.image).convert("RGB")
            intrinsics = json.loads(args.intrinsics.read_text())
            assert list(image.size) == intrinsics["resolution"]
            mapped, mask, coverage = project_image(image, intrinsics["K"], args.width, height)
            mapped.save(output/"conditioning.png")
            mask.save(output/"generation-mask.png")
            image.save(output/"input.png")
            panorama = gen_pano_fill_image(model.pano_gen_model, mapped, mask, prompt=args.prompt,
                seed=args.seed, num_inference_steps=args.steps, height=height, width=args.width)
            generated = np.array(panorama)
            keep = np.array(mask)==0
            generated[keep] = np.array(mapped)[keep]
            panorama = Image.fromarray(generated)
            conditioning = {"source_sha256": hashlib.sha256(args.image.read_bytes()).hexdigest(),
                "source_resolution": list(image.size), "intrinsics": intrinsics["K"],
                "observed_panorama_fraction": coverage,
                "max_preserved_rgb_error": int(np.abs(generated[keep].astype(int)-np.array(mapped)[keep].astype(int)).max()),
                "projection": "known pinhole K to equirectangular rays; white mask is generated"}
        else:
            panorama = gen_pano_image(model.pano_gen_model, prompt=args.prompt, seed=args.seed,
                num_inference_steps=args.steps, height=height, width=args.width)
        torch.cuda.synchronize()
        generation_seconds = time.monotonic()-stage
        panorama.save(output/"panorama.png")
        print("Panorama saved", list(panorama.size), flush=True)
        stage = time.monotonic()
        predictions = pred_pano_depth(model.depth_model, panorama)
        depth = predictions["distance"].float().cpu().numpy()
        assert np.isfinite(depth).all() and depth.min()>0
        np.save(output/"distance.npy", depth)
        splat = model.depth2gs(predictions)
        result = export_ply(splat, output/"scene.ply")
        mesh = model.depth2mesh(predictions)
        assert o3d.io.write_triangle_mesh(str(output/"scene-mesh.ply"), mesh)
        assert o3d.io.write_triangle_mesh(str(output/"scene-mesh.glb"), mesh)
        torch.cuda.synchronize()
        geometry_seconds = time.monotonic()-stage
    report = {"status": "success", "mode": mode, "prompt": args.prompt, "seed": args.seed,
        "steps": args.steps, "resolution": list(panorama.size), "conditioning": conditioning,
        "distance": {"shape": list(depth.shape), "min": float(depth.min()), "max": float(depth.max()),
            "scale": "DA-2 scale-invariant estimate normalized to max 20; not measured metric distance"},
        "gaussians": result, "mesh": {"vertices": len(mesh.vertices), "triangles": len(mesh.triangles)},
        "seconds": {"load": loaded_seconds, "panorama": generation_seconds, "geometry": geometry_seconds},
        "runtime": {"gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "cuda": torch.version.cuda,
            "packages": {n: importlib.metadata.version(n) for n in ["nunchaku", "diffusers", "transformers", "da2", "worldgen", "pytorch3d"]},
            "peak_gpu_gb": torch.cuda.max_memory_allocated()/1e9, "max_rss_gb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6},
        "model_revisions": pins["models"], "source_revisions": pins["source_revisions"]}
    for filename in ["panorama.png", "distance.npy", "scene.ply", "scene-mesh.ply", "scene-mesh.glb"]:
        path = output/filename
        report.setdefault("artifacts", {})[filename] = {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    (output/"result.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"mode": mode, "seconds": report["seconds"], "gaussians": result["gaussians"]}), flush=True)


if __name__ == "__main__":
    main()
