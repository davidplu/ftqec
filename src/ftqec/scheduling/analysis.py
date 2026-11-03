"""Diagnose the concrete earliest wire-order schedule, without optimality claims."""
from collections import Counter
from ..results.artifacts import digest
from .scheduler import schedule
from .dependencies import commute


def analyze(c):
    s=schedule(c);last={};edges=[];heights=[];parents=[]
    for i,op in enumerate(c.operations):
        deps={j:{'explicit'} for j in op.deps}
        for q in op.qubits:
            if q in last:
                j=last[q];deps.setdefault(j,set()).add('commuting_wire_order' if commute(c.operations[j],op) else 'noncommuting_wire_order')
            last[q]=i
        for j,reasons in sorted(deps.items()):edges.append(dict(before=j,after=i,reasons=sorted(reasons)))
        parent=max(deps,key=lambda j:heights[j],default=None);parents.append(parent)
        heights.append((heights[parent] if parent is not None else 0)+(op.gate!='BARRIER'))
    end=max(range(len(heights)),key=heights.__getitem__,default=None);path=[]
    while end is not None:
        op=c.operations[end];path.append(dict(operation=end,gate=op.gate,qubits=list(op.qubits),check=op.check,role=op.role,start=s.starts[end]));end=parents[end]
    layers=[dict(layer=t,operations=[i for i,start in enumerate(s.starts) if start==t],gate_counts=dict(Counter(op.gate for op,start in zip(c.operations,s.starts) if start==t))) for t in range(s.depth)]
    return dict(circuit=digest(c.to_dict()),depth=s.depth,critical_path=list(reversed(path)),dependencies=edges,layers=layers,
                gate_counts=dict(Counter(op.gate for op in c.operations)),qualification='Critical path in the actual ordered circuit; noncommutation edges constrain local swaps, not all possible collective circuit rewrites')
