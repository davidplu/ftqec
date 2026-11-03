"""Standalone scientific plots from raw certified resources and frozen LER data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ftqec.results.artifacts import source_identity,save
source=source_identity();root=Path('results/general_extraction/figures')/source;root.mkdir(parents=True,exist_ok=True)
a=Path('results/pareto')/source/'allocation_study/rows.json';l=Path('results/ler')/source/'target5_matched/summary.json';f=Path('results/general_extraction/first_positive')/source/'result.json'
rows=json.loads(a.read_text());ler=json.loads(l.read_text());first=json.loads(f.read_text())
fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
ax=axes[0];cert=[first['resources']]+[r['resources'] for r in rows if r.get('certification',{}).get('result',{}).get('status')=='CERTIFIED'];bad=[r for r in rows if r.get('certification',{}).get('result',{}).get('status')=='INVALID']
ax.scatter([r['Q'] for r in cert],[r['D'] for r in cert],s=80,color='#1766a5',label='Independently certified target 5',zorder=3)
ax.scatter([r['resources']['Q'] for r in bad],[r['resources']['D'] for r in bad],s=70,marker='x',color='#b8452b',label='Verified harmful fault',zorder=3)
for r in cert:ax.annotate(f"Q={r['Q']}, D={r['D']}",(r['Q'],r['D']),xytext=(5,8),textcoords='offset points',fontsize=9)
ax.set(xlabel='Physical qubits Q',ylabel='Compiled circuit depth D',title='Actual allocation/scheduling outcomes',yscale='log');ax.grid(alpha=.2);ax.legend(loc='upper right',fontsize=8);ax.set_ylim(28,500)
ax=axes[1]
for name,color,offset,label in [('low_qubit','#1766a5',.95,'Q=36, D=329'),('low_qd','#bc602c',1.05,'Q=105, D=46')]:
 data=[r for r in ler['arms'] if r['case']==name];x=[r['p']*offset for r in data];y=[r['rate'] for r in data];lo=[r['rate']-r['simultaneous_interval'][0] for r in data];hi=[r['simultaneous_interval'][1]-r['rate'] for r in data]
 ax.errorbar(x,y,yerr=[lo,hi],fmt='o-',color=color,capsize=4,label=label)
ax.set(xscale='log',yscale='log',xlabel='Physical error probability p (points offset for visibility)',ylabel='Decoder-conditional logical failure probability',title='Matched decoder; intervals overlap');ax.grid(alpha=.2);ax.legend(fontsize=9)
fig.suptitle('Shor-product [[25,1,5]] extraction — ideal boundaries, explicit operation noise',fontsize=12)
for ext in ('png','svg','pdf'):fig.savefig(root/('target5_results.'+ext),dpi=180)
save(root/'provenance.json',dict(source=source,inputs=[str(a),str(l),str(f)],qualification='Finite certified alternatives; no global optimum or LER ordering. Four-arm simultaneous 95% Clopper-Pearson intervals; one-mechanism decoder.'))
print(root/'target5_results.png')
