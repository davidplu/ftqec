"""Repeated-memory population driver using the shared supervised scientific workers."""
import json,time
from pathlib import Path
from .selection import pareto
from ..codes.two_block import parse
from ..execution.tasks import Task,batch
from ..execution.locking import RunLock
from ..results.artifacts import save,digest,source_identity,save_checkpoint
from ..circuits.identity import physical_identity
from ..circuits.model import Circuit


def optimize(data,output,rounds,target,population=12,generations=None,workers=1,seed=0,work=200000,shots=128,no_time_limits=False,idles=False,decoder='auto',proof_method='auto',p=.001,strategy='hybrid',promotion=8):
    if any(type(x) is not int or x<1 for x in (rounds,target,population,workers,work,shots,promotion)):raise ValueError('Positive experiment parameters required')
    if generations is not None and (type(generations) is not int or generations<1):raise ValueError('Positive generations')
    if not 0<=p<=1:raise ValueError('Noise probability must be in [0,1]')
    if decoder not in ('auto','matching','one_mechanism_lookup','bposd'):raise ValueError('Unsupported decoder')
    parsed=parse(data);root=Path(output);root.mkdir(parents=True,exist_ok=True)
    source=source_identity();config=dict(rounds=rounds,target=target,population=population,workers=workers,seed=seed,work=work,shots=shots,no_time_limits=no_time_limits,idles=idles,p=p,decoder=decoder,proof_method=proof_method,strategy=strategy,promotion=promotion)
    identity=digest(dict(code=data,config=config,source=source));began=time.perf_counter();cpu=time.process_time()
    with RunLock(root/'run.lock'):
        if (root/'checkpoint.json').exists():
            state=json.loads((root/'checkpoint.json').read_text())
            if state['identity']!=identity:raise ValueError('Resume identity mismatch')
            if state.get('checkpoint_digest')!=digest({k:v for k,v in state.items() if k!='checkpoint_digest'}):raise ValueError('Checkpoint integrity mismatch')
            for tid,answer in state['tasks'].items():
                packet=json.loads((root/'tasks'/(tid+'.json')).read_text())
                if packet['answer']!=answer or Task(**packet['task']).identity!=tid:raise ValueError('Cached task integrity mismatch')
        else:state=dict(identity=identity,source=source,code=parsed.input.to_dict(),config=config,generation=0,rows=[],tasks={},proposals=[],sessions=[])
        def persist():
            save_checkpoint(root/'checkpoint.json',state)
        def evaluate(requests,tier,shot_count=None):
            state['stage']=tier;persist()
            tasks=[]
            for key,circuit in requests:
                task=Task(circuit,tier,parsed.input.identity,dict(p=p),decoder,seed+int(digest(key)[:8],16)+(shot_count or 0),source,dict(target=target,shots=shot_count or shots,work=work,proof_method=proof_method,memory_mb=512,cpu_seconds=None if no_time_limits else 300,wall_seconds=None if no_time_limits else 600,max_decoder_faults=100000,cancel_file=str((root/'cancel.json').resolve()),proof_directory=str((root/'proofs'/key/tier).resolve())))
                tasks.append(task)
            todo=list({t.identity:t for t in tasks if t.identity not in state['tasks']}.values())
            def received(t,answer):
                family=t.circuit.get('experiment',{}).get('family',t.circuit.get('genome',{}).get('family','unknown'))
                state.setdefault('evaluation_costs',{}).setdefault(family,{}).setdefault(tier,[]).append(dict(cpu=answer['cpu'],wall=answer['wall'],task=t.identity))
                state['tasks'][t.identity]=answer;save(root/'tasks'/(t.identity+'.json'),dict(task=t.to_dict(),answer=answer));persist()
            if todo:batch(todo,workers,memory_mb=512,on_result=received)
            return [state['tasks'][t.identity]['result'] for t in tasks]
        try:
            while generations is None or state['generation']<generations:
                if (root/'cancel.json').exists():state['status']='CANCELLED';break
                g=state['generation']
                pending=state.get('pending')
                if pending is None:
                    from .memory_proposals import propose
                    proposals=propose(parsed,state['rows'],seed,g,population,target,strategy)
                    state['pending']=proposals;state['proposals'].extend(proposals);persist()
                else:proposals=pending
                results=evaluate([(p['key'],dict(code_input=data,genome=p['genome'],rounds=rounds,idles=idles)) for p in proposals],'construct_2bga')
                new=[]
                for proposal,result in zip(proposals,results):
                    proposal['construction_status']=result['status'];proposal['construction_reason']=result.get('reason')
                    if result['status']!='STRUCTURALLY_VALID':continue
                    for circuit,metrics in zip(result['circuits'],result['resources']):
                        cid=physical_identity(Circuit.from_dict(circuit));existing=next((r for r in state['rows'] if r['id']==cid),None)
                        row=existing or dict(id=cid,circuit=circuit,resources=metrics,genome=proposal['genome'],parent=proposal['parent'],single=result['single'],generation=g)
                        if existing is None:state['rows'].append(row)
                        if row not in new:new.append(row)
                persist()
                for row,result in zip(new,evaluate([(r['id'],r['circuit']) for r in new],'screen')):row['screen']=result
                eligible=[r for r in new if r['screen']['status']!='FAULT_INVALID' and r.get('certify',{}).get('status')!='INVALID'];persist()
                for row,result in zip(eligible,evaluate([(r['id'],r['circuit']) for r in eligible],'simulation')):row['simulation']=result
                # Both Pauli sectors of each selected architecture are proved independently.
                groups={digest(r['genome']):[] for r in eligible}
                for row in eligible:groups[digest(row['genome'])].append(row)
                from .memory_proposals import promote
                chosen=promote(groups,promotion,strategy,seed+g,state.get('evaluation_costs'))
                state.setdefault('promotion_history',[]).append(dict(generation=g,strategy=strategy,selected=[r['id'] for group in chosen for r in group]))
                finalists=[r for group in chosen for r in group];persist()
                resample=[r for r in finalists if 'rate' in r.get('simulation',{})]
                for row,result in zip(resample,evaluate([(r['id'],r['circuit']) for r in resample],'simulation',4*shots)):
                    row['simulation_batches']=[row['simulation'],result]
                    if 'rate' in result:row['simulation']=result
                for row,result in zip(finalists,evaluate([(r['id'],r['circuit']) for r in finalists],'certify')):row['certify']=result
                for row,result in zip(finalists,evaluate([(r['id']+'-single',r['single']) for r in finalists],'certify')):row['single_certify']=result
                if (root/'cancel.json').exists():state['status']='CANCELLED';break
                state['generation']+=1;state.pop('pending',None);state['status']='RUNNING';persist()
            else:state['status']='REQUESTED_GENERATIONS_COMPLETED'
        except MemoryError as exc:state.update(status='RESOURCE_SAFETY_INTERVENTION',reason=str(exc))
        except Exception as exc:
            state.update(status='INTERRUPTED_ERROR',reason=type(exc).__name__+': '+str(exc));raise
        finally:
            state['sessions'].append(dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-began));persist()
            positives=[r for r in state['rows'] if r.get('certify',{}).get('status')=='CERTIFIED']
            sectors={}
            for r in positives:sectors.setdefault(digest(r['genome']),set()).add(r['circuit']['experiment']['memory_basis'])
            paired=[r for r in positives if sectors[digest(r['genome'])]=={'X','Z'}]
            save(root/'frontier.json',dict(sector_certified=[r['id'] for r in positives],both_sectors_certified=[r['id'] for r in paired],pareto={basis:[r['id'] for r in pareto([r for r in paired if r['circuit']['experiment']['memory_basis']==basis])] for basis in ('X','Z')}))
            stages={'noiselessly_valid':state['rows'],'simulated':[r for r in state['rows'] if 'rate' in r.get('simulation',{})],'independently_certified_paired':paired}
            save(root/'stage-frontiers.json',dict(generated_proposals=[p['key'] for p in state['proposals']],generated_resource_frontier='not assigned before physical compilation and structural validation',stages={stage:{basis:[r['id'] for r in pareto([r for r in rows if r['circuit']['experiment']['memory_basis']==basis])] for basis in ('X','Z')} for stage,rows in stages.items()}))
            save(root/'compute.json',dict(worker_cpu=sum(a['cpu'] for a in state['tasks'].values()),worker_wall_sum=sum(a['wall'] for a in state['tasks'].values()),peak_worker_rss=max((a.get('peak_rss',a['rss']) for a in state['tasks'].values()),default=0),controller_sessions=state['sessions']))
        return state
