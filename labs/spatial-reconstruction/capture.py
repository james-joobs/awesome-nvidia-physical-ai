"""Capture a static CARLA neighborhood with known cameras for fVDB reconstruction.

This is a measured RGB-D dataset, not a generated world or an SfM estimate.
"""
import argparse
import json
import math
import queue
from pathlib import Path

import carla
import numpy as np
from PIL import Image
from prepare_seed import prepare


def read_frame(q, frame):
    while True:
        image = q.get(timeout=30)
        if image.frame == frame:
            return np.frombuffer(image.raw_data, np.uint8).reshape(image.height, image.width, 4).copy()
        if image.frame > frame:
            raise RuntimeError("Camera timestamps do not match")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--port", type=int, default=24000)
    parser.add_argument("--views", type=int, default=72)
    args = parser.parse_args()
    output = args.output
    (output / "images").mkdir(parents=True, exist_ok=True)
    (output / "depth").mkdir(exist_ok=True)
    client = carla.Client("127.0.0.1", args.port)
    client.set_timeout(90)
    world = client.load_world("Town03")
    previous = world.get_settings()
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = .05
    world.apply_settings(settings)
    world.set_weather(carla.WeatherParameters.ClearNoon)
    width, height, fov = 640, 360, 80
    focal = width / (2*math.tan(math.radians(fov/2)))
    intrinsics = np.array([[focal,0,width/2],[0,focal,height/2],[0,0,1]])
    sensors = []
    cameras = []
    # Reflect the world Y axis to make a right-handed reconstruction world.
    world_basis = np.diag([1.,-1.,1.,1.])
    camera_basis = np.array([[0,0,1,0],[1,0,0,0],[0,-1,0,0],[0,0,0,1.]])
    try:
        for kind in ("rgb", "depth"):
            bp = world.get_blueprint_library().find(f"sensor.camera.{kind}")
            for key,value in {"image_size_x":width,"image_size_y":height,"fov":fov,"sensor_tick":0}.items():
                bp.set_attribute(key,str(value))
            if kind == "rgb":
                bp.set_attribute("motion_blur_intensity","0")
            sensor = world.spawn_actor(bp, carla.Transform())
            q=queue.Queue()
            sensor.listen(q.put)
            sensors.append((sensor,q))
        for i in range(args.views):
            # Two interleaved rings; every eighth pose is held out during training.
            angle=2*math.pi*i/args.views
            radius=22+2*math.sin(3*angle)
            x,y=radius*math.cos(angle),radius*math.sin(angle)
            z=5+2*math.sin(2*angle)
            yaw=math.degrees(math.atan2(-y,-x))
            pitch=math.degrees(math.atan2(2-z, radius))
            transform=carla.Transform(carla.Location(x=x,y=y,z=z),carla.Rotation(pitch=pitch,yaw=yaw))
            for sensor,_ in sensors:
                sensor.set_transform(transform)
            for _ in range(6):
                frame=world.tick()
                data=[read_frame(q,frame) for _,q in sensors]
            rgb=data[0][:,:,:3][:,:,::-1].copy()
            raw=data[1].astype(np.float64)
            depth=(raw[:,:,2]+raw[:,:,1]*256+raw[:,:,0]*65536)/16777215*1000
            name=f"view_{i:03}.png"
            Image.fromarray(rgb).save(output/"images"/name)
            np.save(output/"depth"/f"view_{i:03}.npy",depth.astype(np.float32))
            c2w=world_basis@np.array(transform.get_matrix())@camera_basis
            assert np.isclose(np.linalg.det(c2w[:3,:3]),1,atol=1e-5)
            cameras.append({"camera_name":name,"image_path":name,"width":width,"height":height,
                "camera_intrinsics":intrinsics.tolist(),"world_to_camera":np.linalg.inv(c2w).tolist(),
                "sensor_frame":frame})
            print(f"Saved view {i+1}/{args.views}",flush=True)
        (output/"cameras.json").write_text(json.dumps(cameras,indent=2)+"\n")
        seed_points=prepare(output)
        report={"backend":"CARLA 0.9.16 / Unreal Engine 4.26","map":"Town03","weather":"ClearNoon",
            "views":len(cameras),"resolution":[width,height],"fov_degrees":fov,
            "seed_points":seed_points,"seed_views":[i for i in range(args.views) if i%3==0 and i%8!=0],"held_out_modulo":8,
            "depth":"CARLA RGB24 depth decoded in meters",
            "camera_convention":"OpenCV x-right y-down z-forward; right-handed world: CARLA Y reflected",
            "source_license":"CARLA-specific assets: CC-BY; see CARLA 0.9.16 README licenses"}
        (output/"capture.json").write_text(json.dumps(report,indent=2)+"\n")
    finally:
        for sensor,_ in sensors:
            sensor.stop()
            sensor.destroy()
        world.apply_settings(previous)


if __name__=="__main__":
    main()
