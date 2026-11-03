"""Bounded-working-set population optimization using the existing scientific engines."""
import time,json,subprocess
from pathlib import Path
from dataclasses import asdict
from .store import PopulationStore,skyline
from .selection import promising,reliability_pareto
from ..codes.input import load
from ..architectures.population import sample,mutate,recombine,Genome
from ..circuits.model import Circuit
from ..circuits.identity import physical_identity
from ..execution.tasks import Task,batch
from ..execution.runtime import runtime_identity
from ..results.artifacts import digest,source_identity,save
from ..simulation.sequential import combine


def diversity(row):
    from .diversity import timed_structure
    g=row['genome'];c=row['circuit'];r=row['resources']
    # Descriptor classes are conservative near-duplicate buckets, NOT a proof of equivalence.
    descriptor={k:g.get(k) for k in ('family','shared','rounds','basis','orders','flag_style','verification_rounds','schedule','ancilla_slots','native_css')}
    coarse={k:g.get(k) for k in ('family','rounds','flag_style','verification_rounds','schedule','ancilla_slots','shared')}
    coarse['resources']={k:r[k] for k in ('Q','D','two_q_gates')}
    return dict(timed_structure=timed_structure(Circuit.from_dict(c)),structure=digest(descriptor),near_id=digest(coarse),classification='Structural descriptor bucket, not established fault equivalence',detector_count=len(c['detectors']),operations=len(c['operations']))


