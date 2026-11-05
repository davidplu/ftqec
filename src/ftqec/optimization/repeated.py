"""Repeated-memory population driver using the shared supervised scientific workers."""
import json,random,time
from pathlib import Path
from .selection import pareto
from ..codes.two_block import parse
from ..execution.tasks import Task,batch
from ..execution.locking import RunLock
from ..results.artifacts import save,digest,source_identity
from ..circuits.identity import physical_identity
from ..circuits.model import Circuit


def optimize(data,output,rounds,target,population=12,generations=None,workers=1,seed=0,work=200000,shots=128,no_time_limits=False,idles=False,decoder='auto',proof_method='auto',p=.001):
    if any(type(x) is not int or x<1 for x in (rounds,target,population,workers,work,shots)):raise ValueError('Positive experiment parameters required')
    if generations is not None and (type(generations) is not int or generations<1):raise ValueError('Positive generations')
    if not 0<=p<=1:raise ValueError('Noise probability must be in [0,1]')
    if decoder not in ('auto','matching','one_mechanism_lookup'):raise ValueError('Unsupported decoder')
    parsed=parse(data);root=Path(output);root.mkdir(parents=True,exist_ok=True)
    source=source_identity();config=dict(rounds=rounds,target=target,population=population,workers=workers,seed=seed,work=work,shots=shots,no_time_limits=no_time_limits,idles=idles,p=p,decoder=decoder,proof_method=proof_method)
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
            state['checkpoint_digest']=digest({k:v for k,v in state.items() if k!='checkpoint_digest'});save(root/'checkpoint.json',state)
        def evaluate(requests,tier,shot_count=None):
            state['stage']=tier;persist()
            tasks=[]
            for key,circuit in requests:
                task=Task(circuit,tier,parsed.input.identity,dict(p=p),decoder,seed+int(digest(key)[:8],16)+(shot_count or 0),source,dict(target=target,shots=shot_count or shots,work=work,proof_method=proof_method,memory_mb=512,cpu_seconds=None if no_time_limits else 300,wall_seconds=None if no_time_limits else 600,max_decoder_faults=100000,cancel_file=str((root/'cancel.json').resolve()),proof_directory=str((root/'proofs'/key/tier).resolve())))
                tasks.append(task)
            todo=list({t.identity:t for t in tasks if t.identity not in state['tasks']}.values())
            def received(t,answer):
                state['tasks'][t.identity]=answer;save(root/'tasks'/(t.identity+'.json'),dict(task=t.to_dict(),answer=answer));persist()
            if todo:batch(todo,workers,memory_mb=512,on_result=received)
            return [state['tasks'][t.identity]['result'] for t in tasks]
        try:
            while generations is None or state['generation']<generations:
                if (root/'cancel.json').exists():state['status']='CANCELLED';break
                g=state['generation'];rng=random.Random(seed+g*1000003)
                pending=state.get('pending')
                if pending is None:
                    proposals=[];parents=state['rows']
                    for i in range(population):
                        order=[['X',j] for j in range(len(parsed.x_terms))]+[['Z',j] for j in range(len(parsed.z_terms))]
                        parent=None;mutation='random_term_order';family='group_term'
                        genome=dict(family=family,order=order)
                        if parents and i%2:
                            chosen=parents[rng.randrange(len(parents))];parent=chosen['id'];genome=dict(chosen['genome']);order=[x[:] for x in chosen['genome']['order']];mutation='term_swap'
                            siblings=[r for r in parents if r['genome']==chosen['genome']]
                            witness=next((w for r in siblings if (w:=r.get('certify',{}).get('witness') or r.get('screen',{}).get('witness'))),None)
                            positions=[]
                            if witness:
                                for f in witness['faults']:
                                    pos=f.get('interaction_position');ch=f.get('check')
                                    if pos is not None and ch is not None:positions.extend(j for j,(axis,t) in enumerate(order) if t==pos and axis==('X' if ch<parsed.checks.n//2 else 'Z'))
                            a=rng.choice(positions) if positions else rng.randrange(len(order));b=rng.choice([j for j in range(len(order)) if order[j][0]==order[a][0]]);order[a],order[b]=order[b],order[a]
                            if positions:mutation='witness_term_swap'
                            if witness and i%4==3:
                                genome['family']=rng.choice(('flagged','verified_cat'));genome['flag_style']='adjacent';genome['verification_rounds']=max(1,(target-1)//2);mutation+='_'+genome['family']
                        elif g or i:
                            if i%8==3:rng.shuffle(order)
                            else:
                                xs=[x for x in order if x[0]=='X'];zs=[x for x in order if x[0]=='Z'];rng.shuffle(xs);rng.shuffle(zs);order=xs+zs if i%2==0 else zs+xs
                                mutation='structured_axis_order'
                            if i%8>=4:
                                genome.update(family=('flagged','cat','verified_cat','bare')[i%8-4],flag_style='adjacent',verification_rounds=max(1,(target-1)//2),schedule=rng.choice(('critical_path','conflict_color','resource')),ancilla_slots=parsed.checks.n if i%8!=7 else max(1,parsed.checks.n//2))
                                mutation='generic_gadget_schedule_allocation'
                        genome['order']=order;key=digest(genome);proposals.append(dict(key=key,genome=genome,parent=parent,mutation=mutation))
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
                eligible=[r for r in new if r['screen']['status']!='FAULT_INVALID'];persist()
                for row,result in zip(eligible,evaluate([(r['id'],r['circuit']) for r in eligible],'simulation')):row['simulation']=result
                # Both Pauli sectors of each selected architecture are proved independently.
                groups={digest(r['genome']):[] for r in eligible}
                for row in eligible:groups[digest(row['genome'])].append(row)
                ranked=sorted(groups.values(),key=lambda rows:(max(r['resources']['D'] for r in rows),max(r['resources']['QD'] for r in rows)))
                chosen=ranked[:2]
                # Keep a repair-family finalist even when its extra protection costs depth.
                repair=next((rows for rows in ranked if rows[0]['genome'].get('family') in ('flagged','verified_cat')),None)
                if repair is not None and repair not in chosen:chosen.append(repair)
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
        finally:
            state['sessions'].append(dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-began));persist()
            positives=[r for r in state['rows'] if r.get('certify',{}).get('status')=='CERTIFIED']
            sectors={}
            for r in positives:sectors.setdefault(digest(r['genome']),set()).add(r['circuit']['experiment']['memory_basis'])
            paired=[r for r in positives if sectors[digest(r['genome'])]=={'X','Z'}]
            save(root/'frontier.json',dict(sector_certified=[r['id'] for r in positives],both_sectors_certified=[r['id'] for r in paired],pareto={basis:[r['id'] for r in pareto([r for r in paired if r['circuit']['experiment']['memory_basis']==basis])] for basis in ('X','Z')}))
            save(root/'compute.json',dict(worker_cpu=sum(a['cpu'] for a in state['tasks'].values()),worker_wall_sum=sum(a['wall'] for a in state['tasks'].values()),peak_worker_rss=max((a.get('peak_rss',a['rss']) for a in state['tasks'].values()),default=0),controller_sessions=state['sessions']))
        return state
