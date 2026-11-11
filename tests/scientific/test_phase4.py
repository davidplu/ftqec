import itertools
import json
import pytest
from ftqec.experiments.policies import order,hypervolume,checkpoint_frontier
from ftqec.experiments.verification import boundary_witness,verify_exact
from ftqec.architectures.group_schedule import term_schedule
from ftqec.codes.two_block import parse
from ftqec.circuits.repeated import memory
from ftqec.certification.inventory import fault_at
from ftqec.certification.exact import certify
from ftqec.faults.verification import replay,verify_witness
from ftqec.results.artifacts import digest,source_identity,save
from .test_repeated_memory import small


def item(name,index,q,d):
    return dict(id=name,index=index,resources=dict(Q=q,D=d,QD=q*d,two_q_gates=10))


def test_outcome_blind_policy_order_retains_ties_and_low_qubit_alternatives():
    rows=[item('dominated',0,20,20),item('fast',1,20,5),item('small',2,10,15),item('tie',3,20,5)]
    assert [r['id'] for r in order(rows,'frontier',1)]==['fast','tie','small','dominated']
    assert order(rows,'direct',1)==rows
    assert order(rows,'random',4)==order(rows,'random',4)
    assert sorted(r['id'] for r in order(rows,'random',4))==sorted(r['id'] for r in rows)
    assert len(order(rows,'legacy',4))==2
    with pytest.raises(ValueError):order(rows,'unsupported',4)


def test_hypervolume_against_discrete_union_oracle():
    ref=dict(Q=5,D=5,QD=5,two_q_gates=5)
    points=[dict(id=str(i),resources=dict(zip(ref,p))) for i,p in enumerate([(1,3,2,2),(3,1,2,2),(1,3,2,2),(6,1,1,1)])]
    cells=sum(any(all(r['resources'][k]<=x for k,x in zip(ref,cell)) for r in points) for cell in itertools.product(range(5),repeat=4))
    assert hypervolume(points,ref)==cells/5**4
    assert hypervolume([],ref)==0


def test_checkpoint_excludes_results_finishing_at_or_after_threshold():
    events=[dict(available_cpu=5,frontier=['a']),dict(available_cpu=11,frontier=['b'])]
    assert checkpoint_frontier(events,5)==[]
    assert checkpoint_frontier(events,10)==['a']
    assert checkpoint_frontier(events,11)==['a']
    assert checkpoint_frontier(events,12)==['b']


@pytest.mark.parametrize('basis',['X','Z'])
def test_code_derived_upper_witness_matches_independent_exhaustive_oracle(tmp_path,basis):
    c=memory(term_schedule(parse(small()),serial=True),2,basis)
    faults=[fault_at(c,i,'I') for i,o in enumerate(c.operations) if o.gate=='M' and o.qubits[0]<c.code.n]
    minimum=None
    for weight in range(1,4):
        for subset in itertools.combinations(faults,weight):
            out=replay(c,subset)
            if not out['detector_outcomes'] and out['logical_coset']:minimum=weight;break
        if minimum is not None:break
    witness=boundary_witness(c,3)
    assert witness and witness['weight']==minimum and verify_witness(c,witness)['verified']
    cert=certify(c,minimum,200000,tmp_path,'auto')
    checked=verify_exact(dict(circuit=c.to_dict(),certificate=cert),200000)
    if basis=='X':assert checked['status']=='CERTIFIED' and checked['exact_distance']==minimum
    else:assert checked['status']=='INVALID' and checked['verified']  # A lower-weight circuit fault exists.
    negative=certify(c,minimum+1,200000,tmp_path/'negative','auto')
    checked=verify_exact(dict(circuit=c.to_dict(),certificate=negative),200000)
    assert checked['status']=='INVALID' and checked['verified']


def test_frozen_protocol_rejects_source_or_content_changes(tmp_path):
    from ftqec.experiments.controlled import protocol
    body=dict(source=source_identity(),settings={});body['identity']=digest(body)
    save(tmp_path/'protocol.json',body)
    assert protocol(tmp_path/'protocol.json')==body
    body['settings']['target']=6;save(tmp_path/'protocol.json',body)
    with pytest.raises(ValueError,match='integrity'):protocol(tmp_path/'protocol.json')


def test_progress_accounting_uses_scalar_receipts_without_decoding_payloads(tmp_path):
    from ftqec.experiments.controlled import scalar_tiers
    from ftqec.optimization.store import PopulationStore
    with PopulationStore(tmp_path/'population.sqlite') as db:
        # Invalid payload bytes intentionally ensure the accounting path cannot
        # accidentally decompress a completed multi-megabyte circuit record.
        db.db.execute("INSERT INTO tasks VALUES('a','c','construct_2bga','COMPLETE',X'00','bad',X'00','bad')")
        db.db.execute("INSERT INTO execution VALUES('a',2.5,4.5,100,0,4.5,123)")
        db.db.commit()
        assert scalar_tiers(db)=={'construct_2bga':dict(tasks=1,cpu=2.5,summed_wall=4.5,peak_rss=100)}
