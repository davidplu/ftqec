import itertools
import random
from copy import deepcopy
from types import SimpleNamespace
from ftqec.certification.inventory import Inventory
from ftqec.certification.mitm import prove, verify


def inventory(rows):
    inv=Inventory()
    for op,label,d,l in rows:inv.add(SimpleNamespace(operation=op,label=label),d,l,0)
    inv.finish()
    return inv


def oracle(rows,target):
    for weight in range(1,target):
        for selected in itertools.combinations(rows,weight):
            if len({r[0] for r in selected})!=weight:continue
            d=l=0
            for _,_,dd,ll in selected:d^=dd;l^=ll
            if d==0 and l:return False
    return True


def test_mitm_random_physical_oracle():
    rng=random.Random(51)
    for _ in range(60):
        rows=[(i,str(a),rng.randrange(16),rng.randrange(4)) for i in range(5) for a in range(2)]
        inv=inventory(rows)
        try:
            for target in (2,3,4,5):
                p=prove(inv,target,100000)
                assert p['complete']==oracle(rows,target)
                if p['complete']:assert verify(inv,p,target,100000)['verified']
                else:
                    assert p['witness']
                    assert len({op for op,label in p['witness']})==len(p['witness'])
        finally:inv.close()


def test_location_exclusivity_hyperedges_and_tamper(tmp_path):
    # Two hyperedges cancel detector parity but are alternatives at one location.
    rows=[(0,'XX',7,0),(0,'ZZ',7,1),(1,'Y',12,0)]
    inv=inventory(rows)
    try:
        partial=prove(inv,5,1,tmp_path)
        assert not partial['complete'] and partial['reason']
        p=prove(inv,5,10000,tmp_path)
        assert p['complete'] and verify(inv,p,5,10000)['verified']
        bad=deepcopy(p);bad['partitions'][0]['sha256']='wrong'
        assert not verify(inv,bad,5,10000)['verified']
        bad=deepcopy(p);bad['join_counts']['2']=999
        assert not verify(inv,bad,5,10000)['verified']
    finally:inv.close()
    inv=inventory(rows+[(2,'ZZ',7,1)])
    try:assert prove(inv,3,10000)['witness']
    finally:inv.close()


def test_sat_complete_physical_encoding_and_proof_tree():
    from ftqec.certification.sat import encode,solve,prove as sat_prove,verify as sat_verify
    rng=random.Random(82)
    for _ in range(20):
        rows=[(i,str(a),rng.randrange(8),rng.randrange(2)) for i in range(3) for a in range(2)]
        inv=inventory(rows)
        try:
            for target in (2,3,4):
                p=sat_prove(inv,target,1000000)
                assert p['complete']
                assert (not bool(p.get('witness')))==oracle(rows,target)
                if not p.get('witness'):
                    assert sat_verify(inv,p,target,1000000)['verified']
                    bad=deepcopy(p);bad['tree']={'conflict':True}
                    # Some real formulas unit-refute; when they branch, leaf substitution must fail.
                    if 'variable' in p['tree']:assert not sat_verify(inv,bad,target,1000000)['verified']
                # Fix every physical variable, compare existence of auxiliary completion
                # against independently calculated detector/logical/location semantics.
                if target==3:
                    formula=encode(inv,target)
                    for bits in itertools.product((False,True),repeat=len(rows)):
                        chosen=[r for r,b in zip(rows,bits) if b];d=l=0
                        for _,_,dd,ll in chosen:d^=dd;l^=ll
                        legal=len(chosen)<target and len({r[0] for r in chosen})==len(chosen) and d==0 and l!=0
                        f=deepcopy(formula);f['clauses'] += [[i if b else -i] for i,b in enumerate(bits,1)]
                        outcome=solve(f,1000000)
                        assert outcome['complete'] and (outcome['model'] is not None)==legal
        finally:inv.close()
