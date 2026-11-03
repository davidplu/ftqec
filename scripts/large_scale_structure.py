"""Conservative within-code diversity invariant under ancilla wire relabeling.

Different signatures imply different timed gate/detector structures with fixed
input data-wire labels. Equal signatures need not imply isomorphism. This is a
lower bound on structural classes, not code-automorphism canonicalization.
"""
from ftqec.results.artifacts import digest

def ancilla_invariant(c):
 ready=[0]*c.num_qubits;ends=[];events=[]
 for op in c.operations:
  begin=max([ready[q] for q in op.qubits]+[ends[i] for i in op.deps]+[0]);end=begin+int(op.gate!='BARRIER');ends.append(end)
  for q in op.qubits:ready[q]=end
  if op.gate!='BARRIER':events.append((begin,op))
 colors=[digest(('data',q)) if q<c.code.n else digest('ancilla') for q in range(c.num_qubits)]
 for _ in range(4):
  neighbors=[[] for _ in colors]
  for start,op in events:
   for port,q in enumerate(op.qubits):neighbors[q].append((start,op.gate,port,tuple(colors[w] for w in op.qubits)))
  colors=[digest((colors[q],sorted(neighbors[q]))) for q in range(c.num_qubits)]
 gates=sorted((start,op.gate,tuple(colors[q] for q in op.qubits)) for start,op in events)
 records={op.record:(start,op.gate,tuple(colors[q] for q in op.qubits)) for start,op in events if op.record}
 detectors=sorted((sorted(records[r] for r in row),offset) for row,offset in zip(c.detectors,c.detector_offsets or [0]*len(c.detectors)))
 return digest(dict(gates=gates,wires=sorted(colors),detectors=detectors,observables=sorted(sorted(records[r] for r in row) for row in c.observables),boundary=c.boundary_model))