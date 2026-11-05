"""Physical CSS memory rounds with noisy product preparation and destructive readout."""
from dataclasses import replace
from .model import Circuit
from ..codes.logicals import logical_basis
from ..results.artifacts import digest


def repeat(single,rounds):
    if type(rounds) is not int or rounds<1:raise ValueError('Positive round count')
    if single.experiment.get('rounds',1)!=1 or single.boundary_model!='ideal_initial_and_final_syndrome':raise ValueError('A single extraction round is required')
    if single.observables:raise ValueError('Extraction template must not have terminal observables')
    c=Circuit(single.code,single.syndrome_qubits,single.flag_qubits)
    c.experiment=dict(single.experiment,rounds=rounds,extraction_template_hash=digest(single.to_dict()))
    for r in range(rounds):
        c.add('BARRIER',range(c.num_qubits),round_index=r,role='round_start')
        offset=len(c.operations);names={o.record:f'round{r}:{o.record}' for o in single.operations if o.record}
        for op in single.operations:c.operations.append(replace(op,deps=tuple(offset+d for d in op.deps),record=names.get(op.record),round_index=r))
        c.detectors.extend([[names[x] for x in row] for row in single.detectors])
        c.add('BARRIER',range(c.num_qubits),round_index=r,role='round_end')
    c.detector_offsets=list(single.detector_offsets)*rounds
    c.validate();return c


def memory(single,rounds,basis='Z',idles=False):
    from ..screening.structural import check
    check(single)
    if basis not in ('X','Z'):raise ValueError('Memory basis must be X or Z')
    if any(set(str(g))-{'I'} not in ({'X'},{'Z'}) for g in single.code.generators):raise ValueError('CSS memory preparation required')
    if any(single.experiment.get('generator_signs',[])):raise ValueError('Signed CSS memory preparation is not yet supported')
    rep=repeat(single,rounds);c=Circuit(single.code,single.syndrome_qubits,single.flag_qubits,boundary_model='repeated_noisy_memory')
    c.experiment=dict(rep.experiment,memory_basis=basis,memory_protocol='product_prepare_repeated_css_destructive_readout_v1',idle_policy='explicit_active_storage' if idles else 'none',extraction_template=single.to_dict())
    for q in range(c.code.n):c.add('RESET',[q],role='memory_input')
    if basis=='X':
        for q in range(c.code.n):c.add('H',[q],role='memory_input')
    offset=len(c.operations)
    c.operations.extend(replace(o,deps=tuple(d+offset for d in o.deps)) for o in rep.operations)
    records={o.record:o for o in c.operations if o.record};previous={};history=[]
    for row in rep.detectors:
        checks={records[r].check for r in row if records[r].check is not None and '_s' in r}
        if not checks:c.detectors.append(row);continue
        if len(checks)!=1:raise ValueError('Ambiguous extraction parity')
        ch=next(iter(checks));axis=set(str(c.code.generators[ch]))-{'I'}
        if ch in previous:c.detectors.append(row+previous[ch])
        elif axis=={basis}:c.detectors.append(row)
        previous[ch]=row;history.append(dict(check=ch,round=records[row[0]].round_index,records=row))
    if len(previous)!=len(c.code.generators):raise ValueError('Missing check history')
    c.add('BARRIER',range(c.num_qubits),role='terminal_start')
    if basis=='X':
        for q in range(c.code.n):c.add('H',[q],role='memory_readout')
    for q in range(c.code.n):c.add('M',[q],record=f'data{q}',role='memory_readout')
    for ch,g in enumerate(c.code.generators):
        if set(str(g))-{'I'}=={basis}:c.detectors.append(previous[ch]+[f'data{q}' for q in range(c.code.n) if (g.x|g.z)>>q&1])
    for x,z in logical_basis(c.code):
        p=x if basis=='X' else z
        c.observables.append([f'data{q}' for q in range(c.code.n) if (p.x|p.z)>>q&1])
    c.experiment['measurement_history']=history
    if idles:c=with_idles(c)
    c.detector_offsets=[0]*len(c.detectors);c.validate();return c


def with_idles(c):
    from ..scheduling.scheduler import schedule
    s=schedule(c);layers={}
    for i,(op,t) in enumerate(zip(c.operations,s.starts)):
        if op.gate!='BARRIER':layers.setdefault(t,[]).append(op)
    out=Circuit.from_dict(c.to_dict());out.operations=[];live=set()
    for t in range(s.depth):
        ops=layers.get(t,[]);used={q for o in ops for q in o.qubits}
        for o in ops:
            if o.gate in ('RESET','PREP'):live.update(o.qubits)
            out.operations.append(replace(o,deps=()))
        for q in sorted(live-used):out.add('IDLE',[q],role='storage',interval=t)
        out.add('BARRIER',range(c.num_qubits),role='storage_tick',interval=t)
    return out


def stim_model(c,p=0):
    import stim
    if not 0<=p<=1:raise ValueError('Physical probability')
    out=stim.Circuit();records={};nm=0
    for op in c.operations:
        gate={'RESET':'R','PREP':'R','SDG':'S_DAG','IDLE':'I'}.get(op.gate,op.gate)
        if gate=='BARRIER':out.append('TICK');continue
        if gate=='M':out.append('X_ERROR',op.qubits,p)
        out.append(gate,op.qubits)
        if op.record:records[op.record]=nm
        if gate=='M':nm+=1
        else:out.append('X_ERROR' if gate=='R' else 'DEPOLARIZE2' if len(op.qubits)==2 else 'DEPOLARIZE1',op.qubits,p)
    for row in c.detectors:out.append('DETECTOR',[stim.target_rec(records[r]-nm) for r in row])
    for i,row in enumerate(c.observables):out.append('OBSERVABLE_INCLUDE',[stim.target_rec(records[r]-nm) for r in row],i)
    return out


