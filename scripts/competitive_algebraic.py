"""Independent CSS distance exclusion used for finite family metadata."""
from itertools import combinations
from ftqec.codes.pauli import Pauli


def css_distance(code,max_weight=5):
    strings=list(map(str,code.generators))
    if any(set(g)-{'I'} not in ({'X'},{'Z'}) for g in strings):raise ValueError('CSS algebraic audit only')
    trials=0;witness=None;distance=None
    for weight in range(1,max_weight+1):
        for support in combinations(range(code.n),weight):
            mask=sum(1<<q for q in support)
            for axis in ('X','Z'):
                trials+=1;p=Pauli(code.n,mask if axis=='X' else 0,mask if axis=='Z' else 0)
                if not code.syndrome(p) and not code.is_stabilizer(p):witness=str(p);distance=weight;break
            if witness:break
        if witness:break
    if witness is None:return dict(status='UNKNOWN',excluded_through=max_weight,examined=trials)
    def in_span(text,axis):
        rows=[[int(a==axis) for a in g] for g in strings if axis in g];v=[int(a==axis) for a in text];pivot=0
        for column in range(code.n):
            chosen=next((j for j in range(pivot,len(rows)) if rows[j][column]),None)
            if chosen is None:continue
            rows[pivot],rows[chosen]=rows[chosen],rows[pivot]
            for j in range(pivot+1,len(rows)):
                if rows[j][column]:rows[j]=[a^b for a,b in zip(rows[j],rows[pivot])]
            if v[column]:v=[a^b for a,b in zip(v,rows[pivot])]
            pivot+=1
        return not any(v)
    for weight in range(1,distance):
        for support in combinations(range(code.n),weight):
            for axis,opposite in [('X','Z'),('Z','X')]:
                text=''.join(axis if q in support else 'I' for q in range(code.n))
                commutes=all(sum(g[q]==opposite for q in support)%2==0 for g in strings)
                if commutes and not in_span(text,axis):raise AssertionError('Independent algebraic lower-bound counterexample')
    axis=next(a for a in witness if a!='I');opposite='Z' if axis=='X' else 'X';support=[q for q,a in enumerate(witness) if a!='I']
    assert all(sum(g[q]==opposite for q in support)%2==0 for g in strings) and not in_span(witness,axis)
    return dict(status='CERTIFIED',n=code.n,k=code.k,distance=distance,witness=witness,examined=trials,independent=True,method='Exhaustive pure CSS supports; independent string commutation and row-span elimination',scope='Algebraic distance only. Any mixed CSS logical has a nontrivial pure component of no greater weight.')
