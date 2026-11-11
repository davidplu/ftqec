from ftqec.codes.two_block import parse
from ftqec.experiments.adaptive import generate,selected_window
from tests.scientific.test_repeated_memory import small


def test_adaptive_frontier_arm_preserves_legacy_window_decisions():
    pairs=[dict(id=str(i),index=i,resources=dict(Q=12-i%3,D=20+i,QD=(12-i%3)*(20+i),two_q_gates=30),eligible=i!=2) for i in range(10)]
    assert selected_window(pairs,'frontier',15,6)==selected_window(pairs,'legacy',15,6)
    assert len(selected_window(pairs,'direct',15,6))==9
    assert len(selected_window(pairs,'random',15,6))==2
    assert len(selected_window(pairs,'resource',15,6))==2


def test_generation_strategies_preserve_resource_distribution_and_provenance():
    code=parse(small())
    for i in range(20):
        structured=generate(code,i,94004,'structured',[])
        raw=generate(code,i,94004,'random_unfiltered',[])
        assert raw==generate(code,i,94004,'random_unfiltered',[])
        assert raw['parent'] is None and raw['diagnosis'] is None
        for field in ('family','ancilla_slots','check_basis'):
            assert raw['genome'][field]==structured['genome'][field]
        assert sorted(raw['genome']['order'])==sorted(structured['genome']['order'])
        assert raw['raw_order_draws']==1