def validate_memory(c):
    import stim
    from ..screening.structural import check
    c.validate();e=c.experiment
    if e.get('memory_protocol')!='product_prepare_repeated_css_destructive_readout_v1':raise ValueError('Unsupported memory protocol')
    template=Circuit.from_dict(e['extraction_template']);check(template)
    if template.code.to_dict()!=c.code.to_dict() or digest(template.to_dict())!=e['extraction_template_hash']:raise ValueError('Extraction template binding')
    basis=e['memory_basis'];r=e['rounds'];history=e['measurement_history']
    if sorted((h['round'],h['check']) for h in history)!=[(i,j) for i in range(r) for j in range(len(c.code.generators))]:raise ValueError('Incomplete measurement history')
    # Validate each recorded check directly against physical measurement operations.
    by_name={o.record:o for o in c.operations if o.record}
    for h in history:
        if any(by_name[name].round_index!=h['round'] or by_name[name].check!=h['check'] for name in h['records']):raise ValueError('Measurement history binding')
    if type(r) is not int or r<1 or basis not in ('X','Z'):raise ValueError('Memory task declaration')
    # Independent per-wire operation sequences bind each physical round to its template.
    for rd in range(r):
        actual=[o for o in c.operations if o.round_index==rd and o.gate not in ('BARRIER','IDLE')]
        expected_ops=[o for o in template.operations if o.gate not in ('BARRIER','IDLE')]
        key=lambda o,record:(o.gate,o.qubits,record,o.check,o.role,o.interaction_position)
        for q in range(c.num_qubits):
            left=[key(o,o.record) for o in actual if q in o.qubits]
            right=[key(o,f'round{rd}:{o.record}' if o.record else None) for o in expected_ops if q in o.qubits]
            if left!=right:raise ValueError('Physical extraction round differs from template')
    boundary=[o for o in c.operations if o.round_index is None and o.gate not in ('BARRIER','IDLE')]
    for q in range(c.code.n):
        actual=[(o.gate,o.record,o.role) for o in boundary if q in o.qubits]
        wanted=[('RESET',None,'memory_input')]+([('H',None,'memory_input'),('H',None,'memory_readout')] if basis=='X' else [])+[('M',f'data{q}','memory_readout')]
        if actual!=wanted:raise ValueError('Physical memory boundary differs from declaration')
    expected_detectors=[];last={}
    for rd in range(r):
        for row in template.detectors:
            named=[f'round{rd}:{name}' for name in row]
            matches=[o.check for o in template.operations if o.record in row and '_s' in o.record]
            if not matches:expected_detectors.append(named);continue
            ch=matches[0]
            if ch in last:expected_detectors.append(named+last[ch])
            elif set(str(c.code.generators[ch]))-{'I'}=={basis}:expected_detectors.append(named)
            last[ch]=named
    for ch,g in enumerate(c.code.generators):
        if set(str(g))-{'I'}=={basis}:expected_detectors.append(last[ch]+[f'data{q}' for q in range(c.code.n) if (g.x|g.z)>>q&1])
    if c.detectors!=expected_detectors:raise ValueError('Incomplete or fabricated temporal detectors')
    if e['idle_policy']=='explicit_active_storage':
        from ..scheduling.scheduler import schedule
        sched=schedule(c)
        for q in range(c.num_qubits):
            resets=[t for t,o in zip(sched.starts,c.operations) if o.gate in ('RESET','PREP') and q in o.qubits]
            used={t for t,o in zip(sched.starts,c.operations) if o.gate!='BARRIER' and q in o.qubits}
            if resets and any(t not in used for t in range(min(resets),sched.depth)):raise ValueError('Missing active storage fault location')
    expected=[]
    for x,z in logical_basis(c.code):
        logical=x if basis=='X' else z
        expected.append([f'data{q}' for q in range(c.code.n) if (logical.x|logical.z)>>q&1])
    if c.observables!=expected:raise ValueError('Logical readout definitions')
    actual=stim_model(c,0);actual.detector_error_model(allow_gauge_detectors=False)
    # Independent signed stabilizer flows establish deterministic declared detectors and observables.
    physical=stim.Circuit();idx={};count=0
    for op in c.operations:
        if op.gate=='BARRIER':continue
        physical.append({'RESET':'R','PREP':'R','SDG':'S_DAG','IDLE':'I'}.get(op.gate,op.gate),op.qubits)
        if op.record:idx[op.record]=count
        if op.gate=='M':count+=1
    if not physical.has_all_flows([stim.Flow(measurements=[idx[x] for x in row]) for row in c.detectors+c.observables],unsigned=False):raise ValueError('Nondeterministic memory parity')
    c.detector_offsets=[0]*len(c.detectors)
    return dict(status='STRUCTURALLY_VALID',circuit=digest(c.to_dict()),scope='Physical CSS product preparation, noisy repeated extraction and noisy destructive readout; one logical Pauli sector',basis=basis,rounds=r)
