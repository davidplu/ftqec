"""Disk-backed paired-memory population search using the shared FTQEC engines."""
import random,time
from pathlib import Path
from .store import PopulationStore,skyline
from ..architectures.group_search import crossing_masks,valid_order
from ..codes.two_block import parse
from ..circuits.model import Circuit
from ..circuits.identity import physical_identity
from ..execution.tasks import Task,batch
from ..execution.locking import RunLock
from ..results.artifacts import save,digest,source_identity

POLICIES=('random','structured','witness','multifidelity','hybrid','costaware','costhybrid')


def proposal(code,index,seed,policy,parents=()):
    if policy not in POLICIES:raise ValueError('Unsupported Phase 3 policy')
    rng=random.Random(seed+index*1000003);masks=crossing_masks(code)
    terms=[('X',i) for i in range(len(code.x_terms))]+[('Z',i) for i in range(len(code.z_terms))]
    parent=None;diagnosis=None;mutation='code_derived_order';order=list(terms)
    if parents and policy in ('witness','hybrid','costhybrid') and index%2:
        choices=[r for r in parents if r.get('certify',{}).get('witness') or r.get('screen',{}).get('witness')]
        if choices:
            parent=rng.choice(choices);order=list(map(tuple,parent['genome']['order']))
            witness=parent.get('certify',{}).get('witness') or parent.get('screen',{}).get('witness')
            axes=[];checks=[]
            for f in witness['faults']:
                try:
                    op=parent['circuit']['operations'][int(str(f['location']).split(':')[-1])]
                    ch=op.get('check')
                    if ch is not None:
                        checks.append(ch);axes.extend(set(parent['circuit']['code']['generators'][ch])-{'I'})
                except (ValueError,KeyError,IndexError):continue
            axis=rng.choice(axes or ['X','Z']);ids=[i for i,x in enumerate(order) if x[0]==axis]
            if len(ids)>1:
                a,b=rng.sample(ids,2);order[a],order[b]=order[b],order[a]
            diagnosis=dict(witness=digest(witness),checks=sorted(set(checks)),axis=axis)
            mutation='witness_axis_interaction_swap'
    attempts=0
    if parent is None or not valid_order(order,masks):
        if parent is not None:
            mutation='random_order_after_incompatible_witness_swap'
        while True:
            order=list(terms);rng.shuffle(order);attempts+=1
            if valid_order(order,masks):break
            if attempts>=100000:
                # A code-derived serial order is a valid recovery proposal,
                # never a successful reference seed.
                order=list(terms);break
    n=code.checks.n;budget=n+max(1,round(n*(1-(index%6)/6)))
    family='group_term' if index%3==0 else 'group_pool'
    checks=list(range(len(code.checks.generators)))
    if index%4==1:rng.shuffle(checks)
    genome=dict(family=family,order=[list(x) for x in order],ancilla_slots=budget-n,
                checks=checks,check_basis='independent' if index%11==7 else 'redundant')
    # Retain existing flag/cat vocabulary as exploration alternatives.
    if index%20 in (17,18,19):
        genome['family']={17:'flagged',18:'cat',19:'verified_cat'}[index%20]
        width=max(g.weight for g in code.checks.generators)
        genome.update(ancilla_slots=max(1,(budget-n)//(width+1)),flag_style='adjacent',verification_rounds=2,schedule='critical_path')
    return dict(key=digest(genome),genome=genome,parent=parent['id'] if parent else None,
                mutation=mutation,diagnosis=diagnosis,raw_order_draws=attempts,requested_qubit_budget=budget)


def optimize(data,output,rounds=6,target=6,candidate_goal=None,workers=1,seed=1,
             policy='hybrid',proof_method='auto',work=50000000,window=10,promotions=1,
             shots=32,decoder='bposd',noise=.001,experiment_cpu=None):
    if candidate_goal is not None and candidate_goal<1:raise ValueError('Positive candidate goal')
    if min(rounds,target,workers,window,promotions,shots,work)<1:raise ValueError('Positive search settings')
    code=parse(data);root=Path(output);root.mkdir(parents=True,exist_ok=True)
    source=source_identity();config=dict(rounds=rounds,target=target,seed=seed,policy=policy,proof_method=proof_method,work=work,window=window,promotions=promotions,shots=shots,decoder=decoder,noise=noise)
    identity=digest(dict(code=data,source=source,config=config))
    start=time.perf_counter();cpu=time.process_time()
    with RunLock(root/'run.lock'),PopulationStore(root/'population.sqlite',identity) as db:
        state=db.get_meta('state',dict(source=source,code=code.input.to_dict(),config=config,index=0,sessions=[],status='RUNNING'))
        def persist():
            db.set_meta('state',state)
            save(root/'checkpoint.json',dict(schema='sqlite-population-1',population_db='population.sqlite',source=source,identity=identity,index=state['index'],status=state['status']))
        def evaluate(requests,tier):
            tasks=[]
            for key,payload in requests:
                task=Task(payload,tier,code.input.identity,dict(p=noise),decoder,seed+int(digest(key)[:8],16),source,
                    dict(target=target,shots=shots,work=work,proof_method=proof_method,memory_mb=512,cpu_seconds=None,wall_seconds=None,max_decoder_faults=200000,
                         cancel_file=str((root/'cancel.json').resolve()),proof_directory=str((root/'proofs'/key/tier).resolve())))
                db.queue(task,key);tasks.append(task)
            todo=[t for t in tasks if db.answer(t.identity) is None]
            if todo:batch(todo,workers,memory_mb=512,on_result=lambda t,a:db.complete(t.identity,a))
            return [db.answer(t.identity)['result'] for t in tasks]
        def publish():
            summaries=list(db.summaries());pairs={}
            for s in summaries:
                if s['certify']['status']!='CERTIFIED':continue
                row=db.get(s['id']);key=row['pair'];pairs.setdefault(key,[]).append(row)
            complete=[rs for rs in pairs.values() if {r['circuit']['experiment']['memory_basis'] for r in rs}=={'X','Z'}]
            aggregate=[]
            for rs in complete:
                metrics={k:max(r['resources'][k] for r in rs) for k in ('Q','D','QD','two_q_gates')}
                aggregate.append(dict(id=rs[0]['pair'],resources=metrics,sectors={r['circuit']['experiment']['memory_basis']:r['id'] for r in rs}))
            save(root/'frontier.json',dict(paired=aggregate,pareto=skyline(aggregate)))
            save(root/'compute.json',dict(tiers=db.totals(),worker_cpu=db.worker_cpu(),controller_sessions=state['sessions']))
            save(root/'summary.json',dict(status=state['status'],proposed=state['index'],distinct_physical=db.count(),paired_certified=len(complete),
                 certified=sum(s['certify']['status']=='CERTIFIED' for s in summaries),invalid=sum(s['certify']['status']=='INVALID' or s['screen']['status']=='FAULT_INVALID' for s in summaries),
                 unknown=sum(s['certify']['status']=='UNKNOWN' for s in summaries),source=source))
        try:
            persist()
            while candidate_goal is None or state['index']<candidate_goal:
                if (root/'cancel.json').exists():state['status']='CANCELLED';break
                spent=db.worker_cpu()+sum(s['cpu'] for s in state['sessions'])+time.process_time()-cpu
                if experiment_cpu is not None and spent>=experiment_cpu:
                    state['status']='EXPERIMENT_CHECKPOINT_REACHED';break
                count=window if candidate_goal is None else min(window,candidate_goal-state['index'])
                if 'pending' not in state:
                    parents=[db.get(i) for i in db.parent_ids(8,seed+state['index'])]
                    proposals=[proposal(code,i,seed,policy,parents) for i in range(state['index'],state['index']+count)]
                    for offset,p in enumerate(proposals):db.event('proposal',dict(index=state['index']+offset,**p))
                    state['pending']=proposals;persist()
                proposals=state['pending'];count=len(proposals)
                built=evaluate([(p['key'],dict(code_input=data,rounds=rounds,genome=p['genome'])) for p in proposals],'construct_2bga')
                new=[]
                for p,result in zip(proposals,built):
                    if result['status']!='STRUCTURALLY_VALID':db.event('construction_outcome',dict(proposal=p['key'],result=result));continue
                    for c,metrics in zip(result['circuits'],result['resources']):
                        physical=physical_identity(Circuit.from_dict(c));cid=digest(c)
                        duplicate=db.db.execute('SELECT id FROM structures WHERE timed_structure=?',(physical,)).fetchone()
                        if duplicate:
                            existing=db.get(duplicate[0])
                            if existing['pair']==p['key']:new.append(existing)
                            else:db.event('duplicate',dict(proposal=p['key'],existing=duplicate[0]))
                            continue
                        row=dict(id=cid,circuit=c,genome=p['genome'],generation=state['index']//window,pair=p['key'],parent=p['parent'],diagnosis=p['diagnosis'],resources=metrics,diversity=dict(timed_structure=physical))
                        from ..scheduling.scheduler import schedule
                        circuit=Circuit.from_dict(c);sched=schedule(circuit)
                        row['additional_resources']=dict(ancillas=circuit.num_qubits-circuit.code.n,
                            two_qubit_gate_depth=len({sched.starts[i] for i,o in enumerate(circuit.operations) if len(o.qubits)==2 and o.gate!='BARRIER'}))
                        db.put(row);new.append(row)
                for row,result in zip(new,evaluate([(r['id'],r['circuit']) for r in new],'screen')):row['screen']=result;db.put(row)
                groups={}
                for row in new:
                    if row['screen']['status']!='FAULT_INVALID':groups.setdefault(row['pair'],[]).append(row)
                groups=[rs for rs in groups.values() if len(rs)==2]
                # A budget stratum rotates each window to preserve low-Q alternatives.
                budget=code.checks.n+max(1,round(code.checks.n*(1-(state['index']//window)%6/6)))
                rng=random.Random(seed+state['index'])
                if policy=='random':rng.shuffle(groups)
                else:groups.sort(key=lambda rs:(abs(max(r['resources']['Q'] for r in rs)-budget),max(r['resources']['QD'] for r in rs)))
                screened_groups=groups[:promotions*(3 if policy in ('multifidelity','hybrid','costaware','costhybrid') else 1)]
                simulated=[r for rs in screened_groups for r in rs]
                for row,result in zip(simulated,evaluate([(r['id'],r['circuit']) for r in simulated],'simulation')):row['simulation']=result;db.put(row)
                if policy=='multifidelity':screened_groups.sort(key=lambda rs:(max(r['simulation'].get('confidence',[0,1])[1] for r in rs),max(r['resources']['QD'] for r in rs)))
                if policy=='witness':screened_groups.sort(key=lambda rs:not bool(rs[0]['diagnosis']))
                if policy in ('costaware','costhybrid'):
                    costs=state.get('certified_family_costs',{})
                    def cost(rs):
                        values=costs.get(rs[0]['genome']['family'],[])
                        return sum(values)/len(values) if values else float('inf')
                    screened_groups.sort(key=lambda rs:(cost(rs),abs(max(r['resources']['Q'] for r in rs)-budget),max(r['resources']['QD'] for r in rs)))
                finalists=[r for rs in screened_groups[:promotions] for r in rs]
                for row,result in zip(finalists,evaluate([(r['id'],r['circuit']) for r in finalists],'certify')):row['certify']=result;db.put(row)
                for row in finalists:
                    cert=row['certify']
                    if cert['status']=='CERTIFIED' and 'portfolio_selection' in cert:
                        state.setdefault('certified_family_costs',{}).setdefault(row['genome']['family'],[]).append(cert['portfolio_selection']['cpu'])
                state['index']+=count;state.pop('pending',None);state['status']='RUNNING';persist();publish()
                db.event('compute_checkpoint',dict(proposals=state['index'],worker_cpu=db.worker_cpu(),controller_cpu=time.process_time()-cpu))
            else:state['status']='REQUESTED_CANDIDATES_COMPLETED'
        except MemoryError as exc:state.update(status='RESOURCE_SAFETY_INTERVENTION',reason=str(exc))
        finally:
            state['sessions'].append(dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-start));persist();publish()
        return state
