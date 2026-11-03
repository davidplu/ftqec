from ..results.artifacts import digest
from ..scheduling.scheduler import schedule

def physical_identity(c):
    records={op.record:i for i,op in enumerate(c.operations) if op.record}
    sched=schedule(c)
    return digest(dict(code=c.code.to_dict(),signs=c.experiment.get("generator_signs",[]),qubits=c.num_qubits,
        operations=[dict(gate=o.gate,qubits=list(o.qubits),start=sched.starts[i]) for i,o in enumerate(c.operations)],
        detectors=[[records[r] for r in d] for d in c.detectors],observables=[[records[r] for r in d] for d in c.observables],
        detector_offsets=c.detector_offsets,boundary=c.boundary_model))
