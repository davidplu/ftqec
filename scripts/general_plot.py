"""Publication-ready resource plot from exact certified circuit records."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from ftqec.results.artifacts import source_identity,save
source=source_identity();data=json.loads(Path(f'results/pareto/general_competitive/{source}.json').read_text())
points=sorted(set((r['resources']['Q'],r['resources']['D'],r['resources']['QD']) for r in data['discovery']))
ref=next(r['resources'] for r in data['all_known_including_reference'] if r['reference'])
old=json.loads(Path('results/discovery/autonomous/surface_target10/checkpoint.json').read_text());old=[r['resources'] for r in old['rows'] if r.get('certify',{}).get('status')=='CERTIFIED'];old=[min(old,key=lambda r:(r['Q'],r['QD'])),min(old,key=lambda r:(r['D'],r['QD']))]
root=Path('results/pareto/general_competitive')/source;root.mkdir(parents=True,exist_ok=True)
save(root/'plot_data.json',dict(source=source,discovery=points,reference=ref,previous=old,scope='Independent extraction certificates; ideal syndrome boundaries, explicit operation-local faults'))
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,2,figsize=(8,4.4),layout='constrained')
for ax,index,label in zip(axes,(1,2),('Circuit depth (layers)','Q × depth')):
 key='D' if index==1 else 'QD'
 ax.scatter([r['Q'] for r in old],[r[key] for r in old],marker='x',s=75,color='#7b7b7b',linewidths=2,label='Previous discovery',zorder=4)
 ax.scatter([p[0] for p in points],[p[index] for p in points],s=48,color='#087f8c',label='New discovery frontier',zorder=3)
 ax.scatter([ref['Q']],[ref[key]],marker='*',s=135,color='#8a3c9c',label='Independent reference',zorder=5)
 ax.set_yscale('log');ax.yaxis.set_major_formatter(ScalarFormatter());ax.set_xlabel('Physical qubits Q');ax.set_ylabel(label);ax.set_xlim(94,207);ax.grid(axis='y',alpha=.2)
axes[0].set_ylim(6,1050);axes[0].set_yticks([8,12,24,100,756]);axes[1].set_ylim(1200,110000);axes[1].set_yticks([1592,2388,10000,76356])
axes[0].annotate('12 layers',xy=(199,12),xytext=(-8,8),textcoords='offset points',ha='right',color='#087f8c')
axes[0].annotate('8 layers',xy=(199,8),xytext=(-8,-4),textcoords='offset points',ha='right',color='#8a3c9c')
fig.suptitle('Independently certified target-10 extraction circuits',fontsize=12)
handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,frameon=False)
for suffix in ('png','svg','pdf'):fig.savefig(root/('resource_frontier.'+suffix),dpi=180)
plt.close(fig);print(root/'resource_frontier.png')
