"""Plot measured chassis paths, not the requested waypoint polyline (CPU)."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--font',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
if a.font:plt.rcParams['font.family']=FontProperties(fname=str(a.font)).get_name()
plt.rcParams.update({'svg.fonttype':'path','axes.unicode_minus':False,'font.size':11})
runs={name:json.loads((a.evidence/name/'result.json').read_text()) for name in ['combined','blocked']}
for lang in ['en','ko']:
    fig,ax=plt.subplots(figsize=(9,5),layout='constrained');fig.patch.set_facecolor('#f6f8fa');ax.set_facecolor('white')
    ax.add_patch(Rectangle((-.225,-.4),.45,.8,facecolor='#f4a340',edgecolor='#9d5c05',label='Test crate' if lang=='en' else '시험 상자'))
    for name,color,label in [('combined','#659f00','Contact, reverse, detour' if lang=='en' else '접촉·후진 후 우회'),('blocked','#ce5a46','Straight drive' if lang=='en' else '직진')]:
        xy=[s['poses']['/World/Robot/Chassis'][0][:2] for s in runs[name]['samples']]
        ax.plot([q[0] for q in xy],[q[1] for q in xy],color=color,lw=2.5,label=label,zorder=4 if name=='blocked' else 3,linestyle='--' if name=='blocked' else '-')
    ax.scatter([-1.3,1.3],[0,0],s=75,marker='o',color=['#416a94','#659f00'],zorder=4)
    ax.annotate('Start' if lang=='en' else '출발',(-1.3,0),xytext=(-16,14),textcoords='offset points')
    ax.annotate('Goal' if lang=='en' else '목표',(1.3,0),xytext=(-10,14),textcoords='offset points')
    ax.set(xlim=(-1.8,1.8),ylim=(-1.4,.8),xlabel='X (chosen simulation metres)' if lang=='en' else 'X (정한 시뮬레이션 크기, m)',ylabel='Y (m)',title='Measured chassis motion · live PhysX' if lang=='en' else '실제 몸체 이동 기록 · PhysX 실행')
    ax.set_aspect('equal');ax.grid(alpha=.18);ax.legend(loc='upper center',ncol=3,fontsize=10)
    for spine in ax.spines.values():spine.set_edgecolor('#c8d0d7')
    fig.savefig(a.output/f'paths.{lang}.svg');plt.close(fig)
