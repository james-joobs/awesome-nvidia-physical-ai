"""CPU-only checks for actual detection outputs; never treats scores as accuracy."""
from collections import Counter
import hashlib,json,math
from pathlib import Path
import subprocess
LAB=Path(__file__).resolve().parent
REPO=LAB.parents[1]
def main(decode=False):
    report=json.loads((LAB/'evidence/perception-result.json').read_text())
    web=REPO/'site/public/showcase/rgb-reality-view'
    data=json.loads((web/'perception.json').read_text())
    assert hashlib.sha256((web/'perception.json').read_bytes()).hexdigest()==report['perception_sha256']
    assert report['gpu_count']==1 and report['camera_images']==162 and report['frames']==27
    assert not report['uses_source_annotations'] and not report['uses_lidar'] and not report['uses_supplied_calibration']
    assert report['weights_sha256']=='73cbd0190fcbe3ba339921fbce2c3a0b6bb9126c9a133c85e43a2a8e060a109e'
    count=Counter();localized=0;images=set()
    assert len(data['frames'])==27 and len(data['camera_names'])==6
    for fi,frame in enumerate(data['frames']):
        assert frame['index']==fi and set(frame['views'])==set(data['camera_names'])
        for view in frame['views'].values():
            path=web/view['image'];assert path.resolve().is_relative_to(web.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest()==report['rgb_preview_sha256'][view['image']]
            images.add(view['image']);w,h=view['image_size']
            for d in view['detections']:
                assert d['class'] in data['classes'] and data['score_threshold']<=d['score']<=1
                x0,y0,x1,y1=d['bbox'];assert 0<=x0<x1<=w+.01 and 0<=y0<y1<=h+.01
                mask=d['mask'];mw,mh=mask['size'];assert sum(mask['counts'])==mw*mh and all(isinstance(n,int) and n>=0 for n in mask['counts'])
                assert len(mask['origin'])==2 and all(n>0 for n in mask['extent'])
                count[d['class']]+=1
                if d['ground_position'] is not None:
                    assert len(d['ground_position'])==3 and all(math.isfinite(x) for x in d['ground_position']) and d['ground_position'][2]==0
                    assert isinstance(d['track_id'],int);localized+=1
        ids=[o['id'] for o in frame['objects']];assert len(ids)==len(set(ids))
    assert len(images)==162 and dict(count)==report['detections_by_class']
    assert localized==report['localized_detection_observations']
    assert sum(count.values())-localized==report['unlocalized_detection_observations']
    for lang in ['en','ko']:
        trace=json.loads((LAB/f'evidence/perception-interaction.{lang}.json').read_text());assert trace['errors']==[]
        events={e['action']:e for e in trace['events']}
        assert events['initial']['perception']['people_in_camera']>0
        assert not events['recognition_off']['perception']['enabled'] and events['recognition_on']['perception']['enabled']
        assert events['front_camera']['perception']['camera']=='front_camera'
        assert events['left_camera']['perception']['camera']=='left_camera'
        assert math.dist(events['initial']['camera'],events['orbit']['camera'])>.1
        assert events['perception_replay']['frame']!=events['initial']['frame']
        if decode:subprocess.run(['ffmpeg','-v','error','-i',str(LAB/f'evidence/rgb-perception.{lang}.mp4'),'-f','null','-'],check=True)
    print(f'Verified {sum(count.values())} detection observations across 162 RGB images, masks, approximate contacts and actual recognition controls; counts are not unique road users or accuracy.')
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--decode-video',action='store_true');main(p.parse_args().decode_video)
