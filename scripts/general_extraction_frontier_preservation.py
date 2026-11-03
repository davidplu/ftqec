"""Preserve historical certified alternatives beside newly verified frontiers."""
import json,time
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.evaluation.resources import resources
from ftqec.optimization.selection import pareto
source=source_identity();root=Path('results/pareto')/source;new=Path('results/exports')/source/'finalists'
while not (new/'complete.json').exists():time.sleep(2)
old='2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58';groups={};archive=[]
def add(data,metric,target,identity,evidence_source,origin,historical):
 c=Circuit.from_dict(data);actual=resources(c)
 assert all(metric[k]==actual[k] for k in ('Q','D','QD','two_q_gates'))
 record=dict(id=identity,circuit=digest(data),code=c.code.to_dict(),target=target,resources=actual,evidence_source=evidence_source,origin=origin,historical=historical)
 archive.append(record);groups.setdefault(c.code.input_hash+':'+str(target),[]).append(record)
p=Path('results/pareto/competitive_export')/(old+'.json');d=json.loads(p.read_text())
for r in d['archive']:
 cert=r.get('certify',{})
 if r.get('reference') or cert.get('status')!='CERTIFIED' or not cert.get('independent',{}).get('verified'):continue
 add(r['circuit'],r['resources'],cert['target'],r['id'],cert['source'],str(p),True)
p=Path('results/cross_family/competitive_export')/old/'frontiers.json';d=json.loads(p.read_text())
for family,rows in d['frontiers'].items():
 for r in rows:
  cert=r.get('certify',{})
  if cert.get('status')=='CERTIFIED' and cert.get('independent',{}).get('verified'):add(r['circuit'],r['resources'],cert['target'],r['id'],cert['source'],str(p)+'#'+family,True)
for r in json.loads((new/'index.json').read_text())['records']:
 if r['adopted']:add(json.loads((Path(r['bundle'])/'circuit.json').read_text()),r['resources'],r['target'],r['id'],source,r['bundle'],False)
frontiers={}
for key,rows in groups.items():
 unique={}
 for r in rows:
  cid=r['circuit']
  if cid not in unique or not r['historical']:unique[cid]=r
 frontiers[key]=pareto(list(unique.values()))
save(root/'all_known_frontiers.json',dict(source=source,frontiers=frontiers,archive=archive,qualification='Historical certificates retain their original evidence source and verified records; they are not relabelled as current-source proofs. Actual resource tuples recomputed. Independent reference circuits excluded from discovery frontiers. All dominated positive records retained. Finite known frontier, not global optimum.'))
print('PRESERVED_ALL_KNOWN_FRONTIERS',sum(len(v) for v in frontiers.values()),flush=True)
