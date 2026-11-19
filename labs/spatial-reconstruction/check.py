"""Inspect 3DGS evidence with Python's standard library; no CUDA or NumPy required."""
import hashlib
import gzip
import json
import math
from pathlib import Path
import struct


def main():
    root=Path(__file__).resolve().parents[2]
    folder=root/"labs/spatial-reconstruction"
    record=json.loads((folder/"recorded.json").read_text())
    assert record["input_views"]==record["training_views"]+record["held_out_views"]==72
    assert record["held_out_views"]==9
    assert all(i%8!=0 for i in record["input"]["seed_views"])
    cameras=json.loads((folder/"evidence/cameras.json").read_text())
    assert len(cameras)==72
    for camera in cameras:
        m=camera["world_to_camera"]
        assert len(m)==4 and all(len(row)==4 and all(math.isfinite(x) for x in row) for row in m)
        det=(m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
        assert math.isclose(det,1,abs_tol=1e-5), "Camera axes are not a right-handed rotation"
    sample=json.loads((folder/"evidence/point-sample.json").read_text())
    u,v=sample["pixel_uv"];K=sample["intrinsics"];d=sample["depth_m"]
    point=[(u-K[0][2])/K[0][0]*d,(v-K[1][2])/K[1][1]*d,d]
    assert all(math.isclose(a,b,abs_tol=1e-6) for a,b in zip(point,sample["point_camera_m"]))
    m=sample["camera_to_world"]
    world=[sum(m[i][j]*point[j] for j in range(3))+m[i][3] for i in range(3)]
    assert all(math.isclose(a,b,abs_tol=1e-5) for a,b in zip(world,sample["point_world_m"]))
    media=root/"site/public/showcase"
    raw=(media/"town03.spz").read_bytes()
    assert len(raw)==record["web_preview"]["bytes"]
    assert hashlib.sha256(raw).hexdigest()==record["web_preview"]["sha256"]
    unpacked=gzip.decompress(raw)
    magic,version,count,degree,_,_,_=struct.unpack_from('<IIIBBBB',unpacked)
    assert unpacked[:4]==b'NGSP' and version==3 and degree==1
    assert count==record["gaussians"]==record["web_preview"]["gaussians"]
    assert len(unpacked)==16+count*(20+((degree+1)**2-1)*3), "SPZ payload is incomplete"
    assert hashlib.sha256((media/"spatial-reconstruction.mp4").read_bytes()).hexdigest()==record["render"]["sha256"]
    sharp=json.loads((folder/"sharp-recorded.json").read_text())
    for case in sharp["cases"]:
        assert case["gaussians"]==1_179_648 and case["focal_px"]==case["input_resolution"][0]/2
        assert hashlib.sha256((media/f'sharp-{case["video"]}').read_bytes()).hexdigest()==case["video_sha256"]
    print(f'{record["training_views"]} training / {record["held_out_views"]} held-out views; no held-out depth in seed')
    print(f'Full model: {record["gaussians"]:,} Gaussians, held-out PSNR {record["held_out_psnr_db"]} dB')
    print(f'Camera transforms, RGB-D sample, {len(raw):,}-byte browser model and 3 videos verified.')


if __name__=="__main__":
    main()
