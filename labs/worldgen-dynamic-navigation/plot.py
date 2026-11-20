"""Plot recorded physical trajectories; these figures are not simulator footage."""
import argparse,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--font');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
if a.font:plt.rcParams['font.family']=FontProperties(fname=a.font).get_name()
plt.rcParams.update({'svg.fonttype':'path','axes.unicode_minus':False,'font.size':11})
runs={name:json.loads((a.evidence/name/'result.json').read_text()) for name in ['gate-static','gate-dynamic','cart-dynamic']}

def save(fig,name):
    path=a.output/name;fig.savefig(path);fig.savefig(path.with_suffix(".png"),dpi=140);plt.close(fig)
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')

for lang in ['en','ko']:
    fig,axes=plt.subplots(2,1,figsize=(8,6),layout='constrained',sharex=True);fig.patch.set_facecolor('#f5f7f8')
    new=runs['gate-dynamic'];samples=new['samples'];times=[s['sim_time_s'] for s in samples]
    axes[0].plot(times,[s['poses']['/World/MovingObstacle'][0][1] for s in samples],c='#a13286',lw=2)
    axes[0].set_ylabel('Gate Y (m)' if lang=='en' else '차단벽 Y (m)')
    axes[0].set_title('Actual gate position and robot progress' if lang=='en' else '실제 차단벽 위치와 로봇의 진행')
    for case,color,label in [('gate-static','#c27037','Previous map' if lang=='en' else '이전 지도'),('gate-dynamic','#659f00','Updated map' if lang=='en' else '새 지도')]:
        s=runs[case]['samples'];axes[1].plot([v['sim_time_s'] for v in s],[v['poses']['/World/Robot/Chassis'][0][0] for v in s],color=color,lw=2.2,label=label)
    axes[1].set(ylabel='Robot X (m)' if lang=='en' else '로봇 X (m)',xlabel='Simulation time (s)' if lang=='en' else '시뮬레이션 시간 (초)')
    axes[1].legend(loc='lower right')
    for ax in axes:
        ax.axvspan(3.8,8.,color='#a13286',alpha=.07);ax.axvline(9.8,color='#9dabb4',ls='--',lw=1);ax.grid(alpha=.16)
        for spine in ax.spines.values():spine.set_edgecolor('#ced6db')
    fig.suptitle('The route opens, but permanent map memory still blocks the old planner' if lang=='en' else '길은 열렸지만 이전 지도에는 장애물이 남습니다',fontsize=13)
    save(fig,f'gate.{lang}.svg')
    r=runs['cart-dynamic'];samples=r['samples'];scans=json.loads((a.evidence/'cart-dynamic/scans.json').read_text())
    fig,ax=plt.subplots(figsize=(7,6),layout='constrained');fig.patch.set_facecolor('#f5f7f8')
    ax.add_patch(Rectangle((-2.5,-2),5,4,facecolor='#fafbfc',edgecolor='#b7c4cb'))
    ax.add_patch(Rectangle((-.225,-.4),.45,.8,color='#e5a14d',alpha=.9))
    ax.add_patch(Rectangle((.1,-1.25),.6,.6,color='#a13286',alpha=.8))
    ax.add_patch(Rectangle((.1,-3),.6,.6,fill=False,edgecolor='#a13286',ls='--'))
    ax.annotate('',xy=(.4,-1.3),xytext=(.4,-2.35),arrowprops={'arrowstyle':'->','color':'#a13286','lw':2})
    initial=scans[0]['planned_path_xy'];ax.plot([p[0] for p in initial],[p[1] for p in initial],'--',c='#3b9cae',lw=1.4,label='First computed axle path' if lang=='en' else '처음 계산한 차축 경로')
    points=[s['poses']['/World/Robot/Chassis'][0] for s in samples]
    ax.plot([p[0] for p in points],[p[1] for p in points],c='#659f00',lw=2.6,label='Measured chassis path' if lang=='en' else '실제 몸체 이동')
    for target in [0.,3.,15.]:
        row=min(samples,key=lambda s:abs(s['sim_time_s']-target));x,y,_=row['poses']['/World/Robot/Chassis'][0]
        ax.scatter(x,y,c='#659f00',s=18);ax.annotate(f'{int(target)} s',(x,y),xytext=(-24,9),textcoords='offset points',fontsize=9)
    ax.scatter(1.3,0,c='#263b31',marker='x',s=60)
    ax.set(xlim=(-2.,2.),ylim=(-3.2,1.7),xlabel='X (m)',ylabel='Y (m)',title='A moving box closes the first detour' if lang=='en' else '움직이는 상자가 첫 우회로를 막습니다')
    ax.set_aspect('equal');ax.grid(alpha=.15);ax.legend(loc='upper right',fontsize=9)
    for spine in ax.spines.values():spine.set_edgecolor('#ced6db')
    save(fig,f'cart.{lang}.svg')
