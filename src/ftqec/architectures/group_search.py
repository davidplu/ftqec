"""Code-derived commutation constraints and ancilla-pool extraction.

No reference schedules are imported. The algebraic filter is only a proposal
accelerator: every compiled circuit must still pass signed instrument flows.
"""
from ..circuits.model import Circuit
from ..codes.stabilizer import StabilizerCode
from ..screening.structural import check


def crossing_masks(code):
    masks = {}
    for a, xs in enumerate(code.x_terms):
        for b, zs in enumerate(code.z_terms):
            lookup = {q:j for j,q in enumerate(zs)}; mask = 0
            for i,q in enumerate(xs):
                if q in lookup:mask ^= 1 << (i*len(zs)+lookup[q])
            masks[a,b] = mask
    return masks


def valid_order(order, masks):
    positions = {tuple(term):i for i,term in enumerate(order)}; crossed = 0
    for (a,b), mask in masks.items():
        if positions['X',a] < positions['Z',b]:crossed ^= mask
    return crossed == 0


def independent_subset(code, order):
    basis = {}; selected = []
    for i in order:
        value = code.generators[i].packed
        while value:
            pivot = value.bit_length()-1
            if pivot not in basis:
                basis[pivot] = value; selected.append(i); break
            value ^= basis[pivot]
    return selected


def pooled(code, genome):
    n = code.checks.n; m = n//2
    selected = list(genome.get('checks', range(len(code.checks.generators))))
    if sorted(selected) != list(range(len(code.checks.generators))):
        raise ValueError('Check order must cover the full input check list')
    if genome.get('check_basis') == 'independent':
        selected = independent_subset(code.checks, selected)
    measured = StabilizerCode(n, tuple(code.checks.generators[i] for i in selected), code.checks.name)
    if measured.rank != code.checks.rank:raise ValueError('Changed stabilizer space')
    slots = min(genome['ancilla_slots'], len(selected))
    if type(slots) is not int or slots < 1:raise ValueError('Positive ancilla pool required')
    c = Circuit(measured, tuple(range(n,n+slots)), ())
    c.experiment = dict(rounds=1,family='group_pool',reference_seed=False,
        reference_code=code.input.code.to_dict(),reference_signs=list(code.input.signs),
        generator_signs=[0]*len(selected),selected_checks=selected,
        term_order=genome['order'],ancilla_slots=slots,check_basis=genome.get('check_basis','redundant'))
    expected = [('X',i) for i in range(len(code.x_terms))]+[('Z',i) for i in range(len(code.z_terms))]
    if sorted(map(tuple,genome['order'])) != sorted(expected):raise ValueError('Term order coverage')
    for start in range(0,len(selected),slots):
        batch = list(enumerate(selected[start:start+slots],start))
        for offset,(ch,original) in enumerate(batch):
            anc=n+offset;c.add('RESET',[anc],check=ch,round_index=0)
            if original<m:c.add('H',[anc],check=ch,round_index=0)
        for axis,index in genome['order']:
            terms=code.x_terms if axis=='X' else code.z_terms
            for offset,(ch,original) in enumerate(batch):
                if (original<m) != (axis=='X'):continue
                anc=n+offset;data=terms[index][original % m]
                c.add('CX',[anc,data] if axis=='X' else [data,anc],check=ch,round_index=0,role='data_interaction',interaction_position=index)
        for offset,(ch,original) in enumerate(batch):
            anc=n+offset
            if original<m:c.add('H',[anc],check=ch,round_index=0)
            rec=f'r0_s{ch}';c.add('M',[anc],record=rec,check=ch,round_index=0,role='syndrome_readout');c.detectors.append([rec])
        c.add('BARRIER',range(c.num_qubits),round_index=0,role='ancilla_batch_end')
    check(c)
    return c
