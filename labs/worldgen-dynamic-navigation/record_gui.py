"""Record the real native Isaac Sim window while run.py performs live physics."""
import argparse,json,os,signal,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True)
p.add_argument('--scenario',choices=['gate','cart'],default='gate')
p.add_argument('--ffmpeg',type=Path,required=True);p.add_argument('--collision-view',action='store_true')
p.add_argument('--controller',choices=['static','dynamic'],default='dynamic');p.add_argument('--max-seconds',default='32')
a=p.parse_args();root=Path(__file__).resolve().parent;a.work=a.work.resolve()
output=a.work/a.scenario;output.mkdir(parents=True,exist_ok=True)
assert not (output/'ready.json').exists(),'Use a new output folder for a fresh recording'
env=dict(os.environ,WORLDGEN_DATA_ROOT=str(a.work),DISPLAY=os.environ.get('DISPLAY',':1'),XAUTHORITY=os.environ.get('XAUTHORITY',f'/run/user/{os.getuid()}/gdm/Xauthority'))
command=['bash',str(root/'run.sh'),a.scenario,'--record-handshake','--controller',a.controller,'--max-seconds',a.max_seconds]+(['--collision-view'] if a.collision_view else [])
recorder=None
with (output/'simulator.log').open('w') as log:
    process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
    try:
        deadline=time.monotonic()+240
        while not (output/'ready.json').exists():
            if process.poll() is not None:raise RuntimeError('Isaac Sim stopped before the viewport was ready; see simulator.log')
            if time.monotonic()>deadline:raise TimeoutError('Isaac Sim startup timed out')
            time.sleep(.3)
        listing=subprocess.check_output(['xwininfo','-root','-tree'],env=env,text=True)
        window=next(row.split()[0] for row in listing.splitlines() if ('"Isaac Sim' in row or '"Isaac-Sim' in row) and 'mutter-x11-frames' not in row)
        metadata=subprocess.check_output(['xwininfo','-id',window],env=env,text=True)
        (output/'window.txt').write_text(metadata)
        with (output/'recorder.log').open('w') as recordlog:
            recorder=subprocess.Popen([str(a.ffmpeg),'-nostdin','-hide_banner','-loglevel','warning','-y','-f','x11grab','-draw_mouse','0','-framerate','30','-window_id',str(int(window,16)),'-i',env['DISPLAY']+'.0','-an','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2','-c:v','libx264','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output/'native-gui.mp4')],env=env,stdout=recordlog,stderr=subprocess.STDOUT)
            time.sleep(.5);assert recorder.poll() is None,'X11 recorder could not start'
            (output/'record-go').touch()
            process.wait(timeout=300)
        if (output/'FAILED').exists() or not (output/'result.json').exists():raise RuntimeError('Simulation failed; keep the logs for diagnosis')
    finally:
        if recorder and recorder.poll() is None:
            recorder.send_signal(signal.SIGINT);recorder.wait(timeout=15)
        if process.poll() is None:process.terminate()
print('Native GUI recording:',output/'native-gui.mp4')