def select(rows,limit,seed):
    # Keep every family represented, then resource elites and rotating exploration.
    if not rows:return []
    rows=sorted(rows,key=lambda r:(r['resources']['QD'],r['id']));chosen=[]
    for family in sorted({r['genome']['family'] for r in rows}):
        family_rows=[r for r in rows if r['genome']['family']==family]
        chosen.append(family_rows[0])
    for row in sorted(rows,key=lambda r:digest([seed,r['id']]))[:max(1,limit//4)]+rows:
        if len(chosen)>=max(limit,len({r['genome']['family'] for r in rows})):break
        if row['id'] not in {r['id'] for r in chosen}:chosen.append(row)
    return chosen


def run(data,output,config):
    if config.population<1 or config.window<1 or config.promotion<1 or config.workers<1 or config.finalists<0:raise ValueError('Positive population, window, promotion and worker limits required')
    if config.strategy not in ('random','witness','multifidelity','hybrid','costaware','costhybrid'):raise ValueError('Unknown strategy')
    if config.memory_mb<1 or config.convergence_generations<1:raise ValueError('Positive execution limits required')
    if type(config.target) is not int or config.target<1 or config.initial_shots<1 or config.further_shots<1:raise ValueError('Positive target and shot limits required')
    if config.generations is not None and config.generations<1:raise ValueError('Positive generation count required')
    if config.candidate_goal is not None and config.candidate_goal<1:raise ValueError('Positive candidate goal required')
    inp=load(data);root=Path(output);root.mkdir(parents=True,exist_ok=True)
    source=source_identity();identity=digest(dict(source=source,code=inp.to_dict(),config=asdict(config),runtime=runtime_identity()))
    start=time.perf_counter();cpu=time.process_time();cache_hits=0
    with PopulationStore(root/'population.sqlite',identity) as db:
        state=db.get_meta('state')
        if state is None:
            try:commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
            except (OSError,subprocess.CalledProcessError):commit='UNCOMMITTED'
            state=dict(schema='sqlite-population-1',identity=identity,source=source,commit=commit,code=inp.to_dict(),config=asdict(config),runtime=runtime_identity(),generation=0,index=0,generated=0,sessions=[],population_db='population.sqlite',cost_observations=[])
        def persist():
            db.set_meta('state',state)
            save(root/'checkpoint.json',{k:v for k,v in state.items() if k not in ('cost_observations','pending')})
        def task(circuit,tier,seed,shots=0,cid=None):
            return Task(circuit,tier,inp.identity,dict(p=config.p),config.decoder,seed,source,dict(target=config.target,shots=shots,work=config.proof_work,proof_method=config.proof_method,memory_mb=config.memory_mb,cpu_seconds=config.task_cpu_seconds,wall_seconds=config.task_wall_seconds,max_decoder_faults=config.max_decoder_faults,cancel_file=str((root/'cancel.json').resolve()),proof_directory=str((root/'proofs'/(cid or 'construction')).resolve())))
        def dispatch(tasks,ids):
            nonlocal cache_hits
            todo=[]
            for t,cid in zip(tasks,ids):
                db.queue(t,cid)
                if db.answer(t.identity) is None:todo.append(t)
                else:cache_hits+=1
            # Both queued task identities and bounded candidate intents are durable before launch.
            if todo:
                batch(todo,config.workers,memory_mb=config.memory_mb,on_result=lambda t,a:db.complete(t.identity,a))
            return [db.answer(t.identity) for t in tasks]
        def evaluate(rows,tier,shots=0,stream=0):
            tasks=[task(r['circuit'],tier,config.seed+stream+int(r['id'][:8],16),shots,r['id']) for r in rows]
            answers=dispatch(tasks,[r['id'] for r in rows])
            for row,t,a in zip(rows,tasks,answers):
                row[tier]=a['result']
                if tier=='simulation' and 'shots' in a['result']:
                    batches=row.setdefault('simulation_batches',[])
                    if t.identity not in row.setdefault('simulation_task_ids',[]):batches.append(a['result']);row['simulation_task_ids'].append(t.identity)
                    row['simulation']=combine(batches)
                db.put(row)
                if t.identity not in {x['task'] for x in state['cost_observations']}:
                    state['cost_observations'].append(dict(task=t.identity,tier=tier,target=config.target,operations=len(row['circuit']['operations']),cpu=a['cpu'],status=a['result'].get('status','SIMULATED'),censored=a['result'].get('status')=='UNKNOWN',supported=a['result'].get('reason')!='UNSUPPORTED_PROOF_METHOD'))
                    state['cost_observations']=state['cost_observations'][-512:]
            return rows
        def archives(full=False):
            summaries=list(db.summaries());valid=[r for r in summaries if r['screen']['status']!='FAULT_INVALID' and r['certify']['status']!='INVALID']
            certified=[r for r in summaries if r['certify']['status']=='CERTIFIED']
            # Only small metadata summaries are materialized; circuits remain on disk.
            front=skyline(certified);resource=skyline(valid)
            archive=dict(resource_pareto=[r['id'] for r in resource],certified_pareto=[r['id'] for r in front],certified=[r['id'] for r in certified])
            if full:
                simulated=list(db.simulation_summaries());archive['estimated_resource_ler_pareto']=[r['id'] for r in reliability_pareto(simulated)]
                certified_ids={r['id'] for r in certified};archive['certified_circuits_estimated_ler_pareto']=[r['id'] for r in reliability_pareto([r for r in simulated if r['id'] in certified_ids])]
            save(root/'archives.json',archive)
            counts={}
            for r in summaries:counts[r['genome']['family']]=counts.get(r['genome']['family'],0)+1
            state['unique_circuits']=len(summaries);state['meaningful_circuits']=db.meaningful_count();state['diversity']=dict(families=counts,near_buckets=len({r['near_id'] for r in summaries}),qualification='Descriptor buckets are not proven scientific equivalence classes')
            return front
        persist()
        try:
            while config.generations is None or state['generation']<config.generations:
                if config.candidate_goal is not None and db.meaningful_count()>=config.candidate_goal:state['status']='REQUESTED_CANDIDATE_GOAL_COMPLETED';break
                if (root/'cancel.json').exists():state['status']='CANCELLED';break
                if state['index']>=config.population:
                    state['generation']+=1;state['index']=0
                    front=archives();shape=[list(x) for x in sorted({tuple(r['resources'][k] for k in ('Q','D','QD','two_q_gates')) for r in front})]
                    state['stagnant']=state.get('stagnant',0)+1 if shape==state.get('shape') else 0;state['shape']=shape
                    persist()
                    if config.generations is None and config.candidate_goal is None and state['stagnant']>=config.convergence_generations:state['status']='OPERATIONAL_FRONTIER_PLATEAU';break
                    continue
                plan=state.get('pending')
                if plan is None:
                    intents=[];parents=db.parent_ids(config.population,config.seed+state['generated'])
                    for i in range(state['index'],min(config.population,state['index']+config.window)):
                        seed=config.seed+state['generation']*config.population+i;parent=None;construction=dict(method='random_population')
                        if parents and config.strategy!='random' and i%3:
                            parent=db.get(parents[seed%len(parents)]);witness=(parent.get('screen',{}).get('witness') or parent.get('certify',{}).get('witness')) if config.strategy in ('witness','hybrid','costhybrid') else None
                            g=mutate(inp,Genome.from_dict(parent['genome']),seed,witness,target=config.target,compact_ancillas=config.synthesis_mode=='joint')
                            construction=dict(method='physical_witness_guided_repair' if witness else 'mutation',parent=parent['id'])
                            if i%7==0:g=recombine(g,sample(inp,seed+10**6,config.target));construction['recombined']=True
                        else:g=sample(inp,seed,config.target)
                        intents.append(dict(index=i,seed=seed,genome=g.to_dict(),parent=parent['id'] if parent else None,construction=construction))
                    plan=dict(intents=intents,phase='construct');state['pending']=plan;persist()
                if plan['phase']=='construct':
                    construction_tier='construct_screen' if config.fuse_cheap and config.target>=3 and config.strategy not in ('costaware','costhybrid') else 'construct'
                    tasks=[]
                    for x in plan['intents']:
                        payload=dict(code_input=inp.to_dict(),genome=x['genome'])
                        if x['parent'] is None:payload['synthesis']=dict(guided=config.strategy!='random',parallel=True,joint=config.synthesis_mode=='joint')
                        tasks.append(task(payload,construction_tier,x['seed']))
                    answers=dispatch(tasks,[None]*len(tasks));ids=[]
                    for intent,t,a in zip(plan['intents'],tasks,answers):
                        result=a['result'];attempt=dict(generation=state['generation'],index=intent['index'])
                        if result.get('status')!='STRUCTURALLY_VALID':db.event('construction_outcome',dict(attempt=attempt,task=t.identity,intent=intent,result=result));continue
                        c=Circuit.from_dict(result['circuit']);cid=physical_identity(c)
                        if result['structural']['circuit']!=digest(c.to_dict()):raise ValueError('Construction identity mismatch')
                        if db.contains(cid):
                            old=db.get(cid)
                            if old.get('attempt')==attempt:ids.append(cid)
                            else:db.event('exact_duplicate',dict(attempt=attempt,existing=cid,intent=intent))
                            continue
                        row=dict(id=cid,circuit=c.to_dict(),genome=result.get('genome',intent['genome']),parent=intent['parent'],construction=result.get('construction',intent['construction']),generation=state['generation'],attempt=attempt,resources=result['resources'],structural=result['structural'],phase_costs=result['phase_costs'])
                        row['construction_task']=t.identity
                        if 'screen' in result:row['screen']=result['screen']
                        row['diversity']=diversity(row);db.put(row);ids.append(cid)
                    plan['ids']=list(dict.fromkeys(ids));plan['phase']='evaluate';persist()
                rows=[db.get(cid) for cid in plan['ids']]
                # Selection is recorded separately from hard invalidity. Deferred candidates remain eligible for future mutation.
                pool=select([r for r in rows if r.get('screen',{}).get('status')!='FAULT_INVALID' and r.get('certify',{}).get('status')!='INVALID'],config.promotion,config.seed+state['generated'])
                chosen={r['id'] for r in pool};db.event('promotion',dict(generation=state['generation'],index=state['index'],selected=sorted(chosen),deferred=[r['id'] for r in rows if r['id'] not in chosen],reason='Family-balanced resource selection and deterministic exploration'))
                direct=[]
                if config.strategy in ('costaware','costhybrid'):
                    from .costs import CostModel
                    from .adaptive import choose
                    model=CostModel(state['cost_observations'])
                    for i,row in enumerate(pool):
                        decision=choose(row,config.target,model,i);db.event('priority',dict(candidate=row['id'],**decision))
                        if decision['action']=='certify':direct.append(row)
                if direct:evaluate(direct,'certify')
                direct_ids={r['id'] for r in direct}
                screened=[r for r in rows if r['id'] not in direct_ids and 'screen' not in r and r.get('certify',{}).get('status') not in ('CERTIFIED','INVALID')]
                if screened:evaluate(screened,'screen')
                live=[r for r in pool if r.get('screen',{}).get('status')!='FAULT_INVALID' and r.get('certify',{}).get('status')!='INVALID']
                if live:evaluate(live,'simulation',config.initial_shots)
                selected=promising([r for r in live if 'confidence' in r.get('simulation',{})])
                if selected and config.strategy in ('hybrid','multifidelity','costaware','costhybrid'):
                    evaluate(selected,'simulation',config.further_shots,10**10)
                finalists=select(selected+[r for r in live if 'confidence' not in r.get('simulation',{})],config.finalists,config.seed+state['generated']) if config.finalists else []
                finalists=[r for r in finalists if r.get('certify',{}).get('status') not in ('CERTIFIED','INVALID')]
                if finalists:evaluate(finalists,'certify')
                for row in rows:
                    if row['id'] not in chosen:row['retention']='DEFERRED_NOT_INVALID';db.put(row)
                state['generated']+=len(plan['intents']);state['index']+=len(plan['intents']);state.pop('pending');state['status']='RUNNING'
                front=archives()
                db.event('frontier',dict(generated=state['generated'],unique=db.count(),certified=[dict(id=r['id'],resources=r['resources']) for r in front],worker_cpu=db.worker_cpu(),controller_cpu=sum(x['cpu'] for x in state['sessions'])+time.process_time()-cpu,elapsed_wall=sum(x['wall'] for x in state['sessions'])+time.perf_counter()-start))
                persist()
            else:state['status']='REQUESTED_GENERATIONS_COMPLETED'
        except KeyboardInterrupt:state['status']='CANCELLED'
        except MemoryError as e:state['status']='RESOURCE_SAFETY_INTERVENTION';state['resource_reason']=str(e)
        finally:
            archives(full=True);state['cache_hits']=state.get('cache_hits',0)+cache_hits
            tiers=db.totals()
            state['sessions'].append(dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-start,storage=dict(db.cost)))
            save(root/'compute.json',dict(tiers=tiers,sessions=state['sessions'],cache_hits=state['cache_hits'],scope='Whole-process worker CPU; controller sessions separate; summed worker wall is not elapsed time'))
            persist()
        return state