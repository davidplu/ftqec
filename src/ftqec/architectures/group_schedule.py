"""Code-derived term schedules: no successful circuit is used as a seed."""
import random
from ..circuits.model import Circuit
from ..screening.structural import check


def architecture(code,genome,seed=0):
    """Use the existing generic gadget/scheduling vocabulary on full CSS checks."""
    family=genome.get('family','group_term')
    if family=='group_term':return term_schedule(code,seed,order=genome['order'])
    from .population import Genome,compile
    from ..codes.input import CodeInput
    m=code.checks.n//2
    order=genome['order']
    expected=[('X',i) for i in range(len(code.x_terms))]+[('Z',i) for i in range(len(code.z_terms))]
    if sorted(map(tuple,order))!=sorted(expected):raise ValueError('Term order coverage')
    orders=tuple(tuple((code.x_terms if axis=='X' else code.z_terms)[j][i] for a,j in order if a==axis) for axis in ('X','Z') for i in range(m))
    inp=CodeInput(code.checks,(0,)*(2*m),code.input.metadata)
    g=Genome(family,orders,tuple(range(2*m)),rounds=1,shared=False,
             flag_style=genome.get('flag_style','single'),verification_rounds=genome.get('verification_rounds',1),
             schedule=genome.get('schedule','critical_path'),ancilla_slots=genome.get('ancilla_slots',2*m),native_css=True)
    c=compile(inp,g)
    c.experiment.update(reference_code=code.input.code.to_dict(),reference_signs=list(code.input.signs),reference_seed=False,term_order=order)
    check(c)
    return c


def term_schedule(code,seed=0,serial=False,order=None):
    m=code.checks.n//2;nx=len(code.x_terms);nz=len(code.z_terms)
    rng=random.Random(seed);xs=list(range(nx));zs=list(range(nz));rng.shuffle(xs);rng.shuffle(zs)
    c=Circuit(code.checks,tuple(range(2*m,4*m)),())
    c.experiment=dict(rounds=1,family='group_term',generator_signs=[0]*(2*m),reference_code=code.input.code.to_dict(),reference_signs=list(code.input.signs),term_seed=seed,term_order_x=xs,term_order_z=zs,reference_seed=False)
    for i in range(2*m):c.add('RESET',[2*m+i],check=i,round_index=0)
    for i in range(m):c.add('H',[2*m+i],check=i,round_index=0)
    def layer(axis,index):
        terms=code.x_terms if axis=='X' else code.z_terms
        for i in range(m):
            ch=i if axis=='X' else m+i;anc=2*m+ch;data=terms[index][i]
            c.add('CX',[anc,data] if axis=='X' else [data,anc],check=ch,round_index=0,role='data_interaction',interaction_position=index)
    if order is None:
        order=[('X',i) for i in xs]+[('Z',i) for i in zs]
        if not serial:rng.shuffle(order)
    if sorted(map(tuple,order))!=sorted([('X',i) for i in range(nx)]+[('Z',i) for i in range(nz)]):raise ValueError('Term order coverage')
    c.experiment['term_order']=[list(x) for x in order]
    c.experiment['term_order_x']=[i for axis,i in order if axis=='X']
    c.experiment['term_order_z']=[i for axis,i in order if axis=='Z']
    for axis,index in order:layer(axis,index)
    for i in range(m):c.add('H',[2*m+i],check=i,round_index=0)
    for i in range(2*m):
        rec=f'r0_s{i}';c.add('M',[2*m+i],record=rec,check=i,round_index=0,role='syndrome_readout');c.detectors.append([rec])
    # Signed instrument flows reject bad noncommuting CNOT interleavings.
    check(c)
    return c
