"""Independent algebraic input checks, separate from extraction certificates."""
import json,time,itertools
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.codes.input import load
from ftqec.codes.pauli import Pauli
from ftqec.codes.distance import certify_code,verify_code
source=source_identity();root=Path('results/general_competitive/algebraic')/source
states=Path('results/general_competitive/final')/source/'optimizer'
for path in sorted(states.glob('*/checkpoint.json')):
 name=path.parent.name
 if name in ('surface10_seed8','surface10_seed16','color_small'):continue
 state=json.loads(path.read_text());code=load(state['code']).code;target=max(2,state['config']['target']);start=time.perf_counter();cpu=time.process_time()
 if name.startswith('surface'):
  result=certify_code(code,target);assert result['status']=='CERTIFIED' and verify_code(code,result)['verified']
 else:
  witness=None;counts={}
  for weight in range(1,target+1):
   count=0
   for qs in itertools.combinations(range(code.n),weight):
    for axes in itertools.product('XYZ',repeat=weight):
     count+=1;x=sum(1<<q for q,a in zip(qs,axes) if a in 'XY');z=sum(1<<q for q,a in zip(qs,axes) if a in 'YZ');p=Pauli(code.n,x,z)
     if not code.syndrome(p) and not code.is_stabilizer(p):witness=str(p);break
    if witness:break
   counts[str(weight)]=count
   if witness:break
  assert witness
  distance=weight;strings=list(map(str,code.generators));group={0}
  for g in code.generators:group|={v^g.packed for v in list(group)}
  checked=0
  for w in range(1,distance):
   for qs in itertools.combinations(range(code.n),w):
    for axes in itertools.product('XYZ',repeat=w):
     checked+=1
     commutes=all(sum(g[q]!='I' and g[q]!=a for q,a in zip(qs,axes))%2==0 for g in strings)
     x=sum(1<<q for q,a in zip(qs,axes) if a in 'XY');z=sum(1<<q for q,a in zip(qs,axes) if a in 'YZ')
     assert not commutes or (x|(z<<code.n)) in group
  p=Pauli.parse(witness);assert all(sum(a!='I' and b!='I' and a!=b for a,b in zip(witness,g))%2==0 for g in strings) and p.packed not in group
  result=dict(status='CERTIFIED',exact_distance=distance,lower_bound=distance,upper_witness=witness,producer_counts=counts,independent=dict(verified=True,examined=checked,method='string commutation and explicit stabilizer-group closure'),scope='algebraic data-Pauli distance only')
 save(root/(name+'.json'),dict(source=source,code=code.to_dict(),certificate=result,cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
 print(name,result.get('exact_distance'),flush=True)
