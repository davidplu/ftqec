"""Lossless physical inventory and audited unit-cost mechanism reduction.

The equivalence uses Lemma 2.2 of arXiv:2611.08247, not an assumption of
independent physical faults. Original alternatives and their origins are retained.
"""
from collections import defaultdict
from itertools import product
from .inventory import backward, forward, fault_at
from ..results.artifacts import digest, source_identity
from ..faults.verification import replay

SCHEMA = 'ftqec-physical-mechanisms-1'
PAULI = {'I': 0, 'X': 1, 'Z': 2, 'Y': 3}


def _closure(c, rows):
    by_op = defaultdict(dict)
    for op, label, d, logical, data in rows:
        if label in by_op[op]:
            raise ValueError('Duplicate physical alternative')
        by_op[op][label] = (d, logical, data)
    if set(by_op) != {i for i, op in enumerate(c.operations) if op.gate != 'BARRIER'}:
        raise ValueError('Incomplete physical locations')
    for i, options in by_op.items():
        op = c.operations[i]
        expected = ({'I'} if op.gate == 'M' else
                    {''.join(p) for p in product('IXYZ', repeat=len(op.qubits)) if any(x != 'I' for x in p)})
        if set(options) != expected:
            raise ValueError('Incomplete operation-local alternatives')
        # Measurement is a binary outcome flip, despite its historical I label.
        if op.gate == 'M':
            continue
        full = dict(options)
        full['I'*len(op.qubits)] = (0, 0, 0)
        inverse = {v: k for k, v in PAULI.items()}
        for a, av in full.items():
            for b, bv in full.items():
                label = ''.join(inverse[PAULI[x] ^ PAULI[y]] for x, y in zip(a, b))
                if full[label] != tuple(x ^ y for x, y in zip(av, bv)):
                    raise ValueError('Nonlinear or nonclosed physical fault effects')


def build(c, independent=False):
    from .exact import contract
    c.validate()
    inventory = (forward if independent else backward)(c)
    try:
        rows = list(inventory.rows())
        inventory_hash = inventory.hash
    finally:
        inventory.close()
    _closure(c, rows)
    classes = {}
    columns = []
    for index, (_, _, d, logical, _) in enumerate(rows):
        if (d, logical) == (0, 0):
            continue
        if (d, logical) not in classes:
            classes[d, logical] = len(columns)
            columns.append(dict(detectors=d, logical=logical, alternatives=[]))
        columns[classes[d, logical]]['alternatives'].append(index)
    model, scope = contract(c)
    legacy = c.boundary_model == 'ideal_initial_and_final_syndrome'
    body = dict(schema=SCHEMA, source=source_identity(), circuit=digest(c.to_dict()),
                fault_model=model, scope=scope, boundary=c.boundary_model,
                rounds=c.experiment.get('rounds', 1),
                detectors=len(c.detectors)+(len(c.code.generators) if legacy else 0),
                logicals=len(c.observables)+(2*c.code.k if legacy else 0),
                inventory_hash=inventory_hash, alternatives=[list(r) for r in rows],
                columns=columns, unit_cost=1,
                equivalence='complete unit-cost operation-local Pauli groups and binary readout flips')
    body['identity'] = digest(body)
    return body


def validate(c, ir, independent=True):
    if ir.get('schema') != SCHEMA or ir.get('unit_cost') != 1:
        raise ValueError('Unsupported mechanism representation')
    if ir.get('identity') != digest({k: v for k, v in ir.items() if k != 'identity'}):
        raise ValueError('Mechanism identity mismatch')
    expected = build(c, independent=independent)
    # Replay historical evidence with a newer checker while retaining its
    # recorded producer identity. Physical content must still match exactly.
    expected['source'] = ir['source']
    expected['identity'] = digest({k: v for k, v in expected.items() if k != 'identity'})
    if ir != expected:
        raise ValueError('Physical inventory/circuit/model mismatch')
    return True


