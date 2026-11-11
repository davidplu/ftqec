"""Outcome-blind promotion rules and exact finite-frontier metrics."""
import random
from ..optimization.store import skyline

KEYS=('Q','D','QD','two_q_gates')
POLICIES=('direct','random','resource','legacy','frontier')


def aggregate(rows):
    return {key:max(row['resources'][key] for row in rows) for key in KEYS}


def order(pairs,policy,seed,n=72,window=10,promotions=2):
    """Pair records contain resources/index only, never certification outcomes.

    Fixed-pool frontier policy evaluates the frontier sweep first because the
    entire screened pool is available. Adaptive legacy-plus-sweep is separate.
    """
    if policy not in POLICIES:raise ValueError('Unknown promotion policy')
    rows=sorted(pairs,key=lambda r:(r['index'],r['id']))
    if policy=='direct':return rows
    if policy=='random':
        random.Random(seed).shuffle(rows);return rows
    if policy=='resource':
        scale=(144,76,10944,2592)
        return sorted(rows,key=lambda r:(sum(r['resources'][k]/v for k,v in zip(KEYS,scale))/4,r['index'],r['id']))
    if policy=='legacy':
        chosen=[]
        for generation in sorted({r['index']//window for r in rows}):
            budget=n+max(1,round(n*(1-generation%6/6)))
            group=[r for r in rows if r['index']//window==generation]
            chosen.extend(sorted(group,key=lambda r:(abs(r['resources']['Q']-budget),r['resources']['QD'],r['index'],r['id']))[:promotions])
        return chosen
    frontier={r['id'] for r in skyline(rows)}
    # Sweep all resource ties; then deterministic direct fallback. Neither
    # stage discards UNKNOWN candidates or adopts uncertified resource points.
    return sorted(rows,key=lambda r:(r['id'] not in frontier,r['resources']['QD'] if r['id'] in frontier else r['index'],r['index'],r['id']))


def hypervolume(rows,reference):
    """Exact union of dominated boxes, normalized to the frozen reference box."""
    points={tuple(r['resources'][k] for k in KEYS) for r in rows}
    ref=tuple(reference[k] for k in KEYS)
    if any(x<=0 for x in ref):raise ValueError('Positive reference coordinates required')
    if any(any(v<0 for v in p) for p in points):raise ValueError('Negative resource')
    points=[p for p in points if all(a<b for a,b in zip(p,ref))]
    def volume(ps,rs):
        if not ps:return 0
        if len(rs)==1:return rs[0]-min(p[0] for p in ps)
        boundaries=sorted({p[0] for p in ps}|{rs[0]})
        return sum((b-a)*volume([p[1:] for p in ps if p[0]<=a],rs[1:]) for a,b in zip(boundaries,boundaries[1:]))
    denominator=1
    for x in ref:denominator*=x
    return volume(points,ref)/denominator


def checkpoint_frontier(events,threshold):
    """Strictly completed before threshold; in-flight outcomes are excluded."""
    available=[]
    for event in events:
        if event['available_cpu']<threshold:available=event['frontier']
    return available
