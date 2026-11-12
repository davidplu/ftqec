"""Read-only, source-bound analysis; missing/censored runs never become zeros."""
import argparse,itertools,json,statistics
from pathlib import Path
from ftqec.results.artifacts import save,digest
from ftqec.optimization.store import PopulationStore


ANALYSIS_CONVENTION='measured-checkpoint-coverage-1'


def measured_coverage(checkpoint,receipt,shared_cpu=0.):
    """Queue exhaustion is not evidence that the requested CPU was consumed."""
    if receipt['controller_cpu'] is None:return 'UNCONFIRMED_ACCOUNTING'
    actual=shared_cpu+receipt['controller_cpu']+receipt['worker_cpu']
    return 'OBSERVED' if actual>=checkpoint['cpu'] else 'NOT_REACHED'


def compute_receipt(run):
    receipts=[json.loads(p.read_text()) for p in sorted(run.glob('controller-process-*.json'))]
    complete=bool(receipts) and len(list(run.glob('controller-*.log')))<=len(receipts)
    with PopulationStore(run/'population.sqlite',readonly=True) as db:
        workers=db.worker_cpu()
        sector_status_counts={str(status):n for status,n in db.db.execute('SELECT status,count(*) FROM candidates GROUP BY status')}
        task_state_counts=[dict(tier=tier,status=status,count=n) for tier,status,n in db.db.execute('SELECT tier,status,count(*) FROM tasks GROUP BY tier,status')]
        tiers={name:dict(tasks=n,cpu=cpu,summed_wall=wall,peak_rss=peak) for name,n,cpu,wall,peak in db.db.execute('''
            SELECT t.tier,count(*),sum(e.cpu),sum(e.wall),max(e.peak) FROM execution e JOIN tasks t ON t.id=e.id GROUP BY t.tier''')}
    return dict(worker_cpu=workers,controller_cpu=sum(r['whole_controller_cpu'] for r in receipts) if complete else None,
        external_measurement_driver_cpu=sum(r['supervisor_cpu'] for r in receipts) if receipts else None,
        controller_elapsed_wall=sum(r['wall'] for r in receipts) if receipts else None,
        controller_sampled_peak_rss=max((r['sampled_peak_rss'] for r in receipts),default=None),
        worker_sampled_peak_rss=max((r['peak_rss'] for r in tiers.values()),default=0),tiers=tiers,
        sector_status_counts=sector_status_counts,task_state_counts=task_state_counts,
        logical_disk_bytes=sum(p.stat().st_size for p in run.rglob('*') if p.is_file()),
        qualification='Separate sampled process peaks, not a simultaneous aggregate-memory measurement; no missing controller receipt is imputed as zero')


def sign_randomization(differences):
    """Exact paired sign-flip test; requires symmetric null paired differences."""
    if not differences:return None
    observed=abs(sum(differences));n=len(differences)
    extreme=sum(abs(sum(s*d for s,d in zip(signs,differences)))>=observed-1e-15
                for signs in itertools.product((-1,1),repeat=n))
    return dict(p_two_sided=extreme/2**n,seeds=n,assumption='paired differences exchangeable under sign reversal',
                minimum_possible_two_sided_p=2/2**n)


