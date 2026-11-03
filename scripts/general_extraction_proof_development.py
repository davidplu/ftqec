"""Matched preliminary exact-method study; no architecture tuning on final families."""
import argparse,json,sys,time,hashlib,shutil
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--source-root',default='src');args=parser.parse_args()
sys.path.insert(0,str(Path(args.source_root).resolve()))
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
from ftqec.certification.eligibility import assess,verify
from ftqec.architectures.repair import diagnose
source=source_identity();root=Path('results/general_extraction/proof_development')/source
root.mkdir(parents=True,exist_ok=True)
old='2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58'
follow=Path('results/competitive_export/target5_followup')/old
repair=Path('results/competitive_export/delivery')/old/'exports/repair_compressed/circuit.json'
inputs=[('shor4_positive',json.loads(repair.read_text(encoding='utf-8')),4),
        ('shor5_unresolved',json.loads((follow/'seed1_adjacent_input.json').read_text(encoding='utf-8'))['circuit'],5)]
protocol=dict(source=source,cases=[(n,digest(c),t) for n,c,t in inputs],methods=['decomposition_legacy','decomposition'],
 work=2000000,cpu=90,wall=180,memory_mb=256,workers=1,scope='Matched exploratory proof obligations, not final-family evaluation',
 driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol);shutil.copytree(Path(args.source_root)/'ftqec',root/'source/ftqec',ignore=shutil.ignore_patterns('__pycache__'))
start=time.perf_counter();cpu=time.process_time()
packet=json.loads((follow/'seed0_nested_mitm.json').read_text(encoding='utf-8'))
save(root/'shor5_negative_diagnosis.json',diagnose(Circuit.from_dict(packet['task']['circuit']),packet['answer']['result']['witness']))
for name,data,target in inputs:
 c=Circuit.from_dict(data);e=assess(c);v=verify(c,e);assert v['verified']
 save(root/(name+'_input.json'),dict(circuit=data,eligibility=e,independent=v))
 for method in protocol['methods']:
  path=root/(name+'_'+method+'.json')
  if path.exists():continue
  t=Task(data,'certify',c.code.input_hash,{'p':.001},'matching',0,source,dict(target=target,work=protocol['work'],proof_method=method,memory_mb=256,cpu_seconds=90,wall_seconds=180,proof_directory=str(root/'proofs'/name/method)))
  a=batch([t],1)[0];save(path,dict(task=t.to_dict(),answer=a));print(name,method,a['result'].get('status'),a['result'].get('reason'),flush=True)
save(root/'complete.json',dict(source=source,wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu))
