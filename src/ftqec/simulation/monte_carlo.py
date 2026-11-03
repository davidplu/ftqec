import math,time
import stim
from ..screening.structural import initial_state
from ..codes.logicals import logical_basis
from ..results.artifacts import digest

def interval(failures,shots):
    if not shots:return [0.,1.]
    z=1.959963984540054;p=failures/shots;den=1+z*z/shots
    mid=(p+z*z/(2*shots))/den;half=z*math.sqrt(p*(1-p)/shots+z*z/(4*shots*shots))/den
    return [max(0.,mid-half),min(1.,mid+half)]

def model(c,p,detector_basis="raw"):
    if not 0<=p<=1:raise ValueError("Physical probability")
    circuit=initial_state(c);records={};nm=0
    for op in c.operations:
        g={"PREP":"R","RESET":"R","SDG":"S_DAG","IDLE":"I"}.get(op.gate,op.gate)
        if g=="BARRIER":continue
        if g=="M":circuit.append("X_ERROR",op.qubits,p)
        circuit.append(g,op.qubits)
        if op.record:records[op.record]=nm
        if g=="M":nm+=1
        elif g=="R":circuit.append("X_ERROR",op.qubits,p)
        elif len(op.qubits)==2:circuit.append("DEPOLARIZE2",op.qubits,p)
        else:circuit.append("DEPOLARIZE1",op.qubits,p)
    # Ideal final stabilizer readout supplies the same boundary as exact faults.
    for i,pauli in enumerate(c.code.generators):
        targets=[]
        for q,label in enumerate(str(pauli)):
            if label!="I":
                if targets:targets.append(stim.target_combiner())
                targets.append({"X":stim.target_x,"Y":stim.target_y,"Z":stim.target_z}[label](q))
        circuit.append("MPP",targets);records[f"final{i}"]=nm;nm+=1
    detector_rows = list(c.detectors) + [[f"final{i}"] for i in range(len(c.code.generators))]
    if detector_basis=="temporal":
        by_record={o.record:o for o in c.operations if o.record};previous={};changed=[]
        for row in c.detectors:
            op=next((by_record[r] for r in row if "_s" in r),None)
            if op is None:changed.append(row)
            else:
                changed.append(list(set(row)^set(previous.get(op.check,[]))))
                previous[op.check]=row
        changed.extend(list({f"final{i}"}^set(previous.get(i,[]))) for i in range(len(c.code.generators)))
        detector_rows=changed
    elif detector_basis!="raw":raise ValueError("Unknown detector basis")
    for detector in detector_rows:
        circuit.append("DETECTOR",[stim.target_rec(records[r]-nm) for r in sorted(detector)])
    # The prepared logical Z sector defines a memory observable, separate from arbitrary-input claims.
    from ..codes.stabilizer import StabilizerCode
    reference=StabilizerCode.from_dict(c.experiment["reference_code"]) if "reference_code" in c.experiment else c.code
    for i,(x,z) in enumerate(logical_basis(reference)):
        targets=[]
        for q,label in enumerate(str(z)):
            if label!="I":
                if targets:targets.append(stim.target_combiner())
                targets.append({"X":stim.target_x,"Y":stim.target_y,"Z":stim.target_z}[label](q))
        circuit.append("MPP",targets);nm+=1;circuit.append("OBSERVABLE_INCLUDE",[stim.target_rec(-1)],i)
    return circuit

def evaluate(c,p,shots,seed,max_decoder_faults=10000,decoder="one_mechanism_lookup"):
    if decoder not in ("one_mechanism_lookup","matching","auto"):raise ValueError("Unknown decoder")
    if decoder!="one_mechanism_lookup":
        from .matching import evaluate_matching
        answer=evaluate_matching(c,p,shots,seed,max_decoder_faults)
        if answer.get("status")!="UNSUPPORTED_DECODER" or decoder=="matching":return answer
        fallback=evaluate(c,p,shots,seed,max_decoder_faults,"one_mechanism_lookup")
        fallback["decoder_fallback"]=answer;return fallback
    start=time.perf_counter();cpu=time.process_time();sc=model(c,p)
    dem=sc.detector_error_model(decompose_errors=False,approximate_disjoint_errors=False).flattened()
    # Explicit one-mechanism MAP lookup; collisions choose highest-probability mechanism.
    decoder_cpu=time.process_time();decoder_wall=time.perf_counter()
    table={0:(1.,0)};count=0
    for ins in dem:
        if ins.type!="error":continue
        count+=1
        if count>max_decoder_faults:raise MemoryError("Decoder mechanism limit")
        d=l=0
        for t in ins.targets_copy():
            if t.is_relative_detector_id():d^=1<<t.val
            if t.is_logical_observable_id():l^=1<<t.val
        prob=ins.args_copy()[0]
        if prob>table.get(d,(-1,0))[0]:table[d]=(prob,l)
    build_cost=dict(cpu=time.process_time()-decoder_cpu,wall=time.perf_counter()-decoder_wall)
    det,obs=sc.compile_detector_sampler(seed=seed).sample(shots,separate_observables=True)
    decoder_cpu=time.process_time();decoder_wall=time.perf_counter()
    failures=unknown=0
    for ds,ls in zip(det,obs):
        d=sum(int(b)<<i for i,b in enumerate(ds));l=sum(int(b)<<i for i,b in enumerate(ls))
        if d not in table:unknown+=1
        prediction=table.get(d,(0,0))[1]
        failures+=prediction!=l
    inference_cost=dict(cpu=time.process_time()-decoder_cpu,wall=time.perf_counter()-decoder_wall)
    return dict(decoder_build_cost=build_cost,decoder_inference_cost=inference_cost,p=p,shots=shots,failures=failures,decoder_unknown=unknown,rate=failures/shots,confidence=interval(failures,shots),seed=seed,
        decoder="one_mechanism_max_probability_lookup_with_zero_fallback",noise="operation_depolarizing_reset_X_measurement_flip_perfect_boundaries",stim_hash=digest(str(sc)),cpu=time.process_time()-cpu,wall=time.perf_counter()-start)
