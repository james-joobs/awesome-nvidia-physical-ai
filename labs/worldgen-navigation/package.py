"""Package native GUI crops and an honest sequential controller comparison.

Requires ffmpeg and Pillow on the editing machine. All footage stays at 1×.
"""
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--font',required=True);p.add_argument('--font-ko',required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)

def ff(*args):subprocess.run([a.ffmpeg,'-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

records={}
for label,scenario,stem in [('lower','sensor','worldgen-navigation-lower'),('baseline','scripted','worldgen-navigation-fixed'),('upper','sensor','worldgen-navigation-upper'),('center','sensor','worldgen-navigation-center')]:
    folder=a.source/label/scenario
    assert 'Width: 1440' in (folder/'window.txt').read_text() and 'Height: 900' in (folder/'window.txt').read_text()
    r=json.loads((folder/'result.json').read_text());duration=r['duration_wall_s']+.95
    output=a.output/(stem+'.mp4')
    ff('-ss','0.4','-i',folder/'native-gui.mp4','-t',duration,'-an','-vf','crop=952:536:50:64,scale=960:540',
       '-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',output)
    ff('-ss','5','-i',output,'-frames:v','1',a.output/(stem+'.jpg'))
    records[stem]={'source_native_sha256':digest(folder/'native-gui.mp4'),'crop_xywh':[50,64,952,536],
        'trim_start_s':.4,'speed':1.,'duration_limit_s':duration,'simulation_s':r['duration_sim_s'],
        'simulation_wall_s':r['duration_wall_s'],'goal_reached_s':r['goal_reached_s'],'published_sha256':digest(output)}

# The complete sensor take is shown after a 10 s excerpt of the fixed controller.
# A hard cut and persistent labels distinguish separate real simulator runs.
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory)
    for lang in ['en','ko']:
        font=ImageFont.truetype(a.font if lang=='en' else a.font_ko,25)
        labels=['Fixed waypoints | New box blocks the route','Range sensor + A* | Replans from measurements'] if lang=='en' else ['기존 경유점 제어 | 추가 상자에 막힘','거리 센서 + A* | 측정값으로 경로 재계산']
        parts=[]
        for i,(name,text) in enumerate(zip(['worldgen-navigation-fixed','worldgen-navigation-lower'],labels)):
            badge=Image.new('RGBA',(960,48),(247,249,250,235));draw=ImageDraw.Draw(badge)
            draw.rectangle((0,0,5,48),fill='#76b900');draw.text((17,9),text,font=font,fill='#1b252b')
            png=temp/f'label-{lang}-{i}.png';badge.save(png)
            part=temp/f'part-{lang}-{i}.mp4';parts.append(part)
            options=['-i',a.output/(name+'.mp4'),'-i',png,'-filter_complex','[0:v][1:v]overlay=0:0:format=auto,format=yuv420p']
            if i==0:options+=['-t','10']
            ff(*options,'-an','-c:v','libx264','-preset','slow','-crf','23',part)
        listing=temp/f'concat-{lang}.txt';listing.write_text(''.join(f"file '{part}'\n" for part in parts))
        stem='worldgen-navigation' if lang=='en' else 'worldgen-navigation-ko'
        output=a.output/(stem+'.mp4')
        ff('-f','concat','-safe','0','-i',listing,'-c','copy','-movflags','+faststart',output)
        ff('-ss','13','-i',output,'-frames:v','1',a.output/(stem+'.jpg'))
        records[stem]={'edit':'10 s fixed-route excerpt, then complete sensor-lower viewport take; labeled hard cut',
            'sources':['worldgen-navigation-fixed','worldgen-navigation-lower'],'speed':1.,'published_sha256':digest(output)}
(a.output/'navigation-edit.json').write_text(json.dumps(records,indent=2)+'\n')
print('Native crops and bilingual sequential comparison packaged at 1× speed.')
