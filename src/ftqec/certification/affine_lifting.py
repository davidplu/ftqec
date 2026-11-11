"""Compact sufficient obstructions to lifting projected minimum supports.

For each support a parity vector is constant within each full preimage
class, and those constants XOR to one. Thus every choice has nonzero full
syndrome. Failure to find such a vector is inconclusive. This relaxation
ignores exclusivity only in the conservative direction (more choices).
"""


def separator(classes):
    basis = {}
    offset = 0
    for values in classes:
        if not values:
            raise ValueError('Empty preimage class')
        offset ^= values[0]
        for value in values:
            row = value ^ values[0]
            while row:
                pivot = row.bit_length() - 1
                if pivot not in basis:
                    basis[pivot] = (row, 0)
                    break
                row ^= basis[pivot][0]
    row, rhs = offset, 1
    while row:
        pivot = row.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = (row, rhs)
            break
        old, bit = basis[pivot]
        row ^= old
        rhs ^= bit
    else:
        if rhs:
            return None
    solution = 0
    for pivot, (row, rhs) in sorted(basis.items()):
        if ((row & solution).bit_count() & 1) ^ rhs:
            solution |= 1 << pivot
    return solution


def prove(original, projected, minima):
    vectors = []
    for support in minima:
        classes = [[original['columns'][i]['detectors']
                    for i in projected['columns'][j]['preimages']] for j in support]
        vector = separator(classes)
        if vector is None:
            return dict(complete=False, separators=vectors)
        vectors.append(vector)
    return dict(complete=True, separators=vectors)


def verify(original, projected, minima, proof):
    """Check dot products only; do not invoke the Gaussian proof producer."""
    try:
        if proof.get('complete') is not True or len(proof['separators']) != len(minima):
            return False
        for support, vector in zip(minima, proof['separators']):
            if type(vector) is not int or vector < 0 or not support:
                return False
            parity = 0
            for j in support:
                labels = {(vector & original['columns'][i]['detectors']).bit_count() & 1
                          for i in projected['columns'][j]['preimages']}
                if len(labels) != 1:
                    return False
                parity ^= next(iter(labels))
            if parity != 1:
                return False
        return True
    except (KeyError, TypeError, IndexError):
        return False
