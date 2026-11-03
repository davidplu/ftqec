"""Export exact optimizer records; a receipt is not itself a new proof."""
import json
from pathlib import Path
from collections import defaultdict
from ..circuits.model import Circuit, operation_payload
from ..scheduling.scheduler import schedule
from ..evaluation.resources import resources
from ..results.artifacts import digest, source_identity, source_records, save
from ..certification.exact import MODEL, SCOPE

VERSION = 'ftqec-research-bundle-1'


def schedule_payload(c):
    s = schedule(c)
    rows = []
    previous = {}
    groups = defaultdict(list)
    records = {}
    nm = 0
    epochs = []
    active = {}
    for i, (op, start) in enumerate(zip(c.operations, s.starts)):
        dependencies = set(op.deps) | {previous[q] for q in op.qubits if q in previous}
        end = start + (op.gate != 'BARRIER')
        rows.append(dict(id=i, operation=operation_payload(op), start=start, end=end,
                         dependencies=sorted(dependencies), measurement_index=nm if op.record else None))
        if op.record:
            records[op.record] = dict(operation=i, index=nm, layer=start)
        if op.gate == 'M':
            nm += 1
        groups[start].append(i)
        for q in op.qubits:
            previous[q] = i
            if q < c.code.n:
                continue
            if op.gate in ('RESET', 'PREP'):
                if q in active:
                    epochs[active[q]]['next_reset'] = i
                active[q] = len(epochs)
                epochs.append(dict(qubit=q, reset=i, start=start, end=end, operations=[], measurements=[], next_reset=None))
            if q not in active:
                raise ValueError('Ancilla used before preparation')
            e = epochs[active[q]]
            e['operations'].append(i)
            e['end'] = max(e['end'], end)
            if op.gate == 'M':
                e['measurements'].append(i)
    metadata = c.to_dict()
    del metadata['operations']
    payload = dict(schema=VERSION, circuit=digest(c.to_dict()), metadata=metadata,
                   operations=rows, parallel_groups=[dict(start=t, operations=ids) for t, ids in sorted(groups.items())],
                   measurements=records, ancilla_lifetimes=epochs, depth=s.depth,
                   clock='unit-duration explicit operations; BARRIER has zero duration; no implicit idle faults')
    return dict(payload, schedule_identity=digest(payload))


def stim_text(c, p=0):
    """Physical extraction plus explicitly marked ideal simulation boundaries.

    The arbitrary-input certificate includes X and Z logical effects; this Stim
    experiment prepares a logical-Z sector. It is not a physical-memory export.
    """
    if not 0 <= p <= 1:
        raise ValueError('Noise probability must be in [0,1]')
    from ..screening.structural import initial_state
    from ..codes.logicals import logical_basis
    from ..codes.stabilizer import StabilizerCode
    lines = ['# FTQEC ' + digest(c.to_dict()), '# Ideal code-space preparation: outside the certified fault universe', str(initial_state(c)).strip()]
    records = {}; count = 0
    for i, op in enumerate(c.operations):
        lines.append('# operation ' + str(i))
        g = {'PREP':'R', 'RESET':'R', 'SDG':'S_DAG', 'IDLE':'I'}.get(op.gate, op.gate)
        if g == 'BARRIER':
            lines.append('TICK'); continue
        qs = ' '.join(map(str, op.qubits))
        if g == 'M' and p:
            lines.append(f'X_ERROR({p}) {qs}')
        lines.append(g + ' ' + qs)
        if g == 'M':
            if op.record:
                records[op.record] = count
            count += 1
        elif p:
            noise = 'X_ERROR' if g == 'R' else 'DEPOLARIZE2' if len(op.qubits) == 2 else 'DEPOLARIZE1'
            lines.append(f'{noise}({p}) {qs}')
    lines.append('# Ideal final stabilizer boundaries: outside the certified fault universe')
    for i, pauli in enumerate(c.code.generators):
        lines.append('MPP ' + '*'.join(a+str(q) for q,a in enumerate(str(pauli)) if a != 'I'))
        records['final'+str(i)] = count; count += 1
    for row in list(c.detectors) + [['final'+str(i)] for i in range(len(c.code.generators))]:
        lines.append('DETECTOR ' + ' '.join(f'rec[{records[r]-count}]' for r in row))
    reference = StabilizerCode.from_dict(c.experiment['reference_code']) if 'reference_code' in c.experiment else c.code
    pairs = logical_basis(reference)
    for i, (_, z) in enumerate(pairs):
        lines.append('MPP ' + '*'.join(a+str(q) for q,a in enumerate(str(z)) if a != 'I'))
        count += 1; lines.append(f'OBSERVABLE_INCLUDE({i}) rec[-1]')
    for i,row in enumerate(c.observables, start=len(pairs)):
        lines.append(f'OBSERVABLE_INCLUDE({i}) ' + ' '.join(f'rec[{records[r]-count}]' for r in row))
    return '\n'.join(lines) + '\n'


