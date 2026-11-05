"""Validate supplied left/right regular group-algebra conventions without rebasing."""
from dataclasses import dataclass
from .input import load, CodeInput
from .stabilizer import StabilizerCode
from ..results.artifacts import digest

@dataclass(frozen=True)
class TwoBlock:
    input: CodeInput
    checks: StabilizerCode
    x_terms: tuple
    z_terms: tuple
    receipt: dict


def parse(data):
    inp=load(data)
    if any(inp.signs):raise ValueError('2BGA currently requires positive supplied generators')
    md=data.get('metadata',{}); table=md.get('multiplication_table')
    if not isinstance(table,list) or not table:raise ValueError('2BGA multiplication table required')
    m=len(table); elems=list(range(m))
    if any(not isinstance(row,list) or len(row)!=m or any(type(x) is not int for x in row) or sorted(row)!=elems for row in table):raise ValueError('Group table rows')
    if any(sorted(table[i][j] for i in elems)!=elems for j in elems):raise ValueError('Group table columns')
    identities=[e for e in elems if all(table[e][i]==table[i][e]==i for i in elems)]
    if len(identities)!=1 or any(identities[0] not in row for row in table):raise ValueError('Group identity/inverses')
    if any(table[table[i][j]][k]!=table[i][table[j][k]] for i in elems for j in elems for k in elems):raise ValueError('Group associativity')
    a,b=md.get('a',[]),md.get('b',[])
    if any(not terms or len(set(terms))!=len(terms) or any(type(t) is not int or t not in elems for t in terms) for terms in (a,b)):raise ValueError('Binary group-algebra supports')
    if inp.code.n!=2*m or md.get('group_order',m)!=m:raise ValueError('Group/block dimensions')
    # Column g maps to row a*g (left action) or g*b (right action).
    L=[[[int(table[h][g]==row) for g in elems] for row in elems] for h in a]
    R=[[[int(table[g][h]==row) for g in elems] for row in elems] for h in b]
    xt=tuple(tuple(next(g for g in elems if mat[row][g]) for row in elems) for mat in L)+tuple(tuple(m+next(g for g in elems if mat[row][g]) for row in elems) for mat in R)
    zt=tuple(tuple(next(g for g in elems if mat[g][row]) for row in elems) for mat in R)+tuple(tuple(m+next(g for g in elems if mat[g][row]) for row in elems) for mat in L)
    strings=[]
    for axis,terms in [('X',xt),('Z',zt)]:
        for row in elems:
            support={term[row] for term in terms}
            strings.append(''.join(axis if q in support else 'I' for q in range(2*m)))
    full=StabilizerCode.from_dict(dict(name=inp.code.name,n=2*m,generators=strings))
    if full.rank!=inp.code.rank or any(not inp.code.is_stabilizer(g) for g in full.generators):raise ValueError('Supplied basis does not span reconstructed checks')
    if md.get('k',full.k)!=full.k:raise ValueError('Claimed logical dimension')
    abelian=all(table[i][j]==table[j][i] for i in elems for j in elems)
    if md.get('abelian',abelian)!=abelian:raise ValueError('Abelian claim')
    receipt=dict(code=inp.identity,full_checks=digest(full.to_dict()),n=full.n,k=full.k,rank=full.rank,group_order=m,abelian=abelian,check_count=2*m,weights=[g.weight for g in full.generators],commuting=True,associativity='exhaustive',basis_span_verified=True,claimed_distance=data.get('distance'),distance_status='supplied claim; requires independent distance evidence')
    return TwoBlock(inp,full,xt,zt,receipt)
