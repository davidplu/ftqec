import stim
from ..codes.logicals import logical_basis
from ..results.artifacts import digest

def initial_state(c):
    from ..codes.stabilizer import StabilizerCode
    code=StabilizerCode.from_dict(c.experiment["reference_code"]) if "reference_code" in c.experiment else c.code
    signs=c.experiment.get("reference_signs",c.experiment.get("generator_signs",[0]*len(code.generators)))
    stabilizers=[stim.PauliString(("-" if sign else "+")+str(p)) for p,sign in zip(code.generators,signs)]
    stabilizers += [stim.PauliString(str(z)) for x,z in logical_basis(code)]
    return stim.Tableau.from_stabilizers(stabilizers).to_circuit()

def apply(sim,op):
    g={"PREP":"R","RESET":"R","SDG":"S_DAG","IDLE":"I"}.get(op.gate,op.gate)
    if g=="BARRIER":return None
    if g=="M":return sim.measure(op.qubits[0])
    sim.do(stim.Circuit(f"{g} "+" ".join(map(str,op.qubits))))
    return None

def legacy_check(c):
    c.validate();sim=stim.TableauSimulator();sim.do(initial_state(c));records={};known=set(range(c.code.n))
    for op in c.operations:
        if op.gate in ("PREP","RESET"):known.add(op.qubits[0])
        elif any(q not in known for q in op.qubits):raise ValueError("Unprepared ancilla")
        value=apply(sim,op)
        if op.record:records[op.record]=int(value)
    ideal=stim.Circuit();indices={};nm=0
    for op in c.operations:
        g={"PREP":"R","RESET":"R","SDG":"S_DAG","IDLE":"I"}.get(op.gate,op.gate)
        if g=="BARRIER":continue
        ideal.append(g,op.qubits)
        if op.record:indices[op.record]=nm
        if g=="M":nm+=1
    measured=set()
    for detector in c.detectors:
        syndrome=next((op for op in c.operations if op.record in detector and "_s" in op.record),None)
        if syndrome:
            if not 0<=syndrome.check<len(c.code.generators):raise ValueError("Unknown measured check")
            measured.add((syndrome.check,syndrome.round_index if syndrome.round_index is not None else 0))
        pauli=str(c.code.generators[syndrome.check]) if syndrome else "I"*c.code.n
        padded=stim.PauliString(pauli+"I"*(c.num_qubits-c.code.n))
        if not ideal.has_flow(stim.Flow(input=padded,measurements=[indices[r] for r in detector])):raise ValueError("Incorrect stabilizer measurement flow")
    rounds=c.experiment.get("rounds",1)
    if type(rounds) is not int or not 1<=rounds<=len(c.operations)+1:raise ValueError("Invalid extraction-round declaration")
    if any((i,rd) not in measured for i in range(len(c.code.generators)) for rd in range(rounds)):raise ValueError("Incomplete stabilizer measurement coverage")
    for x,z in logical_basis(c.code):
        for p in (x,z):
            padded=stim.PauliString(str(p)+"I"*(c.num_qubits-c.code.n))
            if not ideal.has_flow(stim.Flow(input=padded,output=padded)):raise ValueError("Logical instrument disturbance")
    offsets=[sum(records[r] for r in d)%2 for d in c.detectors]
    c.detector_offsets=offsets
    signs=c.experiment.get("generator_signs",[0]*len(c.code.generators))
    for p,sign in zip(c.code.generators,signs):
        if sim.peek_observable_expectation(stim.PauliString(str(p)))!=(-1 if sign else 1):raise ValueError("Data code-space not preserved")
    return dict(status="STRUCTURALLY_VALID",circuit=digest(c.to_dict()),detector_offsets=offsets,scope="Signed stabilizer measurement and logical-preservation flows verified by Stim; code-space reference parity checked")


def check(c):
    c.validate();sim=stim.TableauSimulator();sim.do(initial_state(c));known=set(range(c.code.n));initial_measurements=len(sim.current_measurement_record())
    for op in c.operations:
        if op.gate in ("PREP","RESET"):known.add(op.qubits[0])
        elif any(q not in known for q in op.qubits):raise ValueError("Unprepared ancilla")
    ideal=stim.Circuit();indices={};nm=0
    for op in c.operations:
        g={"PREP":"R","RESET":"R","SDG":"S_DAG","IDLE":"I"}.get(op.gate,op.gate)
        if g=="BARRIER":continue
        ideal.append(g,op.qubits)
        if op.record:indices[op.record]=nm
        if g=="M":nm+=1
    sim.do(ideal);measurements=sim.current_measurement_record()
    records={name:int(measurements[initial_measurements+index]) for name,index in indices.items()}
    measured=set();flow_checks=[];record_ops={op.record:op for op in c.operations if op.record}
    for detector in c.detectors:
        syndrome=next((record_ops[r] for r in detector if "_s" in r),None)
        if syndrome:
            if not 0<=syndrome.check<len(c.code.generators):raise ValueError("Unknown measured check")
            measured.add((syndrome.check,syndrome.round_index if syndrome.round_index is not None else 0))
        pauli=str(c.code.generators[syndrome.check]) if syndrome else "I"*c.code.n
        padded=stim.PauliString(pauli+"I"*(c.num_qubits-c.code.n))
        flow_checks.append(stim.Flow(input=padded,measurements=[indices[r] for r in detector]))
    rounds=c.experiment.get("rounds",1)
    if type(rounds) is not int or not 1<=rounds<=len(c.operations)+1:raise ValueError("Invalid extraction-round declaration")
    if any((i,rd) not in measured for i in range(len(c.code.generators)) for rd in range(rounds)):raise ValueError("Incomplete stabilizer measurement coverage")
    for x,z in logical_basis(c.code):
        for p in (x,z):
            padded=stim.PauliString(str(p)+"I"*(c.num_qubits-c.code.n))
            flow_checks.append(stim.Flow(input=padded,output=padded))
    if not ideal.has_all_flows(flow_checks,unsigned=False):raise ValueError("Incorrect signed measurement or logical-preservation flow")
    offsets=[sum(records[r] for r in d)%2 for d in c.detectors]
    c.detector_offsets=offsets
    signs=c.experiment.get("generator_signs",[0]*len(c.code.generators))
    for p,sign in zip(c.code.generators,signs):
        if sim.peek_observable_expectation(stim.PauliString(str(p)))!=(-1 if sign else 1):raise ValueError("Data code-space not preserved")
    return dict(status="STRUCTURALLY_VALID",circuit=digest(c.to_dict()),detector_offsets=offsets,scope="Signed stabilizer measurement and logical-preservation flows verified by Stim; code-space reference parity checked")
