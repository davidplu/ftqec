"""Prospective generic allocation neighbors of the first code-only target-five positive."""
import json,time,hashlib
from pathlib import Path
from dataclasses import replace
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.codes.input import load
from ftqec.architectures.population import Genome
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
from ftqec.certification.eligibility import assess,verify
source=source_identity();run=Path('results/non_graphlike')/source/'population_study/shor5_random_101';state=json.loads((run/'checkpoint.json').read_text())
parent=next(r for r in state['rows'] if r.get('certify',{}).get('status')=='CERTIFIED');inp=load(state['code']);genome=Genome.from_dict(parent['genome'])
slots=[];s=1
while s<len(inp.code.generators):slots.append(s);s*=2
slots.append(len(inp.code.generators));root=Path('results/pareto')/source/'allocation_study';root.mkdir(parents=True,exist_ok=True)
protocol=dict(source=source,parent=parent['id'],parent_circuit=digest(parent['circuit']),input_code=state['code'],slots=slots,target=5,workers=2,memory_mb=384,task_cpu=120,task_wall=240,proof_work=20000000,shots=1024,p=.001,decoder='one_mechanism_lookup',driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),qualification='Post-discovery allocation development using powers of two plus all checks; no reference circuits. Noisy and fault-tolerance effects must be re-evaluated.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
start=time.perf_counter();cpu=time.process_time()
def task(data,tier,seed,**limits):return Task(data,tier,inp.identity,{'p':.001},'one_mechanism_lookup',seed,source,dict(memory_mb=384,cpu_seconds=120,wall_seconds=240,**limits))
def run_tasks(label,tasks):
 path=root/(label+'.json')
 if path.exists():return json.loads(path.read_text())['answers']
 answers=batch(tasks,2);save(path,dict(tasks=[t.to_dict() for t in tasks],answers=answers));return answers
genomes=[replace(genome,ancilla_slots=slots_i,schedule='critical_path',interaction_layers=(),compact_ancillas=True) for slots_i in slots]
constructed=run_tasks('construction',[task(dict(code_input=inp.to_dict(),genome=g.to_dict()),'construct',i) for i,g in enumerate(genomes)])
rows=[]
for slot,g,a in zip(slots,genomes,constructed):
 row=dict(slot=slot,genome=g.to_dict(),parent=parent['id'],construction=a);rows.append(row)
 if a['result'].get('status')!='STRUCTURALLY_VALID':continue
 c=Circuit.from_dict(a['result']['circuit']);e=assess(c);v=verify(c,e);assert v['verified'];row.update(circuit=c.to_dict(),resources=a['result']['resources'],eligibility=e,eligibility_verification=v)
 row['screen']=run_tasks(f'slot{slot}_screen',[task(c.to_dict(),'screen',slot,target=5,work=20000)])[0]
 if row['screen']['result'].get('status') in ('INVALID','FAULT_INVALID'):continue
 row['simulation']=run_tasks(f'slot{slot}_simulation',[task(c.to_dict(),'simulation',slot,shots=1024,max_decoder_faults=10000)])[0]
 row['certification']=run_tasks(f'slot{slot}_certify',[task(c.to_dict(),'certify',slot,target=5,work=20000000,proof_method='auto',proof_directory=str(root/'proofs'/str(slot)))])[0]
 print('ALLOCATION',slot,row['resources']['Q'],row['resources']['D'],row['certification']['result'].get('status'),flush=True);save(root/'rows_checkpoint.json',rows)
save(root/'rows.json',rows);save(root/'complete.json',dict(source=source,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
