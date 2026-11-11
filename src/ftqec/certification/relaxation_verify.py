"""Replay a row-relaxation evidence directory without the pair/triple producer.

This checker reconstructs the physical inventory by forward propagation and
uses canonical branching for the projected minimum. Lifting exclusion uses
layered reachable-syndrome sets, not the producer's two-sided join.
"""
import json
from pathlib import Path
from . import mechanism_ir as physical
from .relaxation import canonical_minima, Incomplete
from ..results.artifacts import digest


def exclude_lifts(original, projected, minima, work_limit=50000000):
    work = 0
    for support in minima:
        states = {0}
        for j in support:
            following = set()
            for state in states:
                for index in projected['columns'][j]['preimages']:
                    work += 1
                    if work > work_limit:
                        raise Incomplete('Independent lifting work limit')
                    following.add(state ^ original['columns'][index]['detectors'])
                    if len(following) > 500000:
                        raise Incomplete('Independent lifting memory safety bound')
            states = following
        if 0 in states:
            return dict(excluded=False, work=work)
    return dict(excluded=True, work=work)


def verify(c, directory, work=50000000):
    root = Path(directory)
    def read(name):
        return json.loads((root/name).read_text())
    result = read('result.json')
    if result['circuit'] != digest(c.to_dict()) or read('circuit.json') != c.to_dict():
        raise ValueError('Circuit binding mismatch')
    ir = read('inventory.json')
    physical.validate(c, ir, independent=True)
    projection = read('projection.json')
    if projection != physical.project(ir, projection['groups']):
        raise ValueError('Projection binding mismatch')
    answer = read('projected-enumeration.json')
    check = canonical_minima(projection['columns'], min(answer['lower_bound'], 5, result['target']), work)
    if (check['lower_bound'], check['minima']) != (answer['lower_bound'], answer['minima']):
        raise ValueError('Minimum or complete minimizer list mismatch')
    lower = check['lower_bound']; upper = None
    if result.get('upper_bound') is not None:
        lift = read('lifting.json')
        replay = physical.lift_and_replay(c, ir, lift['witness'])
        if not replay['verified'] or replay != read('witness.json'):
            raise ValueError('Physical witness mismatch')
        upper = replay['weight']
    if result['lower_bound'] > lower:
        if not check['minima'] or result['lower_bound'] != lower+1:
            raise ValueError('Unsupported lifting bound')
        if result.get('lifting_method') == 'affine_parity':
            from .affine_lifting import verify as affine_verify
            exclusion = dict(excluded=affine_verify(ir, projection, check['minima'], read('affine-lifting.json')))
        else:
            exclusion = exclude_lifts(ir, projection, check['minima'], work)
        if not exclusion['excluded']:
            raise ValueError('A projected minimizer has a full preimage')
        lower += 1
    if result['lower_bound'] != lower or result.get('upper_bound') != upper:
        raise ValueError('Claimed bounds disagree with replay')
    if result['status'] == 'CERTIFIED' and lower < result['target']:
        raise ValueError('Insufficient target lower bound')
    if result['status'] == 'INVALID' and (upper is None or upper >= result['target']):
        raise ValueError('Missing invalid-target witness')
    return dict(verified=True, circuit=result['circuit'], inventory=ir['identity'],
                projection=projection['identity'], lower_bound=lower, upper_bound=upper,
                evidence=digest(result), checker='forward/canonical/layered-lift')
