import itertools
import random
from copy import deepcopy
from types import SimpleNamespace
from ftqec.certification.inventory import Inventory
from ftqec.certification import decomposition,span_decomposition


def inventory(rows):
    inv=Inventory()
    for op,label,d,l in rows:inv.add(SimpleNamespace(operation=op,label=label),d,l,0)
    inv.finish();return inv


def brute(rows,target):
    domains={}
    for row in rows:domains.setdefault(row[0],[]).append(row)
    for choice in itertools.product(*[[None]+v for v in domains.values()]):
        selected=[r for r in choice if r is not None]
        if len(selected)>=target:continue
        d=l=0
        for _,_,dd,ll in selected:d^=dd;l^=ll
        if not d and l:return False
    return True


def test_suffix_span_matches_full_physical_oracle():
    rng=random.Random(716)
    for case in range(40):
        rows=[(i,str(a),rng.randrange(32),rng.randrange(4)) for i in range(5) for a in range(3)]
        inv=inventory(rows)
        try:
            for target in (2,3,4,5):
                p=span_decomposition.prove(inv,target,1000000)
                assert p['complete']
                assert (not bool(p.get('witness')))==brute(rows,target)
                if not p.get('witness'):
                    assert span_decomposition.verify(inv,p,target,1000000)['verified']
                    altered=deepcopy(p);altered['tables'][0][0]['sha256']='tampered'
                    assert not span_decomposition.verify(inv,altered,target,1000000)['verified']
                else:assert len({op for op,label in p['witness']})==len(p['witness'])
        finally:inv.close()


def test_suffix_span_retains_exclusivity_and_unknown():
    inv=inventory([(0,'XX',7,0),(0,'ZZ',7,1),(1,'Y',12,0)])
    try:
        p=span_decomposition.prove(inv,5,10000)
        assert p['complete'] and not p['witness']
        assert span_decomposition.verify(inv,p,5,10000)['verified']
        assert not span_decomposition.prove(inv,5,1)['complete']
        old=decomposition.prove(inv,5,10000)
        assert decomposition.verify(inv,old,5,10000)['verified']
    finally:inv.close()


def test_round_prefixed_flags_independently_agree():
    from ftqec.codes.families import shor_product
    from ftqec.architectures.population import sample,compile
    from dataclasses import replace
    from ftqec.faults.signatures import signatures,signatures_forward
    from ftqec.faults.verification import replay
    inp=shor_product(2);g=replace(sample(inp,0),family='flagged',rounds=2,flag_style='overlap')
    c=compile(inp,g);fast=signatures(c);slow=signatures_forward(c)
    assert any(s.flags for s in fast)
    assert [(s.detectors,s.flags,s.logical) for s in fast]==[(s.detectors,s.flags,s.logical) for s in slow]
    for sig in fast:
        if sig.flags:
            assert replay(c,[sig.fault])['flag_outcomes']==sig.flags
            break


def test_composed_repairs_preserve_noiseless_semantics():
    from ftqec.codes.families import shor_product
    from ftqec.architectures.population import sample,mutate,compile,Genome
    from ftqec.screening.structural import check
    inp=shor_product(2);parent=sample(inp,0)
    witness={'faults':[{'location':'op:0','check':0,'role':'flag_open','label':'XI'},
                       {'location':'op:1','check':0,'role':'flag_close','label':'XI'}]}
    children=[mutate(inp,parent,i,witness,target=5) for i in range(6)]
    assert {g.family for g in children}=={'flagged','verified_cat'}
    assert any(g.flag_style=='overlap' for g in children)
    for child in children:
        assert Genome.from_dict(child.to_dict())==child
        check(compile(inp,child))


def test_closed_domain_reduction_oracle_and_tamper():
    from ftqec.certification import quotient_decomposition as q
    rng=random.Random(835)
    for case in range(35):
        # Include both closed Pauli-like domains and arbitrary nonclosed domains.
        generators=[(rng.randrange(16),rng.randrange(4)) for _ in range(2)]
        effects=generators+[(generators[0][0]^generators[1][0],generators[0][1]^generators[1][1])]
        rows=[(i,str(a),d,l) for i in range(4) for a,(d,l) in enumerate(effects if i<3 else [(rng.randrange(16),rng.randrange(4)) for _ in range(2)])]
        inv=inventory(rows)
        try:
            for target in (2,3,4,5):
                proof=q.prove(inv,target,1000000)
                assert proof['complete']
                assert (not bool(proof.get('witness')))==brute(rows,target)
                if not proof.get('witness'):
                    assert q.verify(inv,proof,target,1000000)['verified']
                    bad=deepcopy(proof);bad['mapping'][0][1]=None
                    if any(d or l for op,label,d,l in rows if op==bad['mapping'][0][0]):
                        assert not q.verify(inv,bad,target,1000000)['verified']
        finally:inv.close()


def test_nonclosed_location_cannot_absorb_another():
    from ftqec.certification import quotient_decomposition as q
    # Absorbing two domains without closure would erase a legal weight-two logical.
    rows=[(0,'a',1,0),(0,'b',1,1),(1,'a',1,0),(1,'b',1,1)]
    inv=inventory(rows)
    try:
        reduced,mapping=q.compress(inv)
        assert reduced.count==inv.count
        proof=q.prove(inv,3,10000)
        assert proof['witness'] and len(proof['witness'])==2
    finally:inv.close()
