"""General multi-fault-guided candidate operators, never positive guarantees."""
import random
from ..results.artifacts import digest,source_identity
from ..faults.verification import replay,verify_witness


def diagnose(c,witness):
    checked=verify_witness(c,witness)
    if not checked['verified']:raise ValueError('Repair diagnosis requires a replayed harmful witness')
    contributions=[]
    for fault in witness['faults']:
        effect=replay(c,[fault]);op=c.operations[fault['operation']]
        initial_data=sum(q<c.code.n and p!='I' for q,p in zip(fault['qubits'],fault['label']))
        final_weight=sum(p!='I' for p in effect['final_data_pauli'])
        contributions.append(dict(fault=fault,effect=effect,check=op.check,role=op.role,
            data_spread=final_weight>initial_data,correlated_alternative=sum(p!='I' for p in fault['label'])>1,
            flag_effect=bool(effect['flag_outcomes']),measurement_fault=fault['kind']=='measurement',
            preparation_context=op.gate in ('RESET','PREP'),verification_context='verify' in (op.record or '') or op.role in ('flag_open','flag_close')))
    flags=[v['effect']['flag_outcomes'] for v in contributions]
    return dict(source=source_identity(),circuit=digest(c.to_dict()),witness=digest(witness),independent=checked,
        contributions=contributions,mechanisms=dict(multi_fault=len(contributions)>1,
        propagated_data=any(v['data_spread'] for v in contributions),
        flag_cancellation=any(flags) and not checked['actual']['flag_outcomes'],
        correlated_gate_fault=any(v['correlated_alternative'] for v in contributions),
        measurement_fault=any(v['measurement_fault'] for v in contributions)),
        qualification='Mechanism evidence from full and single-fault propagation; gate context alone is not a causal proof.')


def propose(inp,parent,witness,seed,target,compact=True):
    d=dict(parent);d['orders']=[list(x) for x in parent['orders']]
    faults=witness.get('faults',[])
    if not faults:raise ValueError('Witness-guided mutation needs physical faults')
    locations=[f['location'] for f in faults if 'location' in f]
    if len(locations)!=len(set(locations)):raise ValueError('Non-exclusive witness')
    affected=sorted({f['check'] for f in faults if type(f.get('check')) is int and 0<=f['check']<len(d['orders'])})
    arm=seed%6
    # A reproducible operator portfolio retains alternatives to adding flags.
    # Full physical replay/certification is mandatory for every descendant.
    d['family']='verified_cat' if arm in (3,4) else 'flagged'
    if arm in (3,4):d['verification_rounds']=max(parent['verification_rounds'],target-1)
    else:d['flag_style']=('adjacent','nested','overlap')[arm%3]
    if arm in (1,4,5):
        rng=random.Random(seed)
        for check in affected:rng.shuffle(d['orders'][check])
    if arm==5:d['rounds']=max(parent['rounds'],2)
    d['reverse_flags']=False;d['schedule']='critical_path';d['interaction_layers']=[]
    d['compact_ancillas']=compact
    return d
