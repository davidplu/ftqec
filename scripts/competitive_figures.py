"""Standalone scientific figures from the derived raw-backed summary."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ftqec.results.artifacts import source_identity
source=source_identity();summary=json.loads(Path('results/competitive_export/summary.json').read_text());front=json.loads((Path('results/pareto/competitive_export')/(source+'.json')).read_text())
out=Path('results/pareto/competitive_export')/source;out.mkdir(exist_ok=True)
rows=front['discovery'];pairs=sorted({(r['resources']['Q'],r['resources']['D']) for r in rows})
fig,ax=plt.subplots(figsize=(8,4.8));ax.plot([x for x,y in pairs],[y for x,y in pairs],'o-',label='Certified discovery frontier')
ax.scatter([199],[12],marker='s',color='#777777',label='Previous autonomous D12')
ax.scatter([199],[8],marker='o',s=140,facecolors='none',edgecolors='#cc6600',linewidths=2,label='Independent D8 reference')
ax.set(yscale='log',xlabel='Physical qubits Q',ylabel='Compiled depth D (log scale)',title='Certified target-10 resource tradeoffs');ax.grid(alpha=.2);ax.legend();fig.tight_layout()
for suffix in ('png','svg'):fig.savefig(out/('resource_frontier.'+suffix),dpi=170)
plt.close(fig)
arms=[r for r in summary['ler'] if r['status']=='COMPLETE']
fig,ax=plt.subplots(figsize=(8,4.5))
for i,r in enumerate(arms):
 lo,hi=r['simultaneous_interval'];ax.errorbar(i,r['rate'],yerr=[[r['rate']-lo],[hi-r['rate']]],fmt='o',capsize=6,color='#087f8c')
ax.set_xticks(range(len(arms)),[r['name'].replace('_',' ') for r in arms]);ax.set(ylabel='Decoder-conditional logical error rate',title='Matching decoder, p=0.01; simultaneous 95% intervals');ax.grid(axis='y',alpha=.2);fig.tight_layout()
for suffix in ('png','svg'):fig.savefig(out/('logical_error_rates.'+suffix),dpi=170)
print('FIGURES_WRITTEN',out)

