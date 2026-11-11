"""Small exact projected problems and complete minimum-weight lifting.

This is a transparent Python proof path inspired by Section 5.4, not a port of
the upstream accelerated kernels. A second, canonical branching evaluator is
used for independent verification of the projected minimum and its full list.
"""
from collections import defaultdict
from itertools import combinations, product


class Incomplete(RuntimeError):
    pass


def enumerate_minima(columns, max_weight=5, work_limit=50000000, on_progress=None):
    if not 1 <= max_weight <= 5:
        raise ValueError('This enumerator supports weights one through five')
    h = [x['detectors'] for x in columns]; l = [x['logical'] for x in columns]
    n = len(h); work = 0
    if n*(n-1)//2 > min(500000, work_limit):
        raise Incomplete('Pair-table safety bound')
    def harmful(support):
        nonlocal work
        work += 1
        if work > work_limit:
            raise Incomplete('Enumeration work limit')
        a = b = 0
        for j in support:
            a ^= h[j]; b ^= l[j]
        return a == 0 and b != 0
    for w in (1, 2):
        if w > max_weight:
            return dict(lower_bound=w, minima=[], work=work)
        solutions = [list(s) for s in combinations(range(n), w) if harmful(s)]
        if solutions:
            return dict(lower_bound=w, minima=solutions, work=work)
        if on_progress:on_progress(w+1)
    pairs = defaultdict(list)
    singles = defaultdict(list)
    for i in range(n):
        singles[h[i]].append(i)
    for a, b in combinations(range(n), 2):
        pairs[h[a] ^ h[b]].append((a, b))
    for w in range(3, max_weight+1):
        found = set()
        if w == 3:
            for syndrome, ps in pairs.items():
                for a, b in ps:
                    for j in singles.get(syndrome, ()):
                        if j > b and harmful((a, b, j)):
                            found.add((a, b, j))
        elif w == 4:
            for ps in pairs.values():
                for x, y in combinations(ps, 2):
                    if len(set(x+y)) == 4 and harmful(x+y):
                        found.add(tuple(sorted(x+y)))
        else:
            for a, b, c in combinations(range(n), 3):
                work += 1
                if work > work_limit:
                    raise Incomplete('Triple-scan work limit')
                for x, y in pairs.get(h[a] ^ h[b] ^ h[c], ()):
                    if x > c and harmful((a, b, c, x, y)):
                        found.add((a, b, c, x, y))
        if found:
            return dict(lower_bound=w, minima=[list(x) for x in sorted(found)], work=work)
        if on_progress:on_progress(w+1)
    return dict(lower_bound=max_weight+1, minima=[], work=work)


def canonical_minima_sets(columns, threshold, work_limit=50000000):
    """Independent Algorithm-2-style checker, without pair/triple tables."""
    incidence = defaultdict(set)
    for j, col in enumerate(columns):
        bits = col['detectors']
        while bits:
            bit = bits & -bits; incidence[bit].add(j); bits ^= bit
    found = set(); nodes = 0
    def visit(chosen, available, syndrome, logical):
        nonlocal nodes
        nodes += 1
        if nodes > work_limit:
            raise Incomplete('Independent branch-check work limit')
        if syndrome == 0:
            if logical:
                found.add(tuple(sorted(chosen)))
            return
        if len(chosen) == threshold:
            return
        bits = syndrome; candidates = None
        while bits:
            bit = bits & -bits; bits ^= bit
            row = incidence[bit] & available
            if not row:
                return
            if candidates is None or len(row) < len(candidates):
                candidates = row
        remaining = set(available)
        for j in sorted(candidates):
            remaining.remove(j)
            col = columns[j]
            visit(chosen+(j,), remaining, syndrome ^ col['detectors'], logical ^ col['logical'])
    for j, col in enumerate(columns):
        visit((j,), set(range(j+1, len(columns))), col['detectors'], col['logical'])
    minimum = min((len(x) for x in found), default=threshold+1)
    return dict(lower_bound=minimum,
                minima=[list(x) for x in sorted(found) if len(x) == minimum], work=nodes)


def canonical_minima(columns, threshold, work_limit=50000000):
    """Same exhaustive partition as the set oracle, using native integer sets."""
    incidence = defaultdict(int)
    for j, col in enumerate(columns):
        bits = col['detectors']
        while bits:
            bit = bits & -bits; incidence[bit] |= 1 << j; bits ^= bit
    found = set(); nodes = 0
    def visit(chosen, available, syndrome, logical):
        nonlocal nodes
        nodes += 1
        if nodes > work_limit:
            raise Incomplete('Independent branch-check work limit')
        if syndrome == 0:
            if logical:found.add(tuple(sorted(chosen)))
            return
        if len(chosen) == threshold:return
        bits = syndrome; candidates = 0; size = len(columns)+1
        while bits:
            bit = bits & -bits; bits ^= bit
            row = incidence[bit] & available
            if not row:return
            count = row.bit_count()
            if count < size:candidates = row; size = count
        remaining = available
        while candidates:
            bit = candidates & -candidates; candidates ^= bit; remaining &= ~bit
            j = bit.bit_length()-1; col = columns[j]
            visit(chosen+(j,), remaining, syndrome ^ col['detectors'], logical ^ col['logical'])
    available = (1 << len(columns))-1
    for j, col in enumerate(columns):
        available &= ~(1 << j)
        visit((j,), available, col['detectors'], col['logical'])
    minimum = min((len(x) for x in found), default=threshold+1)
    return dict(lower_bound=minimum, minima=[list(x) for x in sorted(found) if len(x)==minimum], work=nodes)


def lift_minima(original, projected, minima, reverse=False, work_limit=50000000):
    """Complete preimage enumeration at the established projected minimum only."""
    checked = 0
    for support in minima:
        classes = [projected['columns'][j]['preimages'] for j in support]
        if reverse:
            classes.reverse()
        cut = len(classes)//2
        table = {}
        size = 1
        for cls in classes[:cut]:
            size *= len(cls)
        if size > 500000:
            raise Incomplete('Lift-table memory safety bound')
        for selected in product(*classes[:cut]):
            checked += 1
            if checked > work_limit:
                raise Incomplete('Lifting work limit')
            syndrome = 0
            for j in selected:
                syndrome ^= original['columns'][j]['detectors']
            table[syndrome] = selected
        for selected in product(*classes[cut:]):
            checked += 1
            if checked > work_limit:
                raise Incomplete('Lifting work limit')
            syndrome = 0
            for j in selected:
                syndrome ^= original['columns'][j]['detectors']
            if syndrome in table:
                return dict(witness=list(table[syndrome]+selected), complete=False, work=checked)
    return dict(witness=None, complete=True, work=checked)
