"""Independent reconstruction and evidence checks for delivered circuits.

Does not call the schedule/export producer. A bound receipt cannot substitute
for executing the original source's independent proof checker.
"""
import hashlib
import json
from pathlib import Path
from collections import Counter, defaultdict
from ..circuits.model import Circuit
from ..results.artifacts import digest, source_identity
from ..certification.exact import MODEL, SCOPE


def reconstruct(payload):
    if payload.get('schema') != 'ftqec-research-bundle-1':
        raise ValueError('Unknown schedule schema')
    body = {k:v for k,v in payload.items() if k != 'schedule_identity'}
    if digest(body) != payload.get('schedule_identity'):
        raise ValueError('Schedule identity')
    rows = payload['operations']
    if [r['id'] for r in rows] != list(range(len(rows))):
        raise ValueError('Operation coverage/order')
    c = Circuit.from_dict(dict(payload['metadata'], operations=[r['operation'] for r in rows]))
    if digest(c.to_dict()) != payload['circuit']:
        raise ValueError('Reconstructed circuit identity')
    nm=0
    last = {}; finishes = []; chain = []; work = Counter(); groups = defaultdict(list); records = {}; epochs = []; active = {}
    for i, (op,r) in enumerate(zip(c.operations,rows)):
        needed = set(op.deps)
        needed.update(last[q] for q in op.qubits if q in last)
        if r['dependencies'] != sorted(needed):
            raise ValueError('Missing or fabricated dependencies')
        start = max((finishes[j] for j in needed),default=0)
        duration = 0 if op.gate == 'BARRIER' else 1
        if type(r['start']) is not int or type(r['end']) is not int or (r['start'],r['end']) != (start,start+duration):
            raise ValueError('Schedule time/dependency conflict')
        finishes.append(start+duration)
        chain.append(duration+max((chain[j] for j in op.deps),default=0))
        groups[start].append(i)
        if r.get('measurement_index') != (nm if op.record else None):
            raise ValueError('Measurement record order')
        if op.record:
            records[op.record] = dict(operation=i,index=nm,layer=start)
        if op.gate=='M':nm+=1
        for q in op.qubits:
            last[q]=i;work[q]+=duration
            if q < c.code.n:
                continue
            if op.gate in ('RESET','PREP'):
                if q in active:
                    epochs[active[q]]['next_reset']=i
                active[q]=len(epochs)
                epochs.append(dict(qubit=q,reset=i,start=start,end=start+duration,operations=[],measurements=[],next_reset=None))
            if q not in active:
                raise ValueError('Missing ancilla reset')
            epoch=epochs[active[q]];epoch['operations'].append(i);epoch['end']=max(epoch['end'],start+duration)
            if op.gate=='M':epoch['measurements'].append(i)
    expected_groups=[dict(start=t,operations=ids) for t,ids in sorted(groups.items())]
    if payload['parallel_groups']!=expected_groups or payload['measurements']!=records or payload['ancilla_lifetimes']!=epochs:
        raise ValueError('Parallel/measurement/lifecycle inconsistency')
    depth=max(finishes,default=0)
    if depth!=payload['depth']:
        raise ValueError('Depth mismatch')
    counts=Counter(o.gate for o in c.operations);two=sum(counts[g] for g in ('CX','CZ','SWAP'));capacity=max(1,c.num_qubits//2)
    bound=max(max(work.values(),default=0),max(chain,default=0),(two+capacity-1)//capacity)
    metrics=dict(data_qubits=c.code.n,syndrome_ancillas=len(c.syndrome_qubits),flag_ancillas=len(c.flag_qubits),Q=c.num_qubits,
                 D=depth,QD=c.num_qubits*depth,one_q_gates=sum(counts[g] for g in ('H','S','SDG','X','Y','Z')),two_q_gates=two,
                 measurements=counts['M'],resets=counts['RESET'],preparations=counts['PREP'],operation_count=len(c.operations)-counts['BARRIER'],
                 depth_lower_bound=bound,schedule_efficiency=bound/depth if depth else 1.)
    return c,metrics


def verify_stim(c, text, p):
    import stim
    from ..simulation.monte_carlo import model
    actual=stim.Circuit(text)
    expected=model(c,p)
    records={};nm=0
    for op in c.operations:
        if op.record:records[op.record]=nm
        if op.gate=='M':nm+=1
    for i,row in enumerate(c.observables,start=c.code.k):
        expected.append('OBSERVABLE_INCLUDE',[stim.target_rec(records[r]-expected.num_measurements) for r in row],i)
    def normalized(circuit):
        out=stim.Circuit()
        for inst in circuit.flattened():
            if inst.name=='TICK':continue
            if inst.name in ('X_ERROR','DEPOLARIZE1','DEPOLARIZE2') and inst.gate_args_copy()==[0]:continue
            out.append(inst)
        return out
    if normalized(actual)!=normalized(expected):raise ValueError('Stim operations/noise/detectors/observables mismatch')
    actual.detector_error_model(allow_gauge_detectors=False)
    return True


def verify_bundle(path, work=20000000, replay_proof=True):
    root=Path(path)
    if root.is_file():
        data=json.loads(root.read_text(encoding='utf-8-sig'));c,metrics=reconstruct(data)
        return dict(verified=True,reconstruction_verified=True,circuit=digest(c.to_dict()),resources=metrics,certificate_binding='NOT_PRESENT',positive_certificate_verified=False)
    read=lambda name:json.loads((root/name).read_text(encoding='utf-8-sig'))
    manifest=read('manifest.json')
    required={'tasks.json','input_code.json','circuit.json','schedule.json','resources.json','certificate.json','evidence.json','circuit.stim','REPRODUCE.txt','schedule.txt'}
    if set(manifest['members'])!=required or {p.name for p in root.iterdir()}!=required|{'manifest.json'}:
        raise ValueError('Incomplete or unexpected bundle members')
    for name,sha in manifest['members'].items():
        if Path(name).name!=name or hashlib.sha256((root/name).read_bytes()).hexdigest()!=sha:
            raise ValueError('Bundle member integrity')
    c,metrics=reconstruct(read('schedule.json'));circuit=digest(c.to_dict())
    if c.to_dict()!=read('circuit.json') or metrics!=read('resources.json') or manifest['circuit']!=circuit or manifest['schedule']!=read('schedule.json')['schedule_identity']:
        raise ValueError('Circuit/schedule/resource binding')
    evidence=read('evidence.json');cert=read('certificate.json')
    from ..circuits.identity import physical_identity
    candidate_id=evidence['row']['id']
    if evidence['row']['circuit']!=c.to_dict() or candidate_id not in (circuit,physical_identity(c)) or manifest.get('candidate_id',candidate_id)!=candidate_id or evidence['row'].get('certify')!=cert:
        raise ValueError('Optimizer evidence binding')
    if manifest.get('fault_model')!=MODEL or manifest.get('scope')!=SCOPE or evidence.get('noise_model')!=MODEL or evidence.get('scope')!=SCOPE:
        raise ValueError('Fault model mismatch')
    if evidence['optimizer_source']!=manifest['evidence_source'] or evidence['exporter_source']!=manifest['exporter_source'] or digest(evidence['source_records'])!=manifest['exporter_source']:
        raise ValueError('Source binding')
    for packet in read('tasks.json'):
        task=packet['request']
        if task.get('circuit')!=c.to_dict() or task.get('source')!=manifest['evidence_source']:
            raise ValueError('Simulation/proof task binding')
        from ..execution.tasks import Task
        if Task(**task).identity!=packet['answer'].get('task'):
            raise ValueError('Task answer identity')
    from ..codes.input import load
    original=load(read('input_code.json')).code
    if original.n!=c.code.n or original.rank!=c.code.rank or any(not original.is_stabilizer(g) for g in c.code.generators):
        raise ValueError('Input stabilizer group mismatch')
    verify_stim(c,(root/'circuit.stim').read_text(encoding='utf-8'),evidence['noise_probability'])
    from ..screening.structural import check
    check(c)
    if digest(c.to_dict())!=circuit:raise ValueError('Noiseless validation changed circuit identity')
    binding=False;proof=dict(verified=False,reason='NOT_RUN')
    if cert:
        binding=cert.get('circuit')==circuit and cert.get('source')==manifest['evidence_source'] and cert.get('fault_model')==MODEL and cert.get('scope')==SCOPE
        if not binding:raise ValueError('Certificate identity/fault model mismatch')
        if replay_proof:
            if cert['source']!=source_identity():proof=dict(verified=False,reason='SOURCE_MISMATCH: install the original scientific source to replay')
            else:
                from ..certification.exact import verify
                proof=verify(c,cert,work)
    positive=bool(cert and cert['status']=='CERTIFIED' and proof['verified'])
    return dict(verified=True,reconstruction_verified=True,stim_verified=True,resource_recomputation_verified=True,circuit=circuit,
                schedule=manifest['schedule'],evidence_source=manifest['evidence_source'],certificate_binding_verified=binding,
                recorded_status=cert['status'] if cert else 'NOT_RUN',proof_replay=proof,positive_certificate_verified=positive,
                qualification='verified denotes reconstruction/integrity; positive_certificate_verified separately requires actual proof replay')
