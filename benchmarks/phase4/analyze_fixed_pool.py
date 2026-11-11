"""Read-only, source-bound analysis; missing/censored runs never become zeros."""
import argparse,itertools,json,statistics
from pathlib import Path
from ftqec.results.artifacts import save,digest


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
    spec=json.loads(protocols[0].read_text());records=[];missing=[]
    for seed in spec['generator_seeds']:
        block=epoch/'fixed-pool'/f'seed-{seed}'
        available={}
        for policy in spec['policies']:
            path=block/policy/'comparison.json'
            if not path.exists():missing.append(dict(seed=seed,policy=policy,reason='No completed comparison snapshot'));continue
            data=json.loads(path.read_text())
            if data['protocol']!=spec['identity']:raise ValueError('Mixed protocols')
            available[policy]=data
        positive={p['id']:p for data in available.values() for p in data['state']['positive']}
        for policy,data in available.items():
            for offset,point in zip(spec['promotion_cpu_checkpoints'],data['checkpoints']):
                accepted=[e['pair'] for e in data['state']['events'] if e['available_cpu']<point['cpu']]
                # Determine accepted positives from the actual verified positive set,
                # including dominated/tied discoveries absent from the final skyline.
                verified={p['id'] for p in data['state']['positive']} & set(accepted)
                metrics=point['frontier']
                records.append(dict(seed=seed,policy=policy,promotion_cpu_checkpoint=offset,total_cpu_checkpoint=point['cpu'],
                    coverage=point['coverage'],accounting_censored=data['accounting_censored'],
                    valid_comparison=point['coverage']=='OBSERVED' and not data['accounting_censored'],
                    hypervolume=point['hypervolume'],frontier=metrics,paired_positives=len(verified),
                    missed_verified_pool_pairs=sorted(set(positive)-verified),
                    missed_scope='Retrospective union of independently verified pool positives, including retained overshoot; not a claim all fit the budget',
                    best={k:min((p['resources'][k] for p in metrics),default=None) for k in ('Q','D','QD','two_q_gates')}))
    primary=[]
    for seed in spec['generator_seeds']:
        rows={r['policy']:r for r in records if r['seed']==seed and r['promotion_cpu_checkpoint']==1000 and r['valid_comparison']}
        if 'frontier' in rows and 'legacy' in rows:
            primary.append(dict(seed=seed,difference=rows['frontier']['hypervolume']-rows['legacy']['hypervolume']))
    diffs=[p['difference'] for p in primary]
    result=dict(protocol=spec['identity'],records=records,missing=missing,primary_contrast=primary,
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
