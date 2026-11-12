"""Controlled adaptive campaigns, separate from the immutable-pool experiment."""
import argparse,random
from pathlib import Path
from .controlled import Ledger,protocol
from .policies import order,aggregate,hypervolume,checkpoint_frontier
from ..optimization.phase3 import proposal,unproved_resource_frontier
from ..optimization.store import skyline
from ..results.artifacts import digest,save
from ..codes.two_block import parse
from ..circuits.model import Circuit
from ..circuits.identity import physical_identity


def repair_parents(parents,target):
    """An exact-distance upper witness is not a below-target repair failure."""
    selected=[]
    for row in parents:
        copy=dict(row);cert=dict(row.get('certify',{}));screen=dict(row.get('screen',{}))
        for record,allowed in ((cert,cert.get('status')=='INVALID' and row.get('independent_verification',{}).get('verified',False)),
                               (screen,screen.get('status')=='FAULT_INVALID' and screen.get('verification',{}).get('verified',False))):
            if not allowed or not record.get('witness') or len(record['witness']['faults'])>=target:record.pop('witness',None)
        copy.update(certify=cert,screen=screen);selected.append(copy)
    return selected


def generate(code,index,seed,strategy,parents,target=6):
    if strategy in ('structured','hybrid'):return proposal(code,index,seed,strategy,repair_parents(parents,target))
    if strategy!='random_unfiltered':raise ValueError('Unknown generation strategy')
    # The random baseline shares the architecture/ancilla distribution but has no
    # crossing-parity order prefilter. Actual compiled instrument validation remains.
    rng=random.Random(seed+index*1000003)
    terms=[('X',i) for i in range(len(code.x_terms))]+[('Z',i) for i in range(len(code.z_terms))]
    rng.shuffle(terms);n=code.checks.n;budget=n+max(1,round(n*(1-index%6/6)))
    checks=list(range(len(code.checks.generators)))
    if index%4==1:rng.shuffle(checks)
    genome=dict(family='group_term' if index%3==0 else 'group_pool',order=[list(x) for x in terms],
                ancilla_slots=budget-n,checks=checks,check_basis='independent' if index%11==7 else 'redundant')
    if index%20 in (17,18,19):
        width=max(g.weight for g in code.checks.generators)
        genome.update(family={17:'flagged',18:'cat',19:'verified_cat'}[index%20],ancilla_slots=max(1,(budget-n)//(width+1)),
                      flag_style='adjacent',verification_rounds=2,schedule='critical_path')
    return dict(key=digest(genome),genome=genome,parent=None,mutation='unfiltered_random_order',diagnosis=None,
                raw_order_draws=1,requested_qubit_budget=budget)


def selected_window(pairs,policy,seed,n):
    eligible=[p for p in pairs if p['eligible']]
    if policy=='frontier':policy='legacy'  # Actual integration: legacy first, final sweep later.
    selected=order(eligible,policy,seed,n=n)
    return selected if policy in ('direct','legacy') else selected[:2]


def optimize(spec,root,seed,policy,strategy='hybrid'):
    code=parse(spec['code']);settings=dict(spec['settings'],code_identity=code.input.identity,decoder='bposd',seed=seed,
                                         promotion_seed=seed+100000,p=spec['settings']['noise'])
    identity=digest(dict(protocol=spec['identity'],kind='adaptive',seed=seed,policy=policy,generator=strategy))
    run=Ledger(root,identity,spec['source'],settings,seed+100000);db=run.db
    state=db.get_meta('state',dict(index=0,pairs=[],aliases=[],outcomes=[],positive=[],events=[],phase='generate',
                                 pending=[],build_cursor=0,selected=[],selection_cursor=0,window_pairs=[],status='RUNNING'))
    state.update(code=code.input.to_dict())
    checkpoints=spec['total_cpu_checkpoints'];goal=spec['candidate_goal'];maximum=max(checkpoints)
    state['status']='RUNNING'

    def persist():db.set_meta('state',state);run.persist()

    def evaluate(pair):
        rows=[]
        for cid in pair['sectors']:
            row=db.get(cid);row['simulation']=run.evaluate(cid,'simulation',row['circuit'])
            cert=run.evaluate(cid,'certify',row['circuit']);row['certify']=cert
            if cert['status'] in ('CERTIFIED','INVALID'):
                checked=run.evaluate(cid,'verify_exact',dict(circuit=row['circuit'],certificate=cert))
                row['independent_verification']=checked
                if checked['status']=='CONTRADICTION':db.put(row);raise RuntimeError('Physical witness contradicts lower bound')
                row['certify']=checked.get('certificate',cert)
                if checked['status'] not in ('CERTIFIED','INVALID'):row['certify']=dict(row['certify'],status='UNKNOWN')
            db.put(row);rows.append(row)
        if all(r.get('independent_verification',{}).get('status')=='CERTIFIED' for r in rows):
            if pair['id'] not in {r['id'] for r in state['positive']}:state['positive'].append(pair)
        persist()
        frontier=skyline(state['positive'])
        state['events'].append(dict(pair=pair['id'],available_cpu=run.cpu(),frontier=frontier,
            hypervolume=hypervolume(frontier,spec['hypervolume_reference']),phase=state['phase']))

    try:
        while True:
            if run.cpu()>=maximum:state['status']='EXPERIMENT_CHECKPOINT_REACHED';break
            if state['phase']=='generate':
                if not state['pending']:
                    if state['index']>=goal:
                        if policy=='frontier':
                            lookup={p['id']:p for p in state['pairs']}
                            ids=unproved_resource_frontier(db)
                            state['selected']=[lookup[db.get(sectors[0])['pair']] for sectors in ids]
                            state['selection_cursor']=0;state['phase']='final_sweep';persist();continue
                        state['status']='COMPLETE';break
                    parents=[db.get(cid) for cid in db.parent_ids(8,seed+state['index'])]
                    count=min(10,goal-state['index'])
                    state['pending']=[dict(index=i,**generate(code,i,seed,strategy,parents,settings['target'])) for i in range(state['index'],state['index']+count)]
                    state['build_cursor']=0;state['window_pairs']=[]
                    for p in state['pending']:db.event('proposal',p)
                    persist()
                if state['build_cursor']<len(state['pending']):
                    p=state['pending'][state['build_cursor']]
                    result=run.evaluate(p['key'],'construct_2bga',dict(code_input=spec['code'],rounds=settings['rounds'],genome=p['genome']))
                    if result['status']=='STRUCTURALLY_VALID':
                        pair=digest([physical_identity(Circuit.from_dict(c)) for c in result['circuits']])
                        if pair in {r['id'] for r in state['pairs']}:state['aliases'].append(dict(index=p['index'],pair=pair,proposal=p['key']))
                        else:
                            rows=[]
                            for c,metrics in zip(result['circuits'],result['resources']):
                                cid=digest(c);row=dict(id=cid,circuit=c,resources=metrics,genome=p['genome'],generation=p['index']//10,
                                    pair=pair,parent=p['parent'],diagnosis=p['diagnosis'],diversity=dict(timed_structure=physical_identity(Circuit.from_dict(c))))
                                row['screen']=run.evaluate(cid,'screen',c);db.put(row);rows.append(row)
                            info=dict(id=pair,index=p['index'],resources=aggregate(rows),sectors=[r['id'] for r in rows],
                                      eligible=not any(r['screen'].get('status')=='FAULT_INVALID' for r in rows))
                            state['pairs'].append(info);state['window_pairs'].append(info)
                    else:state['outcomes'].append(dict(index=p['index'],proposal=p['key'],result=result))
                    state['build_cursor']+=1;state['index']+=1;persist();continue
                state['selected']=selected_window(state['window_pairs'],policy,seed+100000+state['index']//10,code.checks.n)
                state['selection_cursor']=0;state['phase']='window_promotion';persist()
            else:
                if state['selection_cursor']<len(state['selected']):
                    evaluate(state['selected'][state['selection_cursor']]);state['selection_cursor']+=1;persist()
                    print(dict(policy=policy,generator=strategy,proposals=state['index'],paired=len(state['positive']),cpu=run.cpu(),phase=state['phase']),flush=True)
                    continue
                if state['phase']=='final_sweep':state['status']='COMPLETE';break
                state['pending']=[];state['phase']='generate';persist()
    except (MemoryError,InterruptedError) as exc:
        state['status']='BLOCKED';state['reason']=str(exc);raise
    except Exception:
        state['status']='ERROR';raise
    finally:
        persist()
        save(Path(root)/'comparison.json',dict(protocol=spec['identity'],experiment='adaptive',seed=seed,policy=policy,generator=strategy,
            state=state,accounting_censored=run.censored,
            checkpoints=[dict(cpu=c,coverage='OBSERVED' if run.cpu()>=c or state['status']=='COMPLETE' else 'NOT_REACHED',
                frontier=checkpoint_frontier(state['events'],c),hypervolume=hypervolume(checkpoint_frontier(state['events'],c),spec['hypervolume_reference'])) for c in checkpoints]))
        run.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--protocol',required=True);p.add_argument('--output',required=True)
    p.add_argument('--seed',type=int,required=True);p.add_argument('--policy',choices=('direct','random','resource','legacy','frontier'),required=True)
    p.add_argument('--generator',choices=('structured','hybrid','random_unfiltered'),default='hybrid');a=p.parse_args()
    optimize(protocol(a.protocol),a.output,a.seed,a.policy,a.generator)


if __name__=='__main__':main()
