import json
from dataclasses import replace
from pathlib import Path
from ftqec.architectures.population import Genome,compile
from ftqec.architectures.synthesis import generate
from ftqec.architectures.coloring import colored_orders
from ftqec.codes.input import load
from ftqec.screening.structural import check
from ftqec.certification.exact import certify
from ftqec.certification.eligibility import assess,verify
from ftqec.scheduling.analysis import analyze
from ftqec.evaluation.resources import resources


def test_joint_code_only_css_schedule_and_recertification():
    inp=load(json.loads(Path('examples/surface_small.json').read_text()))
    g,receipt=generate(inp,0,2,parallel=True,joint=True);assert g.schedule=='joint_colored'
    c=compile(inp,g);check(c);r=certify(c,2)
    assert r['status']=='CERTIFIED' and r['independent']['verified']
    assert resources(c)['D']<=8
    analysis=analyze(c);assert len(analysis['critical_path'])==resources(c)['D']
    assert Genome.from_dict(g.to_dict())==g
    old,_=generate(inp,0,2,parallel=True,joint=False);assert old.schedule=='colored'


def test_allocation_compaction_preserves_operations_and_recertifies():
    inp=load(json.loads(Path('examples/shor9.json').read_text()))
    orders=tuple(tuple(q for q in range(inp.code.n) if (p.x|p.z)>>q&1) for p in inp.code.generators)
    g=Genome('flagged',orders,tuple(range(len(orders))),shared=False,flag_style='adjacent')
    a=compile(inp,g);b=compile(inp,replace(g,compact_ancillas=True));check(a);check(b)
    assert len(a.operations)==len(b.operations) and b.num_qubits<a.num_qubits
    assert [o.gate for o in a.operations]==[o.gate for o in b.operations]
    result=certify(b,3);before=certify(a,3)
    assert result['status']==before['status'] and result['independent']['verified']
    from ftqec.certification.inventory import backward
    ia=backward(a);ib=backward(b)
    try:assert ia.hash==ib.hash
    finally:ia.close();ib.close()
    receipt=assess(b);assert verify(b,receipt)['verified']


def test_joint_domains_no_reference_and_conflicts():
    inp=load(json.loads(Path('examples/surface_small.json').read_text()))
    choice,receipt=colored_orders(inp,2,8,joint=True);assert choice
    orders,layers=choice;occupied=set()
    for order,ts in zip(orders,layers):
        for pair in zip(order,ts):assert pair not in occupied;occupied.add(pair)
    assert receipt['method']=='code_only_joint_hook_coloring'


def test_independent_hypergraph_product_family():
    from ftqec.codes.families import hamming_hypergraph_product
    from itertools import combinations
    from ftqec.codes.pauli import Pauli
    inp=hamming_hypergraph_product();assert (inp.code.n,inp.code.k)==(58,16)
    for weight in (1,2):
        for support in combinations(range(58),weight):
            mask=sum(1<<q for q in support)
            for p in (Pauli(58,mask,0),Pauli(58,0,mask)):
                assert inp.code.syndrome(p) or inp.code.is_stabilizer(p)


def test_targets_above_ten_are_not_artificially_rejected():
    inp=load(dict(generators=['ZZ']));c=compile(inp,Genome('bare',((0,1),),(0,)));check(c)
    result=certify(c,11)
    assert result['status']=='INVALID' and result['upper_bound']<11
