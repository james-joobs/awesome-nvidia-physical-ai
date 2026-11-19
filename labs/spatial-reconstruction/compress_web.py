"""Compress the complete 3DGS PLY for Spark without dropping Gaussians.

Requires Node/npm. Uses a pinned MIT-licensed PlayCanvas CLI; no data is uploaded.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("ply",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    subprocess.run(["npm","exec","--yes","--package=@playcanvas/splat-transform@3.12.0","--","splat-transform",
        str(args.ply),"--filter-harmonics","1",str(args.output),"--spz-version","3"],check=True)
    data=args.output.read_bytes()
    magic,version,count,degree,fractional_bits,flags,reserved=struct.unpack_from("<IIIBBBB",gzip.decompress(data))
    report={"file":args.output.name,"format":"SPZ v3","gaussians":count,"sh_degree":degree,"bytes":len(data),
        "sha256":hashlib.sha256(data).hexdigest(),"converter":"PlayCanvas splat-transform 3.12.0 (MIT)",
        "modification":"Keep all Gaussians; quantize SPZ and retain SH through degree 1; full PLY remains degree 3"}
    args.output.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
