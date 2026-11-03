"""Exact detector-component composition and separator-frontier elimination.

Each physical location is one finite-domain variable (identity or one complete
Pauli alternative). Detector parity is eliminated only after its last incident
location. Components share no detector or location. A harmful global assignment
must contain a component with zero detector parity and nonzero logical parity;
choosing identity in other components proves the converse for minimum weight.
"""
from collections import Counter
from ..results.artifacts import digest

VERSION='component-separator-suffix-span-dp-2'


def variables(inv):
    grouped={}
    for op,label,d,l,_ in inv.rows():
        grouped.setdefault(op,[]).append((label,d,l))
    return grouped


def bits(mask):
    while mask:
        b=mask&-mask;yield b;mask^=b


def coordinates(groups):
    """Invertible coordinates on the full detector-signature span."""
    vectors=sorted({d for opts in groups.values() for _,d,_ in opts},key=lambda d:(d.bit_count(),d))
    pivots={};basis=[]
    for original in vectors:
        v=original;label=0
        while v:
            bit=v.bit_length()-1
            if bit not in pivots:
                label^=1<<len(basis);basis.append(original);pivots[bit]=(v,label);break
            a,b=pivots[bit];v^=a;label^=b
    def encode(v):
        value=0
        while v:
            a,b=pivots[v.bit_length()-1];v^=a;value^=b
        return value
    return {op:[(label,encode(d),l) for label,d,l in opts] for op,opts in groups.items()},basis


def decompose(groups):
    parents={op:op for op in groups};owner={}
    def find(x):
        while parents[x]!=x:parents[x]=parents[parents[x]];x=parents[x]
        return x
    supports={op:0 for op in groups}
    for op,opts in groups.items():
        for _,d,_ in opts:supports[op]|=d
        for b in bits(supports[op]):
            if b in owner:parents[find(op)]=find(owner[b])
            else:owner[b]=op
    components={}
    for op in groups:components.setdefault(find(op),[]).append(op)
    orders=[]
    for component in sorted(components.values(),key=min):
        remaining=set(component);counts=Counter(b for op in component for b in bits(supports[op]));active=set();order=[]
        while remaining:
            def key(op):
                support=set(bits(supports[op]));closes={b for b in support if counts[b]==1}
                return (len((active|support)-closes),-len(closes),len(support),op)
            op=min(remaining,key=key);remaining.remove(op);order.append(op)
            for b in bits(supports[op]):counts[b]-=1;active.add(b)
            active={b for b in active if counts[b]}
        orders.append(order)
    return orders,supports


def suffix_spaces(groups, order):
    """A relaxation of every legal remaining detector effect, never an exclusion
    based on independence of physical alternatives. A span membership failure
    is sufficient for impossibility; membership is not sufficient for validity.
    """
    spaces=[None]*(len(order)+1);basis={};spaces[-1]={}
    for i in range(len(order)-1,-1,-1):
        basis=basis.copy()
        for _,vector,_ in groups[order[i]]:
            while vector:
                pivot=vector.bit_length()-1
                if pivot not in basis:basis[pivot]=vector;break
                vector^=basis[pivot]
        spaces[i]=basis
    return spaces


def in_space(vector,basis):
    while vector:
        pivot=vector.bit_length()-1
        if pivot not in basis:return False
        vector^=basis[pivot]
    return True


def prove(inv,target,work_limit=200000,state_limit=100000):
    original=variables(inv);transformed,transformed_basis=coordinates(original)
    raw_width=max((d.bit_length() for opts in original.values() for _,d,_ in opts),default=0)
    choices=[]
    for name,groups,basis in [('raw',original,[1<<i for i in range(raw_width)]),('span',transformed,transformed_basis)]:
        components,supports=decompose(groups);width=0
        for order in components:
            last={b:i for i,op in enumerate(order) for b in bits(supports[op])};active=set()
            for i,op in enumerate(order):
                active.update(bits(supports[op]));active={b for b in active if last[b]>i};width=max(width,len(active))
        choices.append((width,name,groups,basis,components,supports))
    _,coordinate_policy,groups,basis,components,supports=min(choices,key=lambda item:(item[0],item[1]))
    work=0;max_states=1;max_width=0;tables=[]
    base=dict(method=VERSION,target=target,inventory_hash=inv.hash,inventory_count=inv.count,components=components,variables_hash=digest(original),detector_basis=basis,coordinate_policy=coordinate_policy,candidate_widths={name:width for width,name,*_ in choices})
    for order in components:
        suffix=suffix_spaces(groups,order)
        last={b:i for i,op in enumerate(order) for b in bits(supports[op])};states={(0,0):(0,())};layers=[];active=set()
        for i,op in enumerate(order):
            closing=sum(b for b in bits(supports[op]) if last[b]==i)
            active.update(bits(supports[op]));active={b for b in active if last[b]>i};max_width=max(max_width,len(active))
            following={}
            # Equal alternatives at a single location have identical continuation
            # states. Keep one representative, but bind the full original universe.
            unique={}
            for label,d,l in groups[op]:unique.setdefault((d,l),label)
            for (d,l),(w,path) in states.items():
                for (dd,ll),label in [((0,0),None)]+list(unique.items()):
                    work+=1
                    if work>work_limit:return dict(base,complete=False,reason='separator_work_limit',work=work,tables=tables,completed_layers=layers,max_states=max_states,width=max_width)
                    weight=w+(label is not None);nd=d^dd;nl=l^ll
                    if weight>=target or nd&closing:continue
                    if not in_space(nd,suffix[i+1]):continue
                    if (nd,nl) not in following or weight<following[nd,nl][0]:following[nd,nl]=(weight,path+(((op,label),) if label is not None else ()))
                    if len(following)>state_limit:return dict(base,complete=False,reason='separator_state_limit',work=work,tables=tables,completed_layers=layers,max_states=len(following),width=max_width)
            states=following;max_states=max(max_states,len(states))
            layers.append(dict(operation=op,states=len(states),sha256=digest(sorted((d,l,w) for (d,l),(w,path) in states.items()))))
        tables.append(layers)
        harmful=[value for (d,l),value in states.items() if d==0 and l]
        if harmful:return dict(base,complete=True,witness=list(min(harmful)[1]),work=work,tables=tables,max_states=max_states,width=max_width)
    return dict(base,complete=True,lower_bound=target,witness=None,work=work,tables=tables,max_states=max_states,width=max_width)


