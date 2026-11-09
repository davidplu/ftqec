import random
from copy import deepcopy
from itertools import combinations
import pytest
from ftqec.certification.mechanism_ir import build, validate, project, memory_projection, lift_and_replay
from ftqec.certification.relaxation import enumerate_minima, canonical_minima, Incomplete
from ftqec.circuits.repeated import memory
from ftqec.architectures.group_schedule import term_schedule
from ftqec.codes.two_block import parse
from .test_repeated_memory import small


def test_projected_algorithms_against_exhaustive_oracle():
    rng = random.Random(61108247)
    for _ in range(80):
        columns = [dict(detectors=rng.randrange(16), logical=rng.randrange(4)) for j in range(8)]
        expected = []
        lower = 6
        for w in range(1, 6):
            for support in combinations(range(8), w):
                d = logical = 0
                for j in support:
                    d ^= columns[j]['detectors']; logical ^= columns[j]['logical']
                if d == 0 and logical:
                    expected.append(list(support))
            if expected:
                lower = w
                break
        for actual in (enumerate_minima(columns), canonical_minima(columns, 5)):
            assert actual['lower_bound'] == lower
            assert actual['minima'] == expected


@pytest.mark.parametrize('basis', ['X', 'Z'])
def test_physical_inventory_binding_and_lifting(basis):
    c = memory(term_schedule(parse(small()), serial=True), 2, basis, idles=True)
    ir = build(c)
    assert validate(c, ir)
    bad = deepcopy(ir); bad['alternatives'].pop()
    with pytest.raises(ValueError):
        validate(c, bad)
    reduced = project(ir, memory_projection(c))
    assert reduced['original'] == ir['identity']
    answer = enumerate_minima(ir['columns'], 2)
    for support in answer['minima']:
        witness = lift_and_replay(c, ir, support)
        assert witness['verified'] and witness['weight'] <= len(support)
    with pytest.raises(ValueError):
        project(ir, [[0, 0]])


def test_censored_enumeration_is_not_a_lower_bound():
    columns = [dict(detectors=i, logical=i % 2) for i in range(12)]
    with pytest.raises(Incomplete):
        enumerate_minima(columns, work_limit=1)
    with pytest.raises(Incomplete):
        canonical_minima(columns, 5, work_limit=1)


def test_lifting_exclusion_against_cartesian_oracle():
    from itertools import product
    from ftqec.certification.relaxation import lift_minima
    from ftqec.certification.relaxation_verify import exclude_lifts
    rng = random.Random(61108248)
    for _ in range(100):
        original = {'columns': [dict(detectors=rng.randrange(32), logical=1) for _ in range(9)]}
        projected = {'columns': [dict(preimages=list(range(i, i+3))) for i in (0, 3, 6)]}
        exists = any(original['columns'][a]['detectors'] ^ original['columns'][b]['detectors'] ^ original['columns'][c]['detectors'] == 0
                     for a, b, c in product(range(3), range(3, 6), range(6, 9)))
        assert (lift_minima(original, projected, [[0, 1, 2]])['witness'] is not None) == exists
        assert exclude_lifts(original, projected, [[0, 1, 2]])['excluded'] == (not exists)


def test_standalone_evidence_replay_and_tampering(tmp_path):
    from ftqec.architectures.references import rotated_surface
    from ftqec.certification.relaxation_backend import run
    from ftqec.certification.relaxation_verify import verify
    from ftqec.results.artifacts import save
    _, c = rotated_surface(3, 3)
    result = run(c, 3, tmp_path)
    assert result['status'] == 'CERTIFIED'
    assert verify(c, tmp_path)['lower_bound'] == 3
    result['lower_bound'] = 4
    save(tmp_path/'result.json', result)
    with pytest.raises(ValueError):
        verify(c, tmp_path)


def test_public_portfolio_recipe_reconstructs_without_producer_files(tmp_path):
    from ftqec.architectures.references import rotated_surface
    from ftqec.certification.exact import certify, verify
    _, c = rotated_surface(3, 3)
    cert = certify(c, 3, 20000000, tmp_path, method='time_collapse')
    assert cert['status'] == 'CERTIFIED' and verify(c, cert, 20000000)['verified']
    # Recipe verification rebuilds its own inventory, without reading the path.
    cert['proof']['inventory_count'] += 1
    assert not verify(c, cert, 20000000)['verified']


def test_missing_correlated_alternative_is_rejected():
    from ftqec.certification.mechanism_ir import _closure
    c = memory(term_schedule(parse(small()), serial=True), 2, 'X', idles=True)
    ir = build(c)
    rows = ir['alternatives']
    removed = next(i for i, row in enumerate(rows) if len(row[1]) == 2 and 'I' not in row[1])
    with pytest.raises(ValueError, match='Incomplete operation-local alternatives'):
        _closure(c, rows[:removed]+rows[removed+1:])


def test_negative_witness_does_not_require_an_unclaimed_lower_bound(tmp_path):
    from ftqec.architectures.references import rotated_surface
    from ftqec.certification.relaxation_portfolio import certify, verify
    _, c = rotated_surface(3, 3)
    cert = certify(c, 5, 20000000, tmp_path)
    assert cert['status'] == 'INVALID'
    cert['lower_bound'] = 1
    cert.pop('exact_distance', None)
    assert verify(c, cert, work=1)['verified']
