"""Remove allocated but unused ancillas under the explicit-operation model."""
from dataclasses import replace
from ..circuits.model import Circuit
from ..results.artifacts import digest


def compact(c):
    used={q for op in c.operations for q in op.qubits}
    syn=[q for q in c.syndrome_qubits if q in used];flags=[q for q in c.flag_qubits if q in used]
    mapping={q:q for q in range(c.code.n)}
    mapping.update({q:c.code.n+i for i,q in enumerate(syn+flags)})
    out=Circuit.from_dict(c.to_dict());out.syndrome_qubits=tuple(mapping[q] for q in syn);out.flag_qubits=tuple(mapping[q] for q in flags)
    out.operations=[replace(op,qubits=tuple(mapping[q] for q in op.qubits)) for op in c.operations]
    out.experiment=dict(out.experiment,allocation_compaction=dict(parent_circuit=digest(c.to_dict()),removed=sorted((set(c.syndrome_qubits)|set(c.flag_qubits))-used),mapping={str(q):new for q,new in mapping.items()},scope='Unused allocated ancillas only; no physical operations removed; recertification required'))
    out.validate();return out