def verify(inv,proof,target,work_limit=200000,state_limit=100000):
    """Separate forward-inventory finite-domain recurrence and partition checks."""
    if proof.get('method')!=VERSION or proof.get('target')!=target or proof.get('inventory_hash')!=inv.hash or proof.get('inventory_count')!=inv.count:
        return dict(verified=False,reason='separator identity')
    groups={}
    for op,label,d,l,_ in inv.rows():groups.setdefault(op,[]).append((label,d,l))
    if digest(groups)!=proof.get('variables_hash'):return dict(verified=False,reason='physical variable universe')
    original=groups
    basis=proof.get('detector_basis',[]);pivots={}
    for i,vector in enumerate(basis):
        if type(vector) is not int or vector<=0:return dict(verified=False,reason='detector basis type')
        value=vector;combination=1<<i
        while value:
            pivot=(value&-value).bit_length()-1
            if pivot not in pivots:pivots[pivot]=(value,combination);break
            row,mask=pivots[pivot];value^=row;combination^=mask
        if not value:return dict(verified=False,reason='dependent detector basis')
    groups={}
    for op,options in original.items():
        groups[op]=[]
        for label,d,l in options:
            value=d;encoded=0
            while value:
                pivot=(value&-value).bit_length()-1
                if pivot not in pivots:return dict(verified=False,reason='detector-span coverage')
                row,mask=pivots[pivot];value^=row;encoded^=mask
            recovered=0
            for i,vector in enumerate(basis):
                if encoded>>i&1:recovered^=vector
            if recovered!=d:return dict(verified=False,reason='detector coordinate reconstruction')
            groups[op].append((label,encoded,l))
    orders=proof.get('components',[]);flat=[op for order in orders for op in order]
    if len(flat)!=len(set(flat)) or set(flat)!=set(groups) or len(orders)!=len(proof.get('tables',[])):
        return dict(verified=False,reason='component coverage')
    seen=set();work=0;peak=1;width=0
    for order,layers in zip(orders,proof['tables']):
        local=set()
        for op in order:
            for _,d,_ in groups[op]:local.update(j for j in range(d.bit_length()) if d>>j&1)
        if seen&local:return dict(verified=False,reason='components share detectors')
        seen|=local
        future=[0]*(len(order)+1)
        for i in range(len(order)-1,-1,-1):
            mask=future[i+1]
            for _,d,_ in groups[order[i]]:mask|=d
            future[i]=mask
        if len(layers)!=len(order):return dict(verified=False,reason='layer coverage')
        spaces=[None]*(len(order)+1);rows={};spaces[-1]={}
        for j in range(len(order)-1,-1,-1):
            rows=dict(rows)
            for _,effect,_ in groups[order[j]]:
                while effect:
                    b=effect&-effect
                    if b not in rows:rows[b]=effect;break
                    effect^=rows[b]
            spaces[j]=rows
        states={(0,0):0};past=0
        for i,op in enumerate(order):
            for _,d,_ in groups[op]:past|=d
            width=max(width,(past&future[i+1]).bit_count())
            next_states={}
            for label,dd,ll in [(None,0,0)]+groups[op]:
                for (d,l),weight in states.items():
                    work+=1
                    if work>work_limit:return dict(verified=False,reason='independent_separator_work_limit',work=work)
                    nd=d^dd;nl=l^ll;w=weight+(label is not None)
                    if w>=target or nd&~future[i+1]:continue
                    residual=nd
                    while residual:
                        b=residual&-residual
                        if b not in spaces[i+1]:break
                        residual^=spaces[i+1][b]
                    if residual:continue
                    next_states[nd,nl]=min(w,next_states.get((nd,nl),target))
                    if len(next_states)>state_limit:return dict(verified=False,reason='independent_separator_state_limit')
            states=next_states;peak=max(peak,len(states))
            expected=dict(operation=op,states=len(states),sha256=digest(sorted((d,l,w) for (d,l),w in states.items())))
            if expected!=layers[i]:return dict(verified=False,reason='separator transition table')
        if any(d==0 and l for d,l in states):return dict(verified=False,reason='harmful component assignment')
    if proof.get('width')!=width or proof.get('max_states')!=peak:return dict(verified=False,reason='width/state accounting')
    return dict(verified=True,lower_bound=target,method='independent forward physical domains, low-pivot suffix-span exclusion and parity recurrence',work=work,max_states=peak)
