"""Crop actual X11 window recordings into lightweight viewport clips.

No offline renderer or animation is substituted for the native GUI footage.
"""
import argparse,hashlib,json,subprocess,shutil,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--ffprobe',default='ffprobe');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
# Fixed geometry from our 1440×900 native Kit window; inspect window.txt on other layouts.
for scenario,stem in [('combined','worldgen-isaac'),('blocked','worldgen-isaac-blocked'),('detour','worldgen-isaac-detour'),('probes','worldgen-isaac-probes')]:
    folder=a.source/scenario
    if not (folder/'native-gui.mp4').exists():continue
    window=(folder/'window.txt').read_text()
    assert 'Width: 1440' in window and 'Height: 900' in window,'Reinspect the viewport crop for another layout'
    result=json.loads((folder/'result.json').read_text());duration=result['duration_wall_s']+(.75 if scenario!='probes' else 0)+.2
    output=a.output/f'{stem}.mp4'
    subprocess.run([a.ffmpeg,'-hide_banner','-loglevel','error','-y','-ss','0.4','-i',str(folder/'native-gui.mp4'),'-t',str(duration),'-an',
        '-vf','crop=952:536:50:64,scale=960:540','-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
    subprocess.run([a.ffmpeg,'-hide_banner','-loglevel','error','-y','-ss','1.4' if scenario=='probes' else '3','-i',str(output),'-frames:v','1',str(a.output/f'{stem}.jpg')],check=True)
    if shutil.which(a.ffprobe):
        probe=json.loads(subprocess.check_output([a.ffprobe,'-v','error','-show_format','-of','json',str(output)]))
        duration_s=float(probe['format']['duration'])
    else:
        info=subprocess.run([a.ffmpeg,'-hide_banner','-i',str(output)],capture_output=True,text=True).stderr
        hh,mm,ss=re.search(r'Duration: (\d+):(\d+):([\d.]+)',info).groups()
        duration_s=int(hh)*3600+int(mm)*60+float(ss)

    metadata={'source':'native X11 Isaac Sim window, 1440x900','crop_xywh':[50,64,952,536],'trim_start_s':.4,'speed':1.,'published_resolution':[960,540],
        'duration_s':duration_s,'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256((folder/'native-gui.mp4').read_bytes()).hexdigest(),'physical_simulation_s':result['duration_sim_s']}
    (a.output/f'{stem}.edit.json').write_text(json.dumps(metadata,indent=2)+'\n');print(stem,metadata['duration_s'],metadata['bytes'])
