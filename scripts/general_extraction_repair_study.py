"""Prospective six-arm composed repair study of a verified negative, not code-only discovery."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.codes.families import shor_product
from ftqec.architectures.population import Genome,mutate
from ftqec.architectures.repair import diagnose
from ftqec.circuits.model import Circuit
from ftqec.certification.eligibility import assess,verify
from ftqec.faults.verification import replay
from ftqec.execution.tasks import Task,batch
source=source_identity();root=Path('results/repair_trajectories')/source/'shor5_six_arm_rescreened';root.mkdir(parents=True,exist_ok=True)
old='2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58'
packet=json.loads((Path('results/competitive_export/target5_followup')/old/'seed0_nested_mitm.json').read_text())
parent=Circuit.from_dict(packet['task']['circuit']);witness=packet['answer']['result']['witness'];inp=shor_product(5)
ancestry=json.loads(Path('results/competitive_export/order_development/6c675260b459a563ddafe02e5da9696b92a2f812064ac29e441a6181fceece2d/1793390748609460000/seed0.json').read_text())
genome=Genome.from_dict(ancestry['inputs'][1]['genome'])
assert digest(parent.to_dict())==digest(ancestry['tasks'][1]['circuit'])
protocol=dict(source=source,parent=digest(parent.to_dict()),code=inp.to_dict(),seeds=list(range(6)),workers=2,
 target=5,methods=['decomposition','mitm'],proof_work=20000000,cpu=120,wall=240,memory_mb=384,
 shots=256,decoder='one_mechanism_lookup',p=.001,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 qualification='Development repair descendants of a known invalid circuit, not autonomous code-only initialization; elimination of a mapped witness is not a certificate.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
start=time.perf_counter();cpu=time.process_time();save(root/'parent_diagnosis.json',diagnose(parent,witness))
def task(c,tier,seed,**limits):return Task(c,tier,inp.identity,{'p':.001},protocol['decoder'],seed,source,dict(memory_mb=384,cpu_seconds=120,wall_seconds=240,**limits))
def run(label,tasks):
 path=root/(label+'.json')
 if path.exists():return json.loads(path.read_text())['answers']
 answers=batch(tasks,2);save(path,dict(tasks=[t.to_dict() for t in tasks],answers=answers));return answers
children=[mutate(inp,genome,i,witness,target=5) for i in range(6)]
save(root/'genomes.json',[dict(seed=i,parent=protocol['parent'],genome=g.to_dict()) for i,g in enumerate(children)])
constructed=run('construction',[task(dict(code_input=inp.to_dict(),genome=g.to_dict()),'construct',i) for i,g in enumerate(children)])
rows=[]
for i,answer in enumerate(constructed):
 row=dict(seed=i,parent=protocol['parent'],genome=children[i].to_dict(),construction=answer);rows.append(row)
 if answer['result'].get('status')!='STRUCTURALLY_VALID':continue
 c=Circuit.from_dict(answer['result']['circuit']);row['circuit']=digest(c.to_dict())
 eligibility=assess(c);audit=verify(c,eligibility);assert audit['verified'];row['eligibility']=eligibility;row['eligibility_verification']=audit
 # Transfer only unambiguous operation contexts. A failed mapping is not elimination.
 mapped=[]
 from ftqec.certification.inventory import fault_at
 for f in witness['faults']:
  original=parent.operations[f['operation']]
  matches=[j for j,op in enumerate(c.operations) if (op.gate,op.check,op.role,op.round_index,op.interval,op.interaction_position)==(original.gate,original.check,original.role,original.round_index,original.interval,original.interaction_position)]
  if len(matches)!=1:break
  mapped.append(fault_at(c,matches[0],f['label']).to_dict())
 if len(mapped)==len(witness['faults']) and len({f['location'] for f in mapped})==len(mapped):
  effect=replay(c,mapped);row['mapped_mechanism']=dict(faults=mapped,effect=effect,harmful=not effect['detector_outcomes'] and bool(effect['logical_coset']))
 else:row['mapped_mechanism']=dict(status='NOT_TRANSFERABLE',qualification='Architecture changed operation contexts; no mechanism-elimination claim')
 screened=run(f'seed{i}_screen',[task(c.to_dict(),'screen',i,target=5,work=20000)])[0];row['screen']=screened
 if screened['result'].get('status') in ('INVALID','FAULT_INVALID'):continue
 if row['mapped_mechanism'].get('harmful'):
  row['status']='INVALID';row['reason']='independently replayed mapped weight-four witness';continue
 row['simulation']=run(f'seed{i}_simulation',[task(c.to_dict(),'simulation',i,shots=256,max_decoder_faults=10000)])[0]
 for method in protocol['methods']:
  a=run(f'seed{i}_{method}',[task(c.to_dict(),'certify',i,target=5,work=20000000,proof_method=method,proof_directory=str(root/'proofs'/f'seed{i}'/method))])[0]
  row[method]=a;print('REPAIR',i,method,a['result'].get('status'),a['result'].get('reason'),flush=True)
  if a['result'].get('status') in ('CERTIFIED','INVALID'):break
 save(root/'rows_checkpoint.json',rows)
save(root/'rows.json',rows);save(root/'complete.json',dict(source=source,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
