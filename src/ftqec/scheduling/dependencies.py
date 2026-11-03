"""Conservative commutation DAG and physical, unit-duration list schedules.

Explicit dependencies are always retained. Reordering is a candidate operation,
not a fault-tolerance proof. Every output needs noiseless and fault validation.
"""
from dataclasses import replace
from ..circuits.model import Circuit


def commute(a,b):
    if not set(a.qubits)&set(b.qubits):return True
    if a.gate==b.gate=='CZ':return True
    if a.gate==b.gate=='CX':return a.qubits[0]!=b.qubits[1] and b.qubits[0]!=a.qubits[1]
    if {a.gate,b.gate}=={'CX','CZ'}:
        cx=a if a.gate=='CX' else b
        cz=b if a.gate=='CX' else a
        return cx.qubits[1] not in cz.qubits
    return False


def dependencies(c):
    c.validate()
    deps=[set(op.deps) for op in c.operations]
    wires=[[] for _ in range(c.num_qubits)]
    for i,op in enumerate(c.operations):
        for q in op.qubits:
            for j in wires[q]:
                if not commute(c.operations[j],op):deps[i].add(j)
            wires[q].append(i)
    return deps


def reorder(c,method='critical_path'):
    if method not in ('list','critical_path','conflict_color','resource'):raise ValueError('Unsupported scheduling algorithm')
    deps=dependencies(c);n=len(deps);successors=[set() for _ in deps]
    for i,ds in enumerate(deps):
        for j in ds:successors[j].add(i)
    height=[1]*n
    for i in reversed(range(n)):height[i]=1+max((height[j] for j in successors[i]),default=0)
    pending=[len(ds) for ds in deps];ready={i for i,v in enumerate(pending) if not v};order=[];layers=[]
    while ready:
        conflicts={i:sum(bool(set(c.operations[i].qubits)&set(c.operations[j].qubits)) for j in ready if i!=j) for i in ready}
        def key(i):
            if method=='list':return (i,)
            if method=='conflict_color':return (-conflicts[i],-height[i],i)
            if method=='resource':return (conflicts[i],-height[i],i)
            return (-height[i],conflicts[i],i)
        selected=[];used=set()
        for i in sorted(ready,key=key):
            qs=set(c.operations[i].qubits)
            if not used&qs:selected.append(i);used|=qs
        assert selected
        layers.append(selected);order.extend(selected)
        ready.difference_update(selected)
        for i in selected:
            for j in successors[i]:
                pending[j]-=1
                if pending[j]==0:ready.add(j)
    if len(order)!=n:raise ValueError('Cyclic dependency graph')
    remap={old:new for new,old in enumerate(order)}
    out=Circuit.from_dict(c.to_dict())
    out.operations=[replace(c.operations[i],deps=tuple(sorted(remap[j] for j in deps[i]))) for i in order]
    out.experiment=dict(out.experiment,scheduler=dict(method=method,layer_count=len(layers),dag_edges=sum(map(len,deps)),optimality='not claimed',fault_tolerance='requires recertification'))
    out.validate()
    return out


def exact_small(c,node_limit=100000,operation_limit=20):
    """Exhaustive subset-layer scheduling on small unit-duration DAGs.

    The returned optimum is for the conservative dependency DAG, not for all
    possible quantum rewrites. Replaying this bounded search checks its claim.
    """
    from itertools import combinations
    if any(op.gate=='BARRIER' for op in c.operations):raise ValueError('Exact scheduler requires unit-duration operations')
    if len(c.operations)>operation_limit:return None,dict(status='UNSUPPORTED',reason='exact scheduling operation safeguard',operation_limit=operation_limit)
    deps=dependencies(c);n=len(deps);all_done=(1<<n)-1
    masks=[sum(1<<j for j in ds) for ds in deps];best=None;nodes=0;memo={};limited=False
    def visit(done,layers):
        nonlocal best,nodes,limited
        nodes+=1
        if nodes>node_limit:limited=True;return
        if done==all_done:
            if best is None or len(layers)<len(best):best=list(layers)
            return
        if best is not None and len(layers)>=len(best):return
        if memo.get(done,n+1)<=len(layers):return
        memo[done]=len(layers)
        ready=[i for i in range(n) if not (done>>i&1) and masks[i]&done==masks[i]]
        for size in range(len(ready),0,-1):
            for group in combinations(ready,size):
                qs=[q for i in group for q in c.operations[i].qubits]
                if len(qs)!=len(set(qs)):continue
                visit(done|sum(1<<i for i in group),layers+[group])
                if limited:return
    visit(0,[])
    receipt=dict(status='UNKNOWN' if limited else 'OPTIMAL_FOR_DECLARED_DAG',nodes=nodes,node_limit=node_limit,layers=best,scope='unit-duration explicit and noncommutation dependencies')
    if best is None:return None,receipt
    order=[i for layer in best for i in layer];remap={i:j for j,i in enumerate(order)}
    out=Circuit.from_dict(c.to_dict());out.operations=[replace(c.operations[i],deps=tuple(sorted(remap[j] for j in deps[i]))) for i in order]
    out.experiment=dict(out.experiment,exact_schedule=receipt);out.validate()
    return out,receipt
