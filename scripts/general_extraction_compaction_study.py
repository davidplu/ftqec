"""Isolate unused-ancilla removal from scheduling on certified discoveries."""
import json,time,hashlib
from pathlib import Path
from dataclasses import replace
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.architectures.population import Genome
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
from ftqec.certification.eligibility import assess,verify
source=source_identity();base=Path('results/pareto')/source/'deferred_frontier';root=Path('results/pareto')/source/'compaction_study';root.mkdir(parents=True,exist_ok=True)
packets=[json.loads(p.read_text()) for p in base.glob('*.json') if p.name not in ('protocol.json','complete.json')]
parents=[p['origin'] for p in packets if p['answer']['result'].get('status')=='CERTIFIED']
protocol=dict(source=source,selection='All newly certified deferred frontier discoveries; compact unused ancillas without changing scheduling or gates',parents=[r['id'] for r in parents],work=20000000,cpu=120,wall=240,memory_mb=384,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
start=time.perf_counter();cpu=time.process_time();rows=[]
for parent in parents:
 cid=parent['id'];path=root/(cid+'.json')
 if path.exists():rows.append(str(path));continue
 genome=replace(Genome.from_dict(parent['genome']),compact_ancillas=True)
 def task(data,tier,**limits):return Task(data,tier,Circuit.from_dict(parent['circuit']).code.input_hash,{'p':.001},'auto',0,source,dict(memory_mb=384,cpu_seconds=120,wall_seconds=240,**limits))
 t=task(dict(code_input=parent['input_code'],genome=genome.to_dict()),'construct');construction=batch([t],1)[0]
 packet=dict(parent=parent,genome=genome.to_dict(),construction_task=t.to_dict(),construction=construction)
 if construction['result'].get('status')=='STRUCTURALLY_VALID':
  data=construction['result']['circuit'];c=Circuit.from_dict(data);e=assess(c);v=verify(c,e);assert v['verified'];packet.update(eligibility=e,eligibility_verification=v)
  t=task(data,'certify',target=5,proof_method='auto',work=20000000,proof_directory=str(root/'proofs'/cid));a=batch([t],1)[0];packet.update(task=t.to_dict(),answer=a);print('COMPACT',cid[:12],construction['result']['resources']['Q'],construction['result']['resources']['D'],a['result'].get('status'),flush=True)
 save(path,packet);rows.append(str(path))
save(root/'complete.json',dict(source=source,records=rows,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