def resolve(run, circuit_id):
    path = Path(run)
    path = path/'checkpoint.json' if path.is_dir() else path
    state = json.loads(path.read_text(encoding='utf-8'))
    if state.get('schema')=='sqlite-population-1':
        from ..optimization.store import PopulationStore
        with PopulationStore(path.parent/state['population_db'],readonly=True) as db:
            state=db.get_meta('state');return state,db.get(circuit_id)
    matches = [r for r in state['rows'] if r['id'] == circuit_id]
    if len(matches) != 1:
        raise ValueError('Circuit ID must identify exactly one optimizer row in --run')
    return state, matches[0]


def export_result(run, circuit_id, output, format='bundle', noise_p=None):
    if format not in ('bundle', 'schedule-json', 'stim', 'circuit-json'):
        raise ValueError('Unsupported export format')
    state, row = resolve(run, circuit_id)
    c = Circuit.from_dict(row['circuit'])
    from ..circuits.identity import physical_identity
    exact_identity=digest(c.to_dict())
    if circuit_id not in (exact_identity,physical_identity(c)):
        raise ValueError('Optimizer circuit identity mismatch')
    candidate_id=circuit_id
    circuit_id=exact_identity
    p = noise_p if noise_p is not None else state.get('config', {}).get('p', .001)
    out = Path(output)
    if out.exists():
        raise FileExistsError('Export destination already exists; choose a new path')
    out.parent.mkdir(parents=True, exist_ok=True)
    if format == 'schedule-json':
        save(out, schedule_payload(c)); return dict(output=str(out), format=format, circuit=circuit_id)
    if format == 'circuit-json':
        save(out, c.to_dict()); return dict(output=str(out), format=format, circuit=circuit_id)
    if format == 'stim':
        out.write_text(stim_text(c,p), encoding='utf-8')
        save(str(out)+'.identity.json', dict(circuit=circuit_id, circuit_payload=c.to_dict(), exporter_source=source_identity(), evidence_source=state['source'], fault_model=MODEL, scope=SCOPE, noise_probability=p, qualification='Logical-Z-sector Stim experiment with ideal boundaries; see circuit payload for the complete certified task'))
        return dict(output=str(out), format=format, circuit=circuit_id)
    out.mkdir()
    certificate = row.get('certify')
    if certificate and (certificate.get('circuit') != circuit_id or certificate.get('source') != state['source']):
        raise ValueError('Certificate/optimizer binding mismatch')
    checkpoint = Path(run)/'checkpoint.json' if Path(run).is_dir() else Path(run)
    task_records=[]
    for task_id, answer in state.get('tasks',{}).items():
        task_file=checkpoint.parent/'tasks'/(task_id+'.json')
        if not task_file.exists():
            raise ValueError('Missing task record required for reproducible export: '+str(task_file))
        packet=json.loads(task_file.read_text(encoding='utf-8'))
        task=packet.get('task',packet)
        if task.get('circuit')==c.to_dict():task_records.append(dict(request=task,answer=answer))
    if state.get('schema')=='sqlite-population-1':
        from ..optimization.store import PopulationStore
        with PopulationStore(checkpoint.parent/state['population_db'],readonly=True) as db:
            task_records=[dict(request=x['task'],answer=x['answer']) for x in db.packets(candidate_id) if x['task']['circuit']==c.to_dict()]
    packets = {'tasks.json':task_records, 'input_code.json':state['code'], 'circuit.json':c.to_dict(), 'schedule.json':schedule_payload(c),
               'resources.json':resources(c), 'certificate.json':certificate,
               'evidence.json':dict(row=row, optimizer_source=state['source'], optimizer_config=state.get('config'), noise_probability=p,
                                    noise_model=MODEL, scope=SCOPE, decoder=state.get('config',{}).get('decoder'),
                                    optimizer_seed=state.get('config',{}).get('seed'), source_records=source_records(Path(__file__).resolve().parents[1]),
                                    exporter_source=source_identity(), qualification='Recorded certificate status must be independently replayed; UNKNOWN is not a positive certificate')}
    for name, value in packets.items():
        save(out/name,value)
    (out/'circuit.stim').write_text(stim_text(c,p),encoding='utf-8')
    (out/'REPRODUCE.txt').write_text('Install the matching FTQEC scientific source and run:\nftqec verify-export "'+str(out.resolve())+'" --proof-work 20000000\nThe verifier reconstructs schedule rows, checks all bindings and replays proof evidence. Ideal initial/final operations in circuit.stim are simulation boundaries, not certified physical memory. Proof recipes are embedded in certificate.json; independent replay reconstructs physical inventories and proof tables.\n',encoding='utf-8')
    (out/'schedule.txt').write_text('\n'.join('Layer '+str(g['start'])+': '+'; '.join(str(i)+':'+c.operations[i].gate+'('+','.join(map(str,c.operations[i].qubits))+')' for i in g['operations']) for g in packets['schedule.json']['parallel_groups'])+'\n',encoding='utf-8')
    import hashlib
    members={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    save(out/'manifest.json',dict(schema=VERSION,circuit=circuit_id,candidate_id=candidate_id,schedule=packets['schedule.json']['schedule_identity'],evidence_source=state['source'],exporter_source=source_identity(),fault_model=MODEL,scope=SCOPE,members=members))
    return dict(output=str(out),format=format,circuit=circuit_id,schedule=packets['schedule.json']['schedule_identity'],recorded_certification=certificate.get('status') if certificate else 'NOT_RUN')


def list_results(run,all_rows=False):
    path=Path(run);path=path/'checkpoint.json' if path.is_dir() else path
    state=json.loads(path.read_text(encoding='utf-8'))
    if state.get('schema')=='sqlite-population-1':
        from ..optimization.store import PopulationStore,skyline
        with PopulationStore(path.parent/state['population_db'],readonly=True) as db:
            state=db.get_meta('state');summaries=db.summaries(certified=not all_rows)
            chosen=list(summaries) if all_rows else skyline(summaries)
            rows=[db.get(r['id']) for r in chosen]
    else:rows=state['rows']
    if not all_rows:
        from ..optimization.selection import pareto
        rows=pareto([r for r in rows if r.get('certify',{}).get('status')=='CERTIFIED'])
    return dict(source=state['source'],run=str(path.parent),results=[dict(circuit_id=r['id'],exact_circuit_identity=digest(r['circuit']),resources=r['resources'],recorded_certification=r.get('certify',{}).get('status','NOT_RUN'),independent_verification_recorded=r.get('certify',{}).get('independent',{}).get('verified',False)) for r in rows],qualification='Recorded optimizer results; use verify-export for fresh independent replay')