def analyze(epoch):
    epoch=Path(epoch);protocols=list(epoch.glob('protocol-A-v*.json'))
    if len(protocols)!=1:raise ValueError('Exactly one frozen fixed-pool protocol required per epoch')
    spec=json.loads(protocols[0].read_text());records=[];missing=[];compute=[];preparation=[]
    if digest({k:v for k,v in spec.items() if k!='identity'})!=spec['identity']:
        raise ValueError('Protocol integrity mismatch')
    for seed in spec['generator_seeds']:
        block=epoch/'fixed-pool'/f'seed-{seed}'
        pool_path=block/'pool/pool-accounted.json'
        if pool_path.exists():
            pool=json.loads(pool_path.read_text())
            if digest({k:v for k,v in pool.items() if k!='hash'})!=pool['hash'] or pool['protocol']!=spec['identity']:
                raise ValueError('Pool integrity or protocol mismatch')
            preparation.append(dict(seed=seed,pool_hash=pool['hash'],shared_cpu=pool['shared_cpu'],
                proposals=pool['proposals'],distinct_compiled_pairs=len(pool['pairs']),aliases=len(pool['aliases']),
                construction_outcomes=pool['outcomes'],screen_eligible_pairs=sum(p['eligible'] for p in pool['pairs']),
                scope='Charged to each policy for comparison; count once in actual campaign execution cost',
                **compute_receipt(pool_path.parent)))
        available={};receipts={}
        for policy in spec['policies']:
            path=block/policy/'comparison.json'
            if not path.exists():missing.append(dict(seed=seed,policy=policy,reason='No completed comparison snapshot'));continue
            data=json.loads(path.read_text())
            if data['protocol']!=spec['identity']:raise ValueError('Mixed protocols')
            available[policy]=data
            receipts[policy]=compute_receipt(path.parent)
            compute.append(dict(seed=seed,policy=policy,evaluated_pairs=data['state']['index'],
                certified_pairs=len(data['state']['positive']),status=data['state']['status'],**receipts[policy]))
        positive={p['id']:p for data in available.values() for p in data['state']['positive']}
        for policy,data in available.items():
            for offset,point in zip(spec['promotion_cpu_checkpoints'],data['checkpoints']):
                accepted=[e['pair'] for e in data['state']['events'] if e['available_cpu']<point['cpu']]
                # Determine accepted positives from the actual verified positive set,
                # including dominated/tied discoveries absent from the final skyline.
                verified={p['id'] for p in data['state']['positive']} & set(accepted)
                metrics=point['frontier']
                coverage=measured_coverage(point,receipts[policy],pool['shared_cpu']) if pool_path.exists() else 'UNCONFIRMED_ACCOUNTING'
                records.append(dict(seed=seed,policy=policy,promotion_cpu_checkpoint=offset,total_cpu_checkpoint=point['cpu'],
                    raw_coverage=point['coverage'],coverage=coverage,accounting_censored=data['accounting_censored'],
                    valid_comparison=coverage=='OBSERVED' and not data['accounting_censored'],
                    hypervolume=point['hypervolume'],frontier=metrics,paired_positives=len(verified),
                    missed_verified_pool_pairs=sorted(set(positive)-verified),
                    missed_scope='Retrospective union of independently verified pool positives, including retained overshoot; not a claim all fit the budget',
                    best={k:min((p['resources'][k] for p in metrics),default=None) for k in ('Q','D','QD','two_q_gates')}))
    primary=[]
    for seed in spec['generator_seeds']:
        rows={r['policy']:r for r in records if r['seed']==seed and r['promotion_cpu_checkpoint']==spec['promotion_cpu_checkpoints'][-1] and r['valid_comparison']}
        if 'frontier' in rows and 'legacy' in rows:
            primary.append(dict(seed=seed,difference=rows['frontier']['hypervolume']-rows['legacy']['hypervolume']))
    diffs=[p['difference'] for p in primary]
    result=dict(protocol=spec['identity'],analysis_convention=ANALYSIS_CONVENTION,records=records,compute=compute,preparation=preparation,missing=missing,primary_contrast=primary,
        primary_promotion_cpu_checkpoint=spec['promotion_cpu_checkpoints'][-1],
        primary_complete=len(primary)==len(spec['generator_seeds']),
        median_difference=statistics.median(diffs) if diffs else None,
        wins=sum(x>0 for x in diffs),ties=sum(x==0 for x in diffs),losses=sum(x<0 for x in diffs),
        sign_randomization=sign_randomization(diffs) if len(primary)==len(spec['generator_seeds']) else None,
        interpretation='No superiority claim while planned paired blocks are incomplete; five seeds give coarse uncertainty even when complete.')
    result['identity']=digest(result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('epoch');p.add_argument('--output',required=True);a=p.parse_args()
    result=analyze(a.epoch);save(a.output,result)
    print(json.dumps(dict(primary_complete=result['primary_complete'],paired_seeds=len(result['primary_contrast']),missing=len(result['missing'])),indent=2))


if __name__=='__main__':main()
