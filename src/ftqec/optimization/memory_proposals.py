"""Code-only memory proposals and transparent certification promotion."""
import random
from ..results.artifacts import digest

FAMILIES=('group_term','bare','flagged','cat','verified_cat')
BUDGETS=(192,168,144,120,96,72,48)


def propose(code,parents,seed,generation,population,target,strategy):
    if strategy not in ('random','structured','witness','multifidelity','hybrid','costaware','costhybrid'):raise ValueError('Memory search strategy')
    rng=random.Random(seed+generation*1000003);proposals=[];m=code.checks.n;nchecks=len(code.checks.generators)
    for i in range(population):
        order=[['X',j] for j in range(len(code.x_terms))]+[['Z',j] for j in range(len(code.z_terms))]
        family=rng.choice(FAMILIES) if strategy=='random' else FAMILIES[i%len(FAMILIES)]
        xs=order[:len(code.x_terms)];zs=order[len(code.x_terms):];rng.shuffle(xs);rng.shuffle(zs)
        order=xs+zs if rng.randrange(2) else zs+xs
        if strategy=='random' and rng.randrange(4)==0:rng.shuffle(order)
        flag_style=rng.choice(('single','adjacent','nested','overlap')) if strategy=='random' else 'adjacent'
        width=max(p.weight for p in code.checks.generators)
        per=width+1 if family=='verified_cat' else width if family=='cat' else 1+(max(1,width-1) if flag_style!='single' else 1) if family=='flagged' else 1
        budget=rng.choice(BUDGETS) if strategy=='random' else BUDGETS[(i//len(FAMILIES)+generation+seed)%len(BUDGETS)]
        slots=max(1,min(nchecks,(budget-m)//per))
        genome=dict(family=family,order=order,flag_style=flag_style,verification_rounds=max(1,(target-1)//2),schedule=rng.choice(('critical_path','conflict_color','resource')),ancilla_slots=slots)
        parent=None;mutation='code_derived_budget_allocation';diagnosis=None
        if parents and strategy not in ('random','structured') and (strategy=='witness' or i%2):
            candidates=[r for r in parents if r.get('certify',{}).get('witness') or r.get('screen',{}).get('witness')]
            chosen=rng.choice(candidates or parents);parent=chosen['id'];genome=dict(chosen['genome']);genome['order']=[x[:] for x in chosen['genome']['order']]
            witness=chosen.get('certify',{}).get('witness') or chosen.get('screen',{}).get('witness')
            if witness:
                diagnosis=dict(witness_hash=digest(witness),faults=len(witness['faults']),roles=sorted({f.get('role','unknown') or 'unknown' for f in witness['faults']}))
                genome['family']=rng.choice(('flagged','verified_cat'));genome['flag_style']='adjacent';mutation='verified_witness_protection_change'
            else:mutation='resource_allocation_mutation'
            genome['ancilla_slots']=rng.choice(tuple(sorted({1,max(1,nchecks//4),max(1,nchecks//2),nchecks})))
            a=rng.randrange(len(order));b=rng.choice([j for j,x in enumerate(genome['order']) if x[0]==genome['order'][a][0]])
            genome['order'][a],genome['order'][b]=genome['order'][b],genome['order'][a]
        proposals.append(dict(key=digest(genome),genome=genome,parent=parent,mutation=mutation,diagnosis=diagnosis,requested_qubit_budget=budget))
    return proposals


def promote(groups,count,strategy,seed,costs=None):
    rows=list(groups.values())
    if strategy=='random':random.Random(seed).shuffle(rows);return rows[:count]
    cost=lambda rs:(max(r['resources']['QD'] for r in rs),max(r['resources']['D'] for r in rs))
    costs=costs or {}
    def expected(rs):
        observed=costs.get(rs[0]['genome']['family'],{}).get('certify',[])
        return sum(x['cpu'] for x in observed)/len(observed) if observed else float('inf')
    if strategy=='witness':ranked=sorted(rows,key=lambda rs:(not any(r.get('parent') for r in rs),cost(rs)))
    elif strategy=='multifidelity':ranked=sorted(rows,key=lambda rs:(max(r.get('simulation',{}).get('confidence',[0,1])[1] for r in rs),cost(rs)))
    elif strategy=='costaware':ranked=sorted(rows,key=lambda rs:(expected(rs),cost(rs)))
    else:ranked=sorted(rows,key=cost)
    chosen=ranked[:min(2,count)]
    if strategy=='costhybrid':
        for rs in sorted(rows,key=lambda rs:(expected(rs),cost(rs)))[:2]:
            if rs not in chosen and len(chosen)<count:chosen.append(rs)
    for family in FAMILIES:
        options=[rs for rs in ranked if rs[0]['genome']['family']==family]
        if options:
            low=min(options,key=lambda rs:(max(r['resources']['Q'] for r in rs),cost(rs)))
            if low not in chosen and len(chosen)<count:chosen.append(low)
    for rs in ranked:
        if len(chosen)>=count:break
        if rs not in chosen:chosen.append(rs)
    return chosen
