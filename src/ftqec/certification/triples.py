"""Exact streamed weight-three exclusion; no quadratic pair table is stored.

Requires a separately checked singleton/pair prefix. A minimum harmful set then
has three distinct nonzero effects. Grouping retains every physical location;
producer matching and independent Hall checks enforce location exclusivity.
This is a fixed-weight method, not a polynomial algorithm for arbitrary distance.
"""
from collections import defaultdict
from ..results.artifacts import digest
from .mitm import universe,assignment,Budget,WorkLimit

VERSION='streamed-location-exclusive-triples-1'


def prove(inv,work_limit=200000):
    groups=universe(inv);by_detector=defaultdict(list)
    for k,(d,l,locations) in enumerate(groups):by_detector[d].append((k,l))
    budget=Budget(work_limit);pairs=joins=0;witness=None;complete=False;reason=None
    try:
        for i,(di,li,_) in enumerate(groups):
            for j in range(i+1,len(groups)):
                budget.tick();pairs+=1;dj,lj,_=groups[j]
                for k,lk in by_detector.get(di^dj,()):
                    if k<=j or not li^lj^lk:continue
                    budget.tick();joins+=1
                    witness=assignment((i,j,k),groups,budget)
                    if witness is not None:break
                if witness is not None:break
            if witness is not None:break
        complete=witness is None
    except WorkLimit:reason='streamed_triples_work_limit'
    return dict(method=VERSION,complete=complete,target=4,start_weight=3,lower_bound=4 if complete else 3,
                inventory_hash=inv.hash,inventory_count=inv.count,groups_hash=digest(groups),effects=len(groups),
                pairs_processed=pairs,candidate_joins=joins,work=budget.used,witness=witness,reason=reason)


def verify(inv,proof,bound,work_limit=200000):
    if proof.get('method')!=VERSION or proof.get('target')!=4 or proof.get('start_weight')!=3 or bound!=4 or not proof.get('complete') or proof.get('witness') is not None:
        return dict(verified=False,reason='streamed triple proof declaration')
    # Rebuild all effect domains independently from the forward inventory.
    domains=defaultdict(dict)
    for operation,label,detector,logical,_ in inv.rows():
        if detector==0 and logical==0:continue
        previous=domains[(detector,logical)].get(operation)
        if previous is None or label<previous:domains[(detector,logical)][operation]=label
    ordered=[(d,l,tuple(sorted(locations.items()))) for (d,l),locations in sorted(domains.items())]
    if proof.get('inventory_hash')!=inv.hash or proof.get('inventory_count')!=inv.count or proof.get('groups_hash')!=digest(ordered) or proof.get('effects')!=len(ordered):
        return dict(verified=False,reason='independent effect-domain coverage')
    detector_index=defaultdict(list)
    for index,(d,l,_) in enumerate(ordered):detector_index[d].append(index)
    supports=[frozenset(op for op,label in row[2]) for row in ordered]
    work=pairs=joins=0
    # Reverse orientation: choose the two largest indices and recover the first.
    for k in range(len(ordered)-1,-1,-1):
        dk,lk,_=ordered[k]
        for j in range(k-1,-1,-1):
            work+=1;pairs+=1
            if work>work_limit:return dict(verified=False,reason='independent_triples_work_limit',work=work)
            dj,lj,_=ordered[j]
            for i in detector_index.get(dk^dj,()):
                if i>=j:break
                if ordered[i][1]^lj^lk==0:continue
                work+=1;joins+=1
                if work>work_limit:return dict(verified=False,reason='independent_triples_work_limit',work=work)
                a,b,c=supports[i],supports[j],supports[k]
                # Hall's theorem for exactly three physical location domains.
                if a and b and c and len(a|b)>=2 and len(a|c)>=2 and len(b|c)>=2 and len(a|b|c)>=3:
                    return dict(verified=False,reason='legal harmful triple',effects=[i,j,k])
    if pairs!=proof.get('pairs_processed') or joins!=proof.get('candidate_joins'):
        return dict(verified=False,reason='triple enumeration coverage')
    return dict(verified=True,lower_bound=4,work=work,method='forward inventory, reverse complement scan and three-domain Hall theorem')
