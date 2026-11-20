"""Visualize actual poses and measured hits after the run; no rendered footage."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--font');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
if a.font:plt.rcParams['font.family']=FontProperties(fname=a.font).get_name()
plt.rcParams.update({'svg.fonttype':'path','axes.unicode_minus':False,'font.size':10})
for lang in ['en','ko']:
    fig,axes=plt.subplots(1,3,figsize=(12,4.4),layout='constrained');fig.patch.set_facecolor('#f5f7f8')
    for ax,case,label in zip(axes,['center','lower','upper'],['Central box','Lower route blocked','Upper route blocked'] if lang=='en' else ['중앙 상자','아래쪽 통로 막힘','위쪽 통로 막힘']):
        folder=a.evidence/case;r=json.loads((folder/'result.json').read_text());scans=json.loads((folder/'scans.json').read_text())
        ax.add_patch(Rectangle((-.225,-.4),.45,.8,color='#eba146',alpha=.8))
        if case!='center':ax.add_patch(Rectangle((-.225,-1.25 if case=='lower' else .65),.45,.6,color='#eba146',alpha=.8))
        hits=[pt for scan in scans[::10] for d,pt in zip(scan['depths_m'],scan['hit_positions_world']) if d<2.499]
        ax.scatter([p[0] for p in hits],[p[1] for p in hits],s=7,c='#5295b7',label='Sensor hits' if lang=='en' else '센서 측정')
        points=[s['poses']['/World/Robot/Chassis'][0] for s in r['samples']]
        ax.plot([p[0] for p in points],[p[1] for p in points],c='#659f00',lw=2.6,label='Measured robot path' if lang=='en' else '실제 이동 경로')
        if case=='lower':
            old=json.loads((a.evidence/'baseline/result.json').read_text());points=[s['poses']['/World/Robot/Chassis'][0] for s in old['samples']]
            ax.plot([p[0] for p in points],[p[1] for p in points],'--',c='#bc4f38',lw=2,label='Fixed route' if lang=='en' else '기존 제어')
        ax.scatter([-1.3,1.3],[0,0],c=['#3b6d8e','#659f00'],s=30)
        ax.set(xlim=(-1.75,1.75),ylim=(-1.6,1.6),title=label,xlabel='X (m)');ax.set_aspect('equal');ax.grid(alpha=.17)
        for spine in ax.spines.values():spine.set_edgecolor('#d0d5da')
    axes[0].set_ylabel('Y (m)');axes[1].legend(loc='lower center',fontsize=8)
    fig.suptitle('Recorded sensor hits and physical chassis motion' if lang=='en' else '실제 센서 측정점과 몸체 이동 기록',fontsize=14)
    path=a.output/f'paths.{lang}.svg';fig.savefig(path);plt.close(fig)
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
