"""Documented development references, never injected into population seeds."""
import stim
from ..codes.input import load
from ..circuits.model import Circuit

def rotated_surface(distance=3,rounds=None):
    if type(distance) is not int or distance<2:raise ValueError("Integer distance>=2")
    rounds=distance if rounds is None else rounds
    template=stim.Circuit.generated("surface_code:rotated_memory_z",distance=distance,rounds=1).flattened()
    instructions=list(template);anc=next([t.value for t in op.targets_copy()] for op in instructions if op.name=="MR")
    data=next([t.value for t in op.targets_copy()] for op in instructions if op.name=="M");data=sorted(data)
    mapping={q:i for i,q in enumerate(data+anc)};supports={q:set() for q in anc};xanc=set();body=[]
    for op in instructions:
        if op.name=="MR":break
        if op.name=="H":xanc.update(t.value for t in op.targets_copy())
        if op.name in ("H","CX"):
            targets=[t.value for t in op.targets_copy()];body.append((op.name,targets))
            if op.name=="CX":
                for a,b in zip(targets[::2],targets[1::2]):
                    if a in supports:supports[a].add(b)
                    if b in supports:supports[b].add(a)
    generators=[]
    for a in anc:
        text=["I"]*len(data)
        for q in supports[a]:text[mapping[q]]="X" if a in xanc else "Z"
        generators.append("".join(text))
    inp=load(dict(n=len(data),name=f"rotated_surface_{distance}",generators=generators,metadata=dict(family="rotated_surface",designed_distance_claim=distance)))
    c=Circuit(inp.code,tuple(mapping[a] for a in anc),())
    c.experiment=dict(scope="syndrome_extraction_with_ideal_code_space_boundaries",family="surface_reference_schedule",rounds=rounds,generator_signs=[0]*len(generators),reference_origin=dict(generator="stim surface_code:rotated_memory_z",stim_version=stim.__version__,designed_distance=distance,scope="schedule adapted only; no generated memory certificate reused"))
    for rd in range(rounds):
        for a in anc:c.add("RESET",[mapping[a]],round_index=rd,role="syndrome_reset")
        for gate,targets in body:
            arity=2 if gate=="CX" else 1
            for i in range(0,len(targets),arity):c.add(gate,[mapping[q] for q in targets[i:i+arity]],round_index=rd,role="reference_interaction")
        for j,a in enumerate(anc):
            rec=f"r{rd}_s{j}";c.add("M",[mapping[a]],record=rec,check=j,round_index=rd,role="syndrome_readout");c.detectors.append([rec])
    c.validate();return inp,c
