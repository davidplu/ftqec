"""Prospective exact-method follow-up on unresolved graph-ineligible Shor5 cases."""
import sys,json,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path('.private/next-source').resolve()))
from ftqec.results.artifacts import source_identity,save
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
from ftqec.certification.eligibility import assess,verify
source=source_identity();out=Path('results/competitive_export/target5_followup')/source;out.mkdir(parents=True,exist_ok=True)
old=Path('results/competitive_export/order_development/6c675260b459a563ddafe02e5da9696b92a2f812064ac29e441a6181fceece2d/1793390748609460000')
# First unresolved nested and first unresolved adjacent case in original seed order.
choices=[('seed0_nested',old/'seed0.json',1),('seed1_adjacent',old/'seed1.json',0)]
protocol=dict(source=source,selection='First unresolved nested and adjacent case by original seed order; not selected by successful proof outcome',cases=[x[0] for x in choices],methods=['decomposition','mitm'],work=20000000,cpu_seconds=180,wall_seconds=360,memory_mb=512,workers=1,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Follow-up after initial bounded Shor5 study; timings not pooled with original work limits')
if (out/'protocol.json').exists():assert json.loads((out/'protocol.json').read_text())==protocol
else:save(out/'protocol.json',protocol)
start=time.perf_counter();cpu=time.process_time()
for label,path,index in choices:
 packet=json.loads(path.read_text());assert packet['answers'][index]['result']['status']=='UNKNOWN'
 cc=Circuit.from_dict(packet['tasks'][index]['circuit']);eligibility=assess(cc);independent=verify(cc,eligibility);assert independent['verified'] and not eligibility['eligible']
 save(out/(label+'_input.json'),dict(origin=str(path),origin_index=index,circuit=cc.to_dict(),eligibility=eligibility,independent=independent))
 for method in protocol['methods']:
  resultpath=out/(label+'_'+method+'.json')
  if resultpath.exists():continue
  t=Task(cc.to_dict(),'certify',cc.code.input_hash,{'p':.001},'matching',0,source,dict(target=5,proof_method=method,work=20000000,memory_mb=512,cpu_seconds=180,wall_seconds=360,proof_directory=str(out/'proofs'/label/method)))
  a=batch([t],1)[0];save(resultpath,dict(task=t.to_dict(),answer=a));print('TARGET5_FOLLOWUP',label,method,a['result'].get('status'),a['result'].get('reason'),flush=True)
save(out/'complete.json',dict(source=source,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start));print('TARGET5_FOLLOWUP_COMPLETE',flush=True)

