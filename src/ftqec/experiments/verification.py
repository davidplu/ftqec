"""Fresh exact-distance verification without supplied successful witnesses."""
from itertools import combinations
from ..circuits.model import Circuit
from ..certification.inventory import fault_at
from ..faults.verification import replay,verify_witness


def boundary_witness(c,target):
    """Bounded meet-in-the-middle witness search on physical data readout flips.

    This is only an upper-bound search. Failure finds no lower bound. All final
    configurations are legal distinct physical locations and independently replayed.
    """
    if not 1<=target<=6:return None
    faults=[fault_at(c,i,'I') for i,o in enumerate(c.operations) if o.gate=='M' and len(o.qubits)==1 and o.qubits[0]<c.code.n]
    if len(faults)>160:return None
    effects=[replay(c,[f]) for f in faults]
    table={0:[(0,(),0)]};entries=1
    for width in range(1,(target+1)//2+1):
        for subset in combinations(range(len(faults)),width):
            d=l=mask=0
            for i in subset:
                d^=effects[i]['detector_outcomes'];l^=effects[i]['logical_coset'];mask|=1<<i
            for other_mask,other,other_l in table.get(d,()):
                if not mask&other_mask and len(other)+width<=target and l!=other_l:
                    selected=[faults[i].to_dict() for i in other+subset]
                    witness=dict(replay(c,selected),faults=selected,weight=len(selected),fault_count=len(selected))
                    if not verify_witness(c,witness)['verified']:raise ValueError('Boundary upper witness failed independent replay')
                    return witness
            table.setdefault(d,[]).append((mask,subset,l))
            entries+=1
            if entries>=100000:return None
    return None


def verify_exact(payload,work):
    from ..certification.exact import verify
    c=Circuit.from_dict(payload['circuit']);original=payload['certificate'];target=original['target']
    if original['status']=='INVALID':
        check=verify(c,original,work)
        return dict(status='INVALID' if check['verified'] else 'UNKNOWN',verified=check['verified'],verification=check,certificate=original)
    cert=dict(original);upper=boundary_witness(c,target)
    if upper is not None:
        if upper['weight']<original['lower_bound']:
            return dict(status='CONTRADICTION',verified=False,witness=upper,certificate=original)
        cert.update(upper_bound=upper['weight'],upper_witness=upper)
        if 'result' in cert:cert['result']=dict(cert['result'],upper_bound=upper['weight'])
        if cert['lower_bound']==upper['weight']:cert['exact_distance']=upper['weight']
    check=verify(c,cert,work)
    exact=check['verified'] and cert.get('exact_distance')==target and cert['lower_bound']>=target
    return dict(status='CERTIFIED' if exact else 'UNKNOWN',verified=exact,lower_bound_verified=check['verified'],verification=check,certificate=cert,exact_distance=target if exact else None)
