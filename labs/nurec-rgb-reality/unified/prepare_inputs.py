"""Select 17 nominal times from RGB-only undistorted camera images.

Input layout: CAMERA/00.jpg, CAMERA/03.jpg ... CAMERA/48.jpg. These filename
times are the parent lab's assumption, not imported sensor timestamps.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image

CAMERAS=['back_camera','front_camera','front_left_camera','front_right_camera','left_camera','right_camera']


def crop(image,width=720,height=480):
    w,h=image.size
    if height/width>h/w:
        cw=int(h/height*width);ch=h;left=int((w-h/height*width)/2);top=0
    else:
        cw=w;ch=int(w/width*height);left=0;top=int((h-w/width*height)/2)
    return image.crop((left,top,left+cw,top+ch)).resize((width,height),Image.Resampling.BILINEAR)


def main():
    p=argparse.ArgumentParser();p.add_argument('--images',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise ValueError('Choose a fresh output folder')
    files=[(cam,f'{i:02d}.jpg',a.images/cam/f'{i:02d}.jpg') for i in range(0,49,3) for cam in CAMERAS]
    missing=[str(p.relative_to(a.images)) for _,_,p in files if not p.is_file()]
    if missing:raise ValueError(f'Missing RGB images: {missing[:6]}')
    for name in ['front-full','front-crop','surround']:(a.out/name).mkdir(parents=True)
    records=[]
    for cam,name,path in files:
        shutil.copy2(path,a.out/'surround'/f'{Path(name).stem}-{cam}.jpg')
        if cam=='front_camera':
            shutil.copy2(path,a.out/'front-full'/name)
            crop(Image.open(path).convert('RGB')).save(a.out/'front-crop'/f'{int(Path(name).stem)//3:06d}.png')
        records.append({'image':f'{cam}/{name}','sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest()})
    (a.out/'inputs.json').write_text(json.dumps({'schema':1,'view_count':102,'nominal_time_count':17,'nominal_span_seconds':4.8,'camera_names':CAMERAS,'lidar_used':False,'source_sensor_timestamps_used':False,'records':records},indent=2)+'\n')
    print('Prepared RGB only: 17 front views + 102 surround views at17 nominal times.')


if __name__=='__main__':main()
