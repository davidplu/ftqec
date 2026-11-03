"""Physical timed-structure classes for diversity, separate from certificate identities."""
from ..scheduling.scheduler import schedule
from ..results.artifacts import digest


def timed_structure(c):
    s=schedule(c)
    # Gates on a shared qubit cannot occupy the same positive-duration layer.
    # Thus sorting disjoint simultaneous operations removes textual ordering only.
    events=sorted((s.starts[i],o.gate,tuple(o.qubits),i) for i,o in enumerate(c.operations) if o.gate!='BARRIER')
    records={c.operations[old].record:new for new,(_,_,_,old) in enumerate(events) if c.operations[old].record}
    detectors=sorted((sorted(records[r] for r in row),offset) for row,offset in zip(c.detectors,c.detector_offsets or [0]*len(c.detectors)))
    return digest(dict(code=c.code.to_dict(),signs=c.experiment.get('generator_signs',[]),qubits=c.num_qubits,
        gates=[(t,g,qs) for t,g,qs,_ in events],detectors=detectors,observables=sorted(sorted(records[r] for r in row) for row in c.observables),boundary=c.boundary_model))
