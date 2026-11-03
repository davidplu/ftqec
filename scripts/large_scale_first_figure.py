"""Source-bound plot of actual independently verified first-campaign circuits."""
import json,hashlib
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ftqec.results.artifacts import source_identity,save
s=source_identity();path=Path('results/exports/large_scale')/s/'first_closed_campaign/index.json';rows=json.loads(path.read_text())['records'];rows=sorted(rows,key=lambda r:r['resources']['Q']);root=Path('results/large_scale/reports')/s;root.mkdir(parents=True,exist_ok=True)
fig,ax=plt.subplots(figsize=(8,5));q=[r['resources']['Q'] for r in rows];d=[r['resources']['D'] for r in rows]
ax.scatter(q,d,color='#126e82',s=70,zorder=3)
for row in rows:
 r=row['resources'];ax.annotate('D='+str(r['D'])+'; QD='+str(r['QD']),(r['Q'],r['D']),xytext=(0,12),textcoords='offset points',ha='center',fontsize=9)
ax.set(xlabel='Physical qubits Q',ylabel='Circuit depth D',xlim=(9,18),ylim=(0,56),xticks=q);ax.grid(axis='y',alpha=.22);ax.spines[['top','right']].set_visible(False)
ax.set_title('Independently verified resource tradeoffs',loc='left',fontsize=14,pad=18)
fig.text(.125,.93,'First closed surface-code campaign; requested extraction distance 3',fontsize=10,color='#45515c')
fig.text(.125,.015,'Each point is an actual circuit with 24 two-qubit gates. Operation-local faults; ideal boundaries.\nOne campaign only: this figure does not establish matched-compute search superiority.',fontsize=8,color='#45515c')
fig.subplots_adjust(bottom=.18,top=.84)
for extension in ('png','svg','pdf'):fig.savefig(root/('FIRST_CLOSED_FRONTIER.'+extension),dpi=180,bbox_inches='tight')
plt.close(fig);save(root/'first_closed_frontier_plot.json',dict(source=s,data=str(path),data_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),points=[dict(circuit=r['circuit'],resources=r['resources']) for r in rows],script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
print(root/'FIRST_CLOSED_FRONTIER.png')