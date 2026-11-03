"""Code-only constraint search for hook-guided bipartite interaction coloring."""
from itertools import permutations
import random
from ..codes.pauli import Pauli
from ..codes.logicals import logical_basis,logical_effect
from ..certification.structural import graph,produce
from .synthesis import channel_masks,Effects


def colored_orders(inp,target,seed,node_limit=10000,joint=False):
    code=inp.code;masks=channel_masks(code)
    if not masks or any(set(str(p))-{'I'} not in ({'X'},{'Z'}) for p in code.generators):return None,dict(status='INAPPLICABLE',reason='CSS channels required')
    width=max(p.weight for p in code.generators)
    if width>4:return None,dict(status='INAPPLICABLE',reason='bounded exact coloring domains support check weight at most four')
    pairs=logical_basis(code);rng=random.Random(seed)
    def effect(p):return code.syndrome(p),logical_effect(p,pairs)
    base={effect(Pauli(code.n,(1<<q) if a in 'XY' else 0,(1<<q) if a in 'YZ' else 0)) for q in range(code.n) for a in 'XYZ'}
    cache={};evaluations=0
    def sufficient(items):
        nonlocal evaluations
        for bit,selected in enumerate(masks):
            g=graph(Effects(items),selected,bit)
            if g is None:return False
            key=(bit,tuple(sorted(tuple(e[:3]) for e in g['edges'])))
            if key not in cache:
                p=produce(g,target,work_limit=2000000);evaluations+=1
                cache[key]=p['complete'] and p['lower_bound']>=target
            if not cache[key]:return False
        return True
    domains=[];axes=[]
    for p in code.generators:
        axis='X' if p.x else 'Z';axes.append(axis)
        support=[q for q in range(code.n) if (p.x|p.z)>>q&1];options=[];order_effects={}
        for positions in permutations(range(width),len(support)):
            ordered=sorted(zip(positions,support));order=tuple(q for t,q in ordered);layers=tuple(t for t,q in ordered)
            if order not in order_effects:
                effects=set();suffix=Pauli(code.n)
                for q in reversed(order):
                    for a in 'IXYZ':effects.add(effect(suffix^Pauli(code.n,(1<<q) if a in 'XY' else 0,(1<<q) if a in 'YZ' else 0)))
                    suffix=suffix^Pauli(code.n,(1<<q) if p.x>>q&1 else 0,(1<<q) if p.z>>q&1 else 0)
                order_effects[order]=effects if sufficient(base|effects) else None
            effects=order_effects[order]
            if effects is not None:options.append((order,layers,effects))
        rng.shuffle(options);domains.append(options)
        if not options:return None,dict(status='NO_GUIDED_DOMAIN',check=len(domains)-1,graph_evaluations=evaluations)
    selected={};occupied=set();nodes=0;exhausted=False
    def keys(i,option):
        return {(None if joint else axes[i],q,t) for q,t in zip(option[0],option[1])}
    def compatible(i,option):
        if keys(i,option)&occupied:return False
        if not joint:return True
        times=dict(zip(option[0],option[1]))
        for j,other in selected.items():
            if axes[i]==axes[j]:continue
            other_times=dict(zip(other[0],other[1]));common=times.keys()&other_times.keys()
            # CNOT commutators between opposite-axis checks cancel only when
            # their relative ordering has even parity over the shared support.
            if sum(times[q]<other_times[q] for q in common)%2:return False
        return True
    def visit():
        nonlocal nodes,exhausted
        nodes+=1
        if nodes>node_limit:exhausted=True;return False
        if len(selected)==len(domains):return sufficient(base|set().union(*(o[2] for o in selected.values())))
        feasible=[]
        for i,domain in enumerate(domains):
            if i in selected:continue
            options=[o for o in domain if compatible(i,o)]
            if not options:return False
            feasible.append((len(options),-len(domain[0][0]),i,options))
        _,_,i,options=min(feasible,key=lambda x:x[:3])
        for option in options:
            used=keys(i,option);occupied.update(used);selected[i]=option
            if visit():return True
            occupied.difference_update(used);del selected[i]
            if exhausted:return False
        return False
    success=visit()
    receipt=dict(status='GENERATED' if success else 'UNKNOWN' if exhausted else 'GUIDED_DOMAIN_EXHAUSTED',method='code_only_joint_hook_coloring' if joint else 'code_only_hook_guided_constraint_coloring',nodes=nodes,node_limit=node_limit,graph_evaluations=evaluations,domain_sizes=list(map(len,domains)),qualification='Construction guidance only; full physical certification required')
    if not success:return None,receipt
    return (tuple(selected[i][0] for i in range(len(domains))),tuple(selected[i][1] for i in range(len(domains)))),receipt


def compile_layers(c,orders,layers,joint=False):
    from dataclasses import replace
    if len(layers)!=len(c.code.generators):raise ValueError('Coloring coverage')
    width=max(max(ts,default=-1)+1 for ts in layers)
    occupied=set()
    for i,(order,ts) in enumerate(zip(orders,layers)):
        if len(order)!=len(ts) or list(ts)!=sorted(set(ts)) or any(type(t) is not int or t<0 for t in ts):raise ValueError('Coloring domain')
        axis='X' if c.code.generators[i].x else 'Z'
        for q,t in zip(order,ts):
            if (None if joint else axis,q,t) in occupied:raise ValueError('Color conflict')
            occupied.add((None if joint else axis,q,t))
    def layer(op):
        offset=0 if joint or c.code.generators[op.check].x else width
        ts=layers[op.check]
        times={'syndrome_reset':0,'syndrome_prepare':1,'syndrome_basis_readout':3+offset+max(ts),'syndrome_readout':(3 if joint and not c.code.generators[op.check].x else 4)+offset+max(ts)}
        t=2+offset+ts[op.interaction_position] if op.role=='data_interaction' else times[op.role]
        return (op.round_index,t)
    order=sorted(range(len(c.operations)),key=lambda i:(layer(c.operations[i]),i));remap={old:new for new,old in enumerate(order)}
    c.operations=[replace(c.operations[i],deps=tuple(remap[j] for j in c.operations[i].deps)) for i in order]
    c.experiment['coloring']=dict(width=width,joint=joint,layers=[list(ts) for ts in layers],qualification='not a fault-tolerance certificate')
    c.validate();return c
