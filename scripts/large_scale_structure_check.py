import sys,json,random
from pathlib import Path
sys.path.insert(0,str(Path('scripts').resolve()))
from large_scale_structure import ancilla_invariant
from ftqec.optimization.store import PopulationStore
from ftqec.circuits.model import Circuit
from ftqec.results.artifacts import source_identity,save
s=source_identity();root=Path('results/populations')/s/'study/surface3_hybrid_p100_n100_s2001';checked=[]
with PopulationStore(root/'population.sqlite',readonly=True) as db:
 for ix,item in enumerate(db.summaries()):
  c=Circuit.from_dict(db.get(item['id'])['circuit']);d=c.to_dict();anc=list(range(c.code.n,c.num_qubits));order=list(anc);random.Random(70000+ix).shuffle(order);mapping=dict(zip(anc,order));wire=lambda q:mapping.get(q,q)
  d['syndrome_qubits']=[wire(q) for q in d['syndrome_qubits']];d['flag_qubits']=[wire(q) for q in d['flag_qubits']]
  for op in d['operations']:op['qubits']=[wire(q) for q in op['qubits']]
  changed=Circuit.from_dict(d);assert ancilla_invariant(c)==ancilla_invariant(changed)
  checked.append(item['id'])
save(Path('results/large_scale/development')/s/'ancilla_relabel_invariant_validation.json',dict(source=s,checked=checked,seed_rule='70000 + sorted candidate index',scope='Random ancilla renaming leaves four-round colored timed-structure invariant unchanged. Inequality distinguishes structures; equality is not an isomorphism proof. Data-wire code automorphisms are not quotiented.'))
print('RELABEL_INVARIANCE_VALIDATED',len(checked))