"""Prospectively frozen, local general-certification and scheduling experiments.

Every stage persists raw outputs. Existing completed stages are reused only with
matching source/protocol identity. Finite trial populations are not convergence
claims; public optimize remains anytime unless the caller specifies generations.
"""
import json,time,sys,subprocess,hashlib
from pathlib import Path
from dataclasses import replace
import psutil
from ftqec.results.artifacts import save,digest,source_identity,source_records
from ftqec.execution.runtime import runtime_identity
from ftqec.execution.tasks import Task,batch
from ftqec.codes.input import load
from ftqec.architectures.references import rotated_surface
from ftqec.architectures.population import Genome,compile
from ftqec.architectures.synthesis import generate
from ftqec.optimization.engine import Config,optimize
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.circuits.model import Circuit
from ftqec.certification.inventory import forward
from ftqec.certification.exact import verify

source=source_identity();root=Path('results/general_competitive/final')/source
root.mkdir(parents=True,exist_ok=True)
protocol=dict(source=source,runtime=runtime_identity(),driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seeds=[0,8,16],distance_ladder=list(range(1,11)),families=['surface','steane','shor9','color_small','shor_product4_repair'],cross_family_trials=dict(population=4,generations=3,finalists=4,seed=0),methods=['graph','mitm','dp','sat'],method_controls=[3,5,10],method_work=2000000,workers=2,memory_mb=512,cpu_seconds=300,active_wall_seconds=600,optimizer=dict(population=2,generations=1,finalists=2,initial_shots=128,further_shots=512,strategy='hybrid'),qualification='Finite prospective trials; no global optimality, convergence or held-out generalization claim. Prior development surface and Shor mechanisms are disclosed.',success=dict(nongraphlike='raw hyperedges and independently verified general target>=5 proof',target10='code-only compiled and independently verified Q<=199,D<=12'),ler=dict(p=[.001,.01],shots=20480,seeds=[3101,3102],decoders=['matching','one_mechanism_lookup']),scope='ideal initial and final syndrome extraction; prepared logical Z simulation task; explicit operation noise only')
pfile=root/'protocol.json'
if pfile.exists():assert json.loads(pfile.read_text())==protocol,'Protocol changed; preserve old epoch'
else:save(pfile,protocol)

def run_tasks(name,items):
    path=root/(name+'.json')
    if path.exists():
        packet=json.loads(path.read_text());assert packet['tasks']==[t.to_dict() for t in items];return packet['answers']
    start=time.perf_counter();cpu=time.process_time()
    answers=batch(items,workers=2,memory_mb=512)
    save(path,dict(source=source,protocol=digest(protocol),tasks=[t.to_dict() for t in items],answers=answers,controller_cpu=time.process_time()-cpu,elapsed_wall=time.perf_counter()-start,peak_controller_working_set=psutil.Process().memory_info().peak_wset))
    print('SAVED',name,[(a['result'].get('status'),a['result'].get('lower_bound')) for a in answers],flush=True)
    return answers

def task(c,tier,target,method='auto',shots=0,seed=0,p=.001,decoder='auto'):
    check(c)
    return Task(c.to_dict(),tier,digest(c.code.to_dict()),dict(p=p),decoder,seed,source,dict(target=target,work=2000000,proof_method=method,shots=shots,max_decoder_faults=100000,memory_mb=512,cpu_seconds=300,wall_seconds=600,proof_directory=str((root/'proofs'/digest(c.to_dict())/method).resolve())))

def campaign(name,inp,target,seed,cross_family=False):
    out=root/'optimizer'/name
    cfg=Config(population=4 if cross_family else 2,generations=3 if cross_family else 1,workers=2,seed=seed,target=target,strategy='hybrid',proof_work=2000000,finalists=4 if cross_family else 2)
    state=optimize(inp.to_dict(),out,cfg)
    if state['status']=='RESOURCE_SAFETY_INTERVENTION':raise MemoryError(state.get('resource_reason'))
    print('OPTIMIZER',name,[(r['resources']['Q'],r['resources']['D'],r.get('certify',{}).get('status')) for r in state['rows']],flush=True)
    return state

