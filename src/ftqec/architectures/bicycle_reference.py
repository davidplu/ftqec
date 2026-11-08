"""Explicit published-reference reconstruction, never imported by search.

Seven interaction layers follow sbravyi/BivariateBicycleCodes decoder_setup.py,
blob 7ec5a36732a2a6dd229ab74405dedf36139ccda4 (Apache-2.0).
Preparation/readout are expanded to FTQEC RESET/H/M primitives. The original
ideal final syndrome boundary is NOT silently retained by physical memory().
"""
from ..circuits.model import Circuit
from ..screening.structural import check


def published_bb72(code):
    import numpy as np
    md=code.input.metadata
    if code.checks.n!=72 or md.get('group')!='Z6xZ6':raise ValueError('This reference is explicitly the published [[72,12,6]] construction')
    elems=md['group_elements'];inverse=[elems.index([(-i)%6,(-j)%6]) for i,j in elems]
    ai=[elems.index(list(x)) for x in ((3,0),(0,1),(0,2))]
    bi=[elems.index(list(x)) for x in ((0,3),(1,0),(2,0))]
    if set(md['a'])!=set(ai) or set(md['b'])!=set(bi):raise ValueError('Reference polynomial mismatch')
    xorder=[md['a'].index(i) for i in ai]+[3+md['b'].index(i) for i in bi]
    zorder=[md['b'].index(i) for i in bi]+[3+md['a'].index(i) for i in ai]
    xt=[code.x_terms[i] for i in xorder];zt=[code.z_terms[i] for i in zorder]
    # Independently reconstruct the upstream positive cyclic shifts, then
    # conjugate by group inversion to match the supplied regular-action labels.
    eye=np.eye(6,dtype=np.uint8)
    matrices=[np.kron(np.roll(eye,3,axis=1),eye),np.kron(eye,np.roll(eye,1,axis=1)),np.kron(eye,np.roll(eye,2,axis=1)),np.kron(eye,np.roll(eye,3,axis=1)),np.kron(np.roll(eye,1,axis=1),eye),np.kron(np.roll(eye,2,axis=1),eye)]
    for axis,terms,mats in [('X',xt,matrices),('Z',zt,[m.T for m in matrices[3:]+matrices[:3]])]:
        for term,matrix in enumerate(mats):
            for row in range(36):
                original=int(np.flatnonzero(matrix[inverse[row]])[0]);expected=inverse[original]+(36 if term>=3 else 0)
                if terms[term][row]!=expected:raise ValueError('Published/reference label transformation failed: '+axis)
    c=Circuit(code.checks,tuple(range(72,144)),())
    c.experiment=dict(rounds=1,family='published_bb_reference',generator_signs=[0]*72,reference_code=code.input.code.to_dict(),reference_signs=list(code.input.signs),reference_seed=True,classification='published reference only',upstream_blob='7ec5a36732a2a6dd229ab74405dedf36139ccda4',boundary_adaptation='explicit RESET/H/M primitives; physical memory boundaries supplied separately')
    for ch in range(72):c.add('RESET',[72+ch],check=ch,round_index=0)
    for ch in range(36):c.add('H',[72+ch],check=ch,round_index=0)
    sx=(None,1,4,3,5,0,2);sz=(3,5,0,1,2,4,None)
    for layer,(x,z) in enumerate(zip(sx,sz)):
        used=set()
        for axis,index,terms in [('X',x,xt),('Z',z,zt)]:
            if index is None:continue
            for row in range(36):
                ch=row if axis=='X' else row+36;anc=72+ch;data=terms[index][row]
                if {anc,data}&used:raise ValueError('Reference interaction layer conflict')
                used.update((anc,data));c.add('CX',[anc,data] if axis=='X' else [data,anc],check=ch,round_index=0,role='data_interaction',interaction_position=index,interval=layer)
        c.add('BARRIER',range(144),round_index=0,role='reference_interaction_layer')
    for ch in range(36):c.add('H',[72+ch],check=ch,round_index=0)
    for ch in range(72):
        rec=f'r0_s{ch}';c.add('M',[72+ch],record=rec,check=ch,round_index=0,role='syndrome_readout');c.detectors.append([rec])
    check(c);return c
