"""Export static research figures from completed measured records."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root=Path("results/autonomous/release/figures");root.mkdir(parents=True,exist_ok=True)
state=json.loads(Path("results/discovery/autonomous/surface_target10/checkpoint.json").read_text())
rows=[r for r in state["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"]
fig,ax=plt.subplots(figsize=(7,4.4))
ax.scatter([r["resources"]["Q"] for r in rows],[r["resources"]["D"] for r in rows],alpha=.65,s=45,label="Autonomous candidates")
ref=json.loads(Path("results/certificates/reference_validation/target10.json").read_text())["resources"]
ax.scatter([ref["Q"]],[ref["D"]],marker="D",facecolors="none",edgecolors="black",s=60,label="Reference control (not a search seed)")
ax.legend(fontsize=8)
ax.set(xlabel="Physical qubits Q",ylabel="Scheduled depth D (unit gate durations)",yscale="log",title="Target-10 resources: independently certified circuits")
ax.grid(alpha=.2);fig.text(.02,.01,"Extraction-only model; ideal syndrome boundaries. No global-optimality claim.",fontsize=9)
fig.tight_layout(rect=(0,.04,1,1));fig.savefig(root/"target10_resources.png",dpi=180);plt.close(fig)
records=json.loads(Path("results/ler/autonomous_decoder/results.json").read_text())["rows"]
records=[r for r in records if r["target"]==10 and r["p"]==.01 and "simulation" in r]
fig,ax=plt.subplots(figsize=(8,4.4));labels=[]
for i,r in enumerate(records):
 s=r["simulation"];lo,hi=s["confidence"]
 ax.errorbar(i,s["rate"],yerr=[[s["rate"]-lo],[hi-s["rate"]]],fmt="o",capsize=5)
 labels.append(r["id"][:8]+"\n"+("Matching" if r["requested_decoder"]=="matching" else "Lookup"))
ax.set_xticks(range(len(labels)),labels);ax.set(ylabel="Conditional logical failure probability",title="Same physical noise (p=0.01), different decoders")
ax.grid(axis="y",alpha=.2);fig.text(.02,.01,"Candidate-wise sequential intervals; logical-Z sector; zero observed failures is not zero LER.",fontsize=9)
fig.tight_layout(rect=(0,.04,1,1));fig.savefig(root/"target10_decoders.png",dpi=180);plt.close(fig)
print("FIGURES_COMPLETE")
