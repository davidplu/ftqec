"""Exact physical-fault CNF with a bounded DPLL proof tree and separate checker.

No external solver status is trusted. UNSAT leaves must unit-refute; branches
cover both values of one variable. This deliberately small backend is primarily
an encoding oracle; large formulas return UNKNOWN under their work allowance.
"""
from .mitm import Budget,WorkLimit
from ..results.artifacts import digest
VERSION='physical-location-cnf-dpll-1'


def encode(inv,target):
    rows=list(inv.rows());clauses=[];n=len(rows);nextvar=n
    def var():
        nonlocal nextvar
        nextvar+=1
        return nextvar
    true=var();clauses.append([true])
    def xor(a,b):
        z=var();clauses.extend([[a,b,-z],[-a,-b,-z],[a,-b,z],[-a,b,z]])
        return z
    def parity(indices):
        acc=-true
        for i in indices:acc=xor(acc,i)
        return acc
    detectors={};logicals={};locations={}
    for i,(op,label,d,l,_) in enumerate(rows,1):
        locations.setdefault(op,[]).append(i)
        for bits,out in ((d,detectors),(l,logicals)):
            while bits:
                bit=bits&-bits;out.setdefault(bit,[]).append(i);bits^=bit
    for indices in detectors.values():clauses.append([-parity(indices)])
    clauses.append([parity(indices) for indices in logicals.values()])
    for indices in locations.values():
        for j,a in enumerate(indices):
            for b in indices[j+1:]:clauses.append([-a,-b])
    # Exact sequential threshold counter C[i,j] = at least j selected among i.
    previous=[true]+[-true]*target
    for x in range(1,n+1):
        current=[true]
        for j in range(1,target+1):
            a=previous[j];b=previous[j-1];z=var()
            # z <=> a OR (x AND b), with signed constant literals allowed.
            clauses.extend([[-a,z],[-x,-b,z],[-z,a,x],[-z,a,b]])
            current.append(z)
        previous=current
    clauses.append([-previous[target]])
    canonical=[sorted(set(c)) for c in clauses if not any(-v in c for v in c)]
    return dict(version=VERSION,variables=nextvar,physical_variables=n,clauses=canonical,
                alternatives=[[op,label] for op,label,*_ in rows],inventory_hash=inv.hash,target=target)


def solve(formula,work_limit):
    budget=Budget(work_limit);clauses=formula['clauses']
    def visit(values):
        values=dict(values)
        while True:
            changed=False;remaining=[]
            for clause in clauses:
                budget.tick()
                if any(values.get(abs(v))==(v>0) for v in clause):continue
                rest=[v for v in clause if abs(v) not in values]
                if not rest:return {'conflict':True},None
                remaining.append(rest)
                if len(rest)==1:
                    v=rest[0];values[abs(v)]=v>0;changed=True
            if not changed:break
        if not remaining:return None,values
        v=abs(min(remaining,key=len)[0])
        lo,model=visit(values|{v:False})
        if model is not None:return None,model
        hi,model=visit(values|{v:True})
        if model is not None:return None,model
        return {'variable':v,'false':lo,'true':hi},None
    try:
        tree,model=visit({})
        return dict(complete=True,tree=tree,model=model,work=budget.used)
    except (WorkLimit,RecursionError):return dict(complete=False,work=budget.used,reason='SAT work or recursion safeguard')


def check_tree(formula,tree,work_limit):
    budget=Budget(work_limit)
    def check(node,decisions):
        # Independent set-clause substitution, retaining the residual formula.
        clauses=[set(c) for c in formula['clauses']]
        assigned=set(decisions)
        while True:
            reduced=[];units=set()
            for clause in clauses:
                budget.tick()
                if clause&assigned:continue
                rest=clause-{-v for v in assigned}
                if not rest:return node=={'conflict':True}
                reduced.append(rest)
                if len(rest)==1:units|=rest
            if any(-u in units or -u in assigned for u in units):return node=={'conflict':True}
            if units<=assigned:break
            assigned|=units;clauses=reduced
        if not isinstance(node,dict) or set(node)!={'variable','false','true'}:return False
        v=node['variable']
        if type(v) is not int or not 1<=v<=formula['variables'] or v in assigned or -v in assigned:return False
        return check(node['false'],assigned|{-v}) and check(node['true'],assigned|{v})
    try:return dict(verified=check(tree,set()),work=budget.used)
    except (WorkLimit,RecursionError):return dict(verified=False,reason='independent SAT checker safeguard',work=budget.used)


def prove(inv,target,work_limit):
    formula=encode(inv,target);result=solve(formula,work_limit)
    model=result.pop('model',None)
    if model is not None:result['witness']=[row for i,row in enumerate(formula['alternatives'],1) if model.get(i,False)]
    return dict(result,method=VERSION,target=target,formula_hash=digest(formula),inventory_hash=inv.hash,inventory_count=inv.count,variables=formula['variables'],clauses=len(formula['clauses']))


def verify(inv,proof,bound,work_limit):
    if proof.get('method')!=VERSION or proof.get('target')!=bound or not proof.get('complete') or proof.get('witness'):return dict(verified=False,reason='SAT proof claim')
    formula=encode(inv,bound)
    if proof.get('formula_hash')!=digest(formula):return dict(verified=False,reason='independent CNF identity')
    return check_tree(formula,proof.get('tree'),work_limit)