if __name__=='__main__':
    states={}
    for target in range(1,11):
        inp,_=rotated_surface(max(2,target),1)
        save(root/'inputs'/f'surface{target}.json',inp.to_dict())
        states[target]=campaign(f'surface{target}_seed0',inp,target,0)
    for seed in (8,16):
        inp,_=rotated_surface(10,1);campaign(f'surface10_seed{seed}',inp,10,seed)
    for name in ('steane','shor9','color_small'):
        inp=load(json.loads(Path('examples',name+'.json').read_text()))
        campaign(name,inp,3,0,cross_family=True)
    for target in (3,5,10):
        rows=[r for r in states[target]['rows'] if r.get('certify',{}).get('status')=='CERTIFIED']
        if not rows:continue
        row=min(rows,key=lambda r:r['resources']['QD']);c=Circuit.from_dict(row['circuit'])
        run_tasks(f'methods/target{target}',[task(c,'certify',target,method=m) for m in protocol['methods']])
        inv=forward(c)
        save(root/'methods'/f'inventory{target}.json',dict(circuit=digest(c.to_dict()),inventory_hash=inv.hash,alternatives=inv.count,raw_hyperedges=sum(d.bit_count()>2 for _,_,d,l,_ in inv.rows())))
        inv.close()
    # Replay the old Shor mechanism under the new source, then generic flag repairs.
    row=json.loads(Path('results/autonomous/posthoc_shor_diagnosis/candidate.json').read_text())
    parent=Genome.from_dict(row['genome']);inp=load(row['circuit']['code'])
    campaign('shor_product4',inp,4,0,cross_family=True)
    variants=[('original',parent)]+[(f'{style}_{reverse}',replace(parent,family='flagged',flag_style=style,reverse_flags=reverse,schedule='critical_path')) for style in ('single','adjacent','nested') for reverse in (False,True)]
    for name,g in variants:
        c=compile(inp,g);run_tasks('shor_repair/'+name,[task(c,'certify',4,method='mitm')])
    # Low-qubit architecture remains independently generated from the code.
    inp,reference=rotated_surface(10,1);g,_=generate(inp,4,10)
    low=compile(inp,replace(g,rounds=1,shared=True,ancilla_slots=1,schedule='axis_grouped'))
    run_tasks('target10/low_qubit',[task(low,'certify',10)])
    run_tasks('target10/reference',[task(reference,'certify',10)])
    # Matched physical noise, decoder and task; no superiority claim from zero counts.
    best=min([r for r in states[10]['rows'] if r.get('certify',{}).get('status')=='CERTIFIED'],key=lambda r:r['resources']['QD'])
    chosen=[('discovered',Circuit.from_dict(best['circuit'])),('low_qubit',low),('reference',reference)]
    for name,c in chosen:
        for p in protocol['ler']['p']:
            run_tasks(f'ler/{name}_{p}',[task(c,'simulation',10,shots=20480,seed=seed,p=p,decoder=decoder) for decoder in protocol['ler']['decoders'] for seed in protocol['ler']['seeds']])
    # Independent positive proof replay after all runs, plus resource recomputation.
    receipts=[]
    for path in sorted(root.rglob('*.json')):
        if path.name=='checkpoint.json':
            packet=json.loads(path.read_text())
            for row in packet.get('rows',[]):
                if row.get('certify',{}).get('status') in ('CERTIFIED','INVALID'):
                    c=Circuit.from_dict(row['circuit']);v=verify(c,row['certify'],2000000)
                    receipts.append(dict(path=str(path),id=row['id'],verified=v,resource_match=all(row['resources'][k]==v for k,v in resources(c).items())))
        elif path.parent.name in ('methods','shor_repair','target10') and path.name!='audit.json':
            packet=json.loads(path.read_text())
            for t,a in zip(packet.get('tasks',[]),packet.get('answers',[])):
                cert=a['result']
                if cert.get('status') in ('CERTIFIED','INVALID'):
                    c=Circuit.from_dict(t['circuit']);receipts.append(dict(path=str(path),verified=verify(c,cert,2000000),resources=resources(c)))
    save(root/'audit.json',dict(source=source,receipts=receipts,all_verified=all(r['verified']['verified'] for r in receipts)))
    save(root/'complete.json',dict(source=source,protocol=digest(protocol),completed=time.time(),qualification=protocol['qualification']))
    print('COMPLETE',root,flush=True)
