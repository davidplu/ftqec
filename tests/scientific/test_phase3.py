import random
import itertools
from ftqec.certification.relaxation import canonical_minima,canonical_minima_sets,enumerate_minima
from ftqec.architectures.group_search import crossing_masks,valid_order,pooled
from ftqec.architectures.group_schedule import term_schedule
from ftqec.codes.two_block import parse
from ftqec.circuits.repeated import memory,validate_memory
from .test_repeated_memory import small


def test_affine_lifting_against_exhaustive_oracle_and_tampering():
    from ftqec.certification.affine_lifting import prove,verify
    rng=random.Random(73006)
    checked=0
    for _ in range(500):
        original={'columns':[{'detectors':rng.randrange(256)} for _ in range(12)]}
        projected={'columns':[{'preimages':list(range(i,i+3))} for i in (0,3,6,9)]}
        minima=[[0,1,2,3]];proof=prove(original,projected,minima)
        if proof['complete']:
            checked+=1
            assert verify(original,projected,minima,proof)
            assert not any(original['columns'][a]['detectors']^original['columns'][b]['detectors']^original['columns'][c]['detectors']^original['columns'][d]['detectors']==0
                           for a,b,c,d in itertools.product(range(3),range(3,6),range(6,9),range(9,12)))
            assert not verify(original,projected,minima,dict(complete=True,separators=[0]))
            assert not verify(original,projected,minima,dict(complete=True,separators=[]))
    assert checked>0
    # Affine hull can contain zero even when the actual discrete sum cannot.
    original={'columns':[{'detectors':v} for v in (1,2,3)]}
    projected={'columns':[{'preimages':[0,1,2]}]}
    assert not prove(original,projected,[[0]])['complete']
    assert not verify(original,projected,[[0]],dict(complete=True,separators=[True]))


def test_native_integer_branching_matches_two_independent_oracles():
    rng=random.Random(73003)
    for _ in range(100):
        cols=[dict(detectors=rng.randrange(32),logical=rng.randrange(4)) for _ in range(10)]
        for target in (2,3,4,5):
            a=canonical_minima(cols,target);b=canonical_minima_sets(cols,target);c=enumerate_minima(cols,target)
            assert a==b
            assert (a['lower_bound'],a['minima'])==(c['lower_bound'],c['minima'])


def test_code_derived_order_filter_and_shared_pool():
    code=parse(small());rng=random.Random(73004);masks=crossing_masks(code)
    for _ in range(20):
        order=[('X',i) for i in range(len(code.x_terms))]+[('Z',i) for i in range(len(code.z_terms))];rng.shuffle(order)
        if not valid_order(order,masks):continue
        term_schedule(code,order=order)
        for basis in ('redundant','independent'):
            single=pooled(code,dict(order=order,ancilla_slots=1,check_basis=basis))
            assert single.num_qubits==code.checks.n+1 and single.code.rank==code.checks.rank
            for axis in ('X','Z'):validate_memory(memory(single,2,axis))


def test_auto_portfolio_small_memory_and_legacy_remain_verifiable(tmp_path):
    from ftqec.certification.exact import certify,verify
    c=memory(term_schedule(parse(small()),serial=True),2,'X')
    for method in ('auto','auto_legacy'):
        result=certify(c,3,200000,tmp_path/method,method=method)
        assert result['status']=='INVALID'
        assert verify(c,result,200000)['verified']


def test_disk_memory_campaign_reuses_completed_tasks(tmp_path):
    from ftqec.optimization.phase3 import optimize
    from ftqec.optimization.store import PopulationStore
    from ftqec.delivery.export import export_result
    from ftqec.delivery.verify import verify_bundle
    a=optimize(small(),tmp_path,rounds=2,target=2,candidate_goal=2,window=2,promotions=1,shots=4,decoder='one_mechanism_lookup',work=200000)
    with PopulationStore(tmp_path/'population.sqlite',readonly=True) as db:
        before=list(db.packets());ids=[r['id'] for r in db.summaries(certified=True)]
    b=optimize(small(),tmp_path,rounds=2,target=2,candidate_goal=2,window=2,promotions=1,shots=4,decoder='one_mechanism_lookup',work=200000)
    with PopulationStore(tmp_path/'population.sqlite',readonly=True) as db:assert list(db.packets())==before
    assert a['index']==b['index']==2 and ids
    export_result(tmp_path,ids[0],tmp_path/'bundle')
    import json
    packets=json.loads((tmp_path/'bundle/tasks.json').read_text())
    assert {p['request']['tier'] for p in packets}=={'screen','simulation','certify'}
    assert verify_bundle(tmp_path/'bundle',200000)['positive_certificate_verified']


def test_unproved_frontier_retains_ties_and_low_qubit_alternatives():
    from ftqec.optimization.phase3 import unproved_resource_frontier
    rows={}
    for name,q,d,status in [('fast',12,10,None),('tie',12,10,None),('small',8,20,None),('dominated',12,20,None),('invalid',7,1,'INVALID')]:
        for basis in ('X','Z'):
            cid=name+basis
            rows[cid]=dict(id=cid,pair=name,resources=dict(Q=q,D=d,QD=q*d,two_q_gates=10),circuit=dict(experiment=dict(memory_basis=basis)),screen=dict(status='SCREENED'))
            if status:rows[cid]['certify']=dict(status=status)
    class Store:
        def summaries(self):
            return [dict(id=k,screen=r['screen'],certify=dict(status=r.get('certify',{}).get('status'))) for k,r in rows.items()]
        def get(self,key):return rows[key]
    assert {tuple(pair) for pair in unproved_resource_frontier(Store())}=={('fastX','fastZ'),('tieX','tieZ'),('smallX','smallZ')}


def test_finalist_sweep_recovers_after_memory_admission_stop(tmp_path,monkeypatch):
    import ftqec.optimization.phase3 as engine
    from ftqec.optimization.store import PopulationStore
    real_batch=engine.batch;proof_calls=0
    def interrupted(tasks,*args,**kwargs):
        nonlocal proof_calls
        if tasks and tasks[0].tier=='certify':
            proof_calls+=1
            if proof_calls==2:raise MemoryError('Injected admission interruption at final sweep')
        return real_batch(tasks,*args,**kwargs)
    def remaining(db):
        pairs={}
        for s in db.summaries():
            row=db.get(s['id'])
            if 'certify' not in row:pairs.setdefault(row['pair'],[]).append(row['id'])
        return [ids for ids in pairs.values() if len(ids)==2]
    monkeypatch.setattr(engine,'unproved_resource_frontier',remaining)
    monkeypatch.setattr(engine,'batch',interrupted)
    settings=dict(rounds=2,target=2,candidate_goal=2,window=2,promotions=1,shots=4,decoder='one_mechanism_lookup',work=200000)
    stopped=engine.optimize(small(),tmp_path,**settings)
    assert stopped['status']=='RESOURCE_SAFETY_INTERVENTION' and stopped['index']==2 and stopped['finalist_sweep_pending']
    with PopulationStore(tmp_path/'population.sqlite',readonly=True) as db:
        completed={p['answer']['task'] for p in db.packets()}
    monkeypatch.setattr(engine,'batch',real_batch)
    finished=engine.optimize(small(),tmp_path,**settings)
    assert finished['status']=='REQUESTED_CANDIDATES_COMPLETED' and finished['finalist_sweep_complete_at']==2
    assert 'finalist_sweep_pending' not in finished
    with PopulationStore(tmp_path/'population.sqlite',readonly=True) as db:
        assert completed <= {p['answer']['task'] for p in db.packets()}
