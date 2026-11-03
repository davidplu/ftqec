from copy import deepcopy
import random
from tests.scientific.test_general_certification import inventory,oracle
from ftqec.certification.decomposition import prove,verify


def test_separator_matches_exhaustive_correlated_location_oracle():
    rng=random.Random(910)
    for case in range(35):
        rows=[(i,str(a),rng.randrange(16),rng.randrange(4)) for i in range(5) for a in range(3)]
        inv=inventory(rows)
        try:
            for target in (2,3,4,5):
                p=prove(inv,target,100000)
                assert p['complete']
                assert (p.get('witness') is None)==oracle(rows,target)
                if not p.get('witness'):assert verify(inv,p,target,100000)['verified']
        finally:inv.close()


def test_component_coverage_and_locality_tamper():
    inv=inventory([(0,'X',1,0),(1,'X',1,0),(2,'X',2,0),(3,'X',2,0),(4,'X',0,0)])
    try:
        p=prove(inv,5,10000);assert verify(inv,p,5,10000)['verified'];assert len(p['components'])==3
        q=deepcopy(p);q['components'][0].append(q['components'][1][0]);assert not verify(inv,q,5,10000)['verified']
        q=deepcopy(p);q['tables'][0][0]['states']+=1;assert not verify(inv,q,5,10000)['verified']
        q=prove(inv,5,1);assert not q['complete'] and q['reason']=='separator_work_limit'
    finally:inv.close()


def test_coordinate_and_width_tampering_rejected():
    inv=inventory([(0,'A',7,0),(1,'B',12,0),(2,'C',11,0)])
    try:
        p=prove(inv,5,10000);assert verify(inv,p,5,10000)['verified']
        q=deepcopy(p);q['detector_basis'].append(q['detector_basis'][0]);assert not verify(inv,q,5,10000)['verified']
        q=deepcopy(p);q['width']+=1;assert not verify(inv,q,5,10000)['verified']
    finally:inv.close()
