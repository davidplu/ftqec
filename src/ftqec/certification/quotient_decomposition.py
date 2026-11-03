"""Exact domination of whole physical location domains before separator DP.

A location domain contains identity and complete detector/logical effects. If
that domain is contained in a retained XOR-closed domain, every group of faults
mapped there can be replaced by at most one legal fault at the retained location.
The replacement has identical detector/logical parity and no greater weight.
Conversely retained locations are original physical locations. Hence existence
of a harmful configuration below a target is equivalent in both inventories.
This argument does not split correlated faults or permit two faults per location.
"""
from ..results.artifacts import digest
from . import span_decomposition
VERSION='closed-physical-domain-separator-1'


class Reduced:
    def __init__(self,rows):
        self.values=sorted(rows);self.count=len(self.values);self.hash=digest(self.values)
    def rows(self):return iter(self.values)


def compress(inv):
    rows=list(inv.rows());domains={}
    for op,label,d,l,data in rows:domains.setdefault(op,{(0,0)}).add((d,l))
    retained={};mapping={};index={}
    for op,domain in sorted(domains.items(),key=lambda item:(-len(item[1]),item[0])):
        if len(domain)==1:mapping[op]=None;continue
        options=None
        for effect in domain-{(0,0)}:
            choices=index.get(effect,set());options=set(choices) if options is None else options&choices
            if not options:break
        chosen=next((q for q in sorted(options or ()) if domain<=retained[q]),None)
        if chosen is not None:mapping[op]=chosen;continue
        closed=all((a^c,b^d) in domain for a,b in domain for c,d in domain)
        mapping[op]=op
        if closed:
            retained[op]=domain
            for effect in domain-{(0,0)}:index.setdefault(effect,set()).add(op)
    kept={op for op,target in mapping.items() if op==target}
    return Reduced([row for row in rows if row[0] in kept]),[[op,mapping[op]] for op in sorted(mapping)]


def prove(inv,target,work_limit=200000,state_limit=100000):
    reduced,mapping=compress(inv)
    inner=span_decomposition.prove(reduced,target,work_limit,state_limit)
    return dict(method=VERSION,target=target,inventory_hash=inv.hash,inventory_count=inv.count,
        mapping=mapping,reduced_hash=reduced.hash,reduced_count=reduced.count,inner=inner,
        complete=inner['complete'],witness=inner.get('witness'),lower_bound=inner.get('lower_bound'),
        reason=inner.get('reason'),work=inner.get('work'),width=inner.get('width'),max_states=inner.get('max_states'))


def verify(inv,proof,target,work_limit=200000,state_limit=100000):
    if proof.get('method')!=VERSION or proof.get('target')!=target or proof.get('inventory_hash')!=inv.hash or proof.get('inventory_count')!=inv.count:
        return dict(verified=False,reason='domain reduction identity')
    rows=list(inv.rows());domains={}
    for op,label,d,l,data in rows:domains.setdefault(op,set()).add((d,l))
    pairs=proof.get('mapping',[])
    if not all(isinstance(p,list) and len(p)==2 and type(p[0]) is int and (p[1] is None or type(p[1]) is int) for p in pairs):return dict(verified=False,reason='mapping shape')
    mapping=dict(pairs)
    if len(pairs)!=len(mapping) or set(mapping)!=set(domains):return dict(verified=False,reason='physical location coverage')
    kept={op for op,q in mapping.items() if q==op}
    checked=set()
    for op,destination in mapping.items():
        if destination is None:
            if any(d or l for d,l in domains[op]):return dict(verified=False,reason='non-null location removed')
            continue
        if destination not in kept:return dict(verified=False,reason='missing retained physical location')
        if destination==op:continue
        allowed=domains[destination]|{(0,0)}
        if not domains[op]<=allowed:return dict(verified=False,reason='physical effect coverage')
        if destination not in checked:
            for x in allowed:
                for y in allowed:
                    if (x[0]^y[0],x[1]^y[1]) not in allowed:return dict(verified=False,reason='retained domain not xor closed')
            checked.add(destination)
    reduced=Reduced([row for row in rows if row[0] in kept])
    if reduced.hash!=proof.get('reduced_hash') or reduced.count!=proof.get('reduced_count'):return dict(verified=False,reason='reduced universe binding')
    answer=span_decomposition.verify(reduced,proof['inner'],target,work_limit,state_limit)
    return dict(answer,domain_reduction_verified=True,original_alternatives=inv.count,retained_alternatives=reduced.count)