def to_upstream(c, ir):
    """Requires the separately pinned upstream package on sys.path."""
    validate(c, ir, independent=True)
    from cdist.problem import Problem
    return Problem(ir['circuit'], ir['detectors'], ir['logicals'],
                   [x['detectors'] for x in ir['columns']],
                   [x['logical'] for x in ir['columns']],
                   [() for _ in range(ir['detectors'])],
                   [x['alternatives'] for x in ir['columns']],
                   {'ftqec_ir': ir['identity'], 'physical_equivalence_checked': True})


def lift_and_replay(c, ir, support):
    if len(set(support)) != len(support) or any(type(j) is not int or not 0 <= j < len(ir['columns']) for j in support):
        raise ValueError('Invalid mechanism support')
    # Any representative may be chosen. Compose collisions at each location;
    # closure checked at construction ensures the result is a legal alternative.
    grouped = defaultdict(list)
    for j in support:
        op, label, *_ = ir['alternatives'][ir['columns'][j]['alternatives'][0]]
        grouped[op].append(label)
    faults = []
    inverse = {v: k for k, v in PAULI.items()}
    for op, labels in sorted(grouped.items()):
        if c.operations[op].gate == 'M':
            if len(labels) % 2:
                faults.append(fault_at(c, op, 'I'))
        else:
            values = [0]*len(c.operations[op].qubits)
            for label in labels:
                for q, char in enumerate(label):
                    values[q] ^= PAULI[char]
            if any(values):
                faults.append(fault_at(c, op, ''.join(inverse[x] for x in values)))
    actual = replay(c, faults)
    d = logical = 0
    for j in support:
        d ^= ir['columns'][j]['detectors']; logical ^= ir['columns'][j]['logical']
    if actual['detector_outcomes'] != d or actual['logical_coset'] != logical:
        raise ValueError('Physical witness effect disagrees with mechanism support')
    return dict(verified=d == 0 and logical != 0, weight=len(faults),
                faults=[f.to_dict() for f in faults], **actual)


def memory_projection(c, sector=False):
    """Explicit row groups, never an automatic claim of round-count equivalence.

    Group syndrome differences by check; retain flag detector channels separately
    after stripping round labels. Any such linear projection is a lower bound.
    """
    if c.boundary_model != 'repeated_noisy_memory':
        raise ValueError('Physical repeated memory required')
    names = {o.record: o for o in c.operations if o.record}
    groups = defaultdict(list)
    for i, row in enumerate(c.detectors):
        checks = {names[r].check for r in row if '_s' in r and names[r].check is not None}
        if len(checks) == 1:
            key = ('check', next(iter(checks)))
            if sector:
                basis = c.experiment.get('memory_basis')
                if basis not in ('X', 'Z'):
                    raise ValueError('Sector projection requires a declared CSS memory basis')
                generator = c.code.to_dict()['generators'][key[1]]
                if set(generator) - {'I', basis}:
                    continue
        else:
            key = ('other', tuple(sorted(r.split(':', 1)[-1] for r in row)))
        groups[key].append(i)
    return list(groups.values())


def project(ir, groups):
    if any(type(i) is not int or not 0 <= i < ir['detectors'] for row in groups for i in row):
        raise ValueError('Projection outside detector space')
    if any(len(set(row)) != len(row) for row in groups):
        raise ValueError('Repeated row in a projection parity')
    masks = [sum(1 << i for i in row) for row in groups]
    columns = []; classes = {}
    for j, col in enumerate(ir['columns']):
        d = sum(((col['detectors'] & mask).bit_count() % 2) << i for i, mask in enumerate(masks))
        key = (d, col['logical'])
        if key == (0, 0):
            continue
        if key not in classes:
            classes[key] = len(columns)
            columns.append(dict(detectors=d, logical=col['logical'], preimages=[]))
        columns[classes[key]]['preimages'].append(j)
    result = dict(schema='ftqec-row-relaxation-1', original=ir['identity'], groups=groups,
                  columns=columns, relation='distance(reduced) <= distance(original)')
    result['identity'] = digest(result)
    return result
