"""Match the KITScenes clip with LoMa and recover camera poses using COLMAP."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import pycolmap
import torch
from loma import LoMa, LoMaB
from loma.loma import filter_matches, to_pixel_coords
from PIL import Image

MASK = "facebook/mask2former-swin-tiny-cityscapes-semantic"
MASK_REVISION = "01a04783d1e2981b13cf5aace8cd87774012de27"


@torch.inference_mode()
def features(rows, images, out):
    from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation

    processor = AutoImageProcessor.from_pretrained(MASK, revision=MASK_REVISION)
    semantic = Mask2FormerForUniversalSegmentation.from_pretrained(MASK, revision=MASK_REVISION).eval().cuda()
    matcher = LoMa(LoMaB()).cuda().eval()
    labels, keypoints, data = [], [], []
    masks = out/"labels"
    masks.mkdir()
    for row in rows:
        im = cv2.cvtColor(cv2.imread(str(images/row["file"])), cv2.COLOR_BGR2RGB)
        processed = processor(images=Image.fromarray(im), return_tensors="pt").to("cuda")
        prediction = semantic(**processed)
        label = processor.post_process_semantic_segmentation(prediction,target_sizes=[im.shape[:2]])[0]
        label = label.cpu().numpy().astype(np.uint8)
        cv2.imwrite(str(masks/row["file"].replace(".jpg",".png")),label)
        labels.append(label)
        source_h, source_w = label.shape
        match_w = 1008
        match_h = max(14, round(source_h*match_w/source_w/14)*14)
        match_image = cv2.resize(im, (match_w, match_h), interpolation=cv2.INTER_AREA)
        tensor = torch.from_numpy(match_image).permute(2,0,1)[None].cuda().float()/255
        points, desc, h, w = matcher.detect_and_describe(tensor,num_keypoints=2400)
        uv = to_pixel_coords(points[0], h, w).cpu().numpy() * np.array([source_w/w, source_h/h])
        keypoints.append(uv)
        x,y=np.rint(uv).astype(int).T
        x=x.clip(0,source_w-1);y=y.clip(0,source_h-1)
        ignore=(label>=10).astype(np.uint8)
        # Vehicle roof is a large stationary patch at the bottom of the front camera.
        ignore[round(.83*source_h):] = 1
        keep = cv2.dilate(ignore,np.ones((9,9),np.uint8))[y,x]==0
        data.append((points, desc, keep))
    del semantic
    torch.cuda.empty_cache()
    pairs=[]
    for i, a in enumerate(rows):
        for j in range(i+1,len(rows)):
            b=rows[j]
            distance=b["frame"]-a["frame"]
            same=a["camera"]==b["camera"]
            if distance <= (24 if same else 3):
                pairs.append((i,j))
    matches=[]
    for i,j in pairs:
        pa,da,ma=data[i]
        pb,db,mb=data[j]
        score=matcher(pa,pb,da,db)["scores"]
        ids=filter_matches(score,.15)[0][0].cpu().numpy()
        a=np.flatnonzero((ids>=0)&ma)
        a=a[mb[ids[a]]]
        if len(a)>=22:
            matches.append((i,j,np.column_stack([a,ids[a]]).astype(np.uint32)))
    print(f"{len(rows)} RGB views; {len(matches)} matched image pairs",flush=True)
    return keypoints,matches


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=args.output
    out.mkdir(parents=True)
    images=args.input/"images"
    rows=json.loads((args.input/"input.json").read_text())["images"]
    points,matches=features(rows,images,out)
    db_path=out/"matches.db"
    options=pycolmap.TwoViewGeometryOptions()
    options.detect_watermark=False
    options.ransac.max_error=2.5
    options.ransac.max_num_trials=3000
    with pycolmap.Database.open(db_path) as db:
        cameras={}
        ids=[]
        for row, xy in zip(rows,points,strict=True):
            sensor=row["camera"]
            if sensor not in cameras:
                camera=pycolmap.Camera(model="PINHOLE",width=row["size"][0],height=row["size"][1],
                                       params=row["intrinsics"],has_prior_focal_length=True)
                camera.camera_id=db.write_camera(camera)
                cameras[sensor]=camera
            image_id=db.write_image(pycolmap.Image(name=row["file"],camera_id=cameras[sensor].camera_id))
            db.write_keypoints(image_id,xy)
            ids.append(image_id)

        def verify(entry):
            i,j,pairs=entry
            geometry=pycolmap.estimate_calibrated_two_view_geometry(
                cameras[rows[i]["camera"]],points[i],cameras[rows[j]["camera"]],points[j],
                pairs,options)
            return i,j,pairs,geometry

        with ThreadPoolExecutor(max_workers=8) as pool:
            count=0
            for i,j,pairs,geometry in pool.map(verify,matches):
                if len(geometry.inlier_matches)<20:
                    continue
                db.write_matches(ids[i],ids[j],pairs)
                db.write_two_view_geometry(ids[i],ids[j],geometry)
                count+=1
    print(f"Verified {count} image pairs",flush=True)
    parameters=pycolmap.IncrementalPipelineOptions()
    parameters.num_threads=12
    parameters.random_seed=54
    parameters.ba_refine_principal_point=False
    parameters.ba_refine_extra_params=False
    parameters.min_model_size=10
    parameters.extract_colors=True
    (out/"models").mkdir()
    fitted=pycolmap.incremental_mapping(db_path,images,out/"models",parameters)
    if not fitted:
        raise RuntimeError("COLMAP could not recover the trajectory")
    reconstruction=max(fitted.values(),key=lambda v:v.num_reg_images())
    reconstruction.write(out)
    lookup={row["file"]:row for row in rows}
    records=[]
    for image in reconstruction.images.values():
        c=image.camera
        pose=image.cam_from_world().inverse().matrix()
        records.append(dict(lookup[image.name],K=c.calibration_matrix().tolist(),camera_pose=pose.tolist()))
    p=list(reconstruction.points3D.values())
    np.savez_compressed(out/"sfm.npz",points=np.array([q.xyz for q in p]),colors=np.array([q.color for q in p]))
    report={"records":sorted(records,key=lambda row:(row["frame"],row["camera"])),
            "model_views":reconstruction.num_reg_images(),"total_views":len(rows),
            "points":len(p),"mean_reprojection_px":reconstruction.compute_mean_reprojection_error(),
            "geometrically_verified_pairs":count,"features":"LoMa-B; Mask2Former road, sky and moving-object filtering"}
    (out/"cameras.json").write_text(json.dumps(report,indent=2)+"\n")
    print({key:value for key,value in report.items() if key!="records"})


if __name__=="__main__":
    main()
