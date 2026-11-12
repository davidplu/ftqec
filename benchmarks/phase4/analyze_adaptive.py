"""Analyze completed adaptive snapshots without turning missing arms into zeros."""
import argparse
import json
import statistics
from pathlib import Path

from ftqec.results.artifacts import digest, save

try:
    from .analyze_fixed_pool import compute_receipt, sign_randomization, measured_coverage, ANALYSIS_CONVENTION
except ImportError:
    from analyze_fixed_pool import compute_receipt, sign_randomization, measured_coverage, ANALYSIS_CONVENTION


def sealed(path):
    value = json.loads(path.read_text())
    if digest({k: v for k, v in value.items() if k != 'identity'}) != value['identity']:
        raise ValueError(f'Integrity failure: {path}')
    return value


def analyze(path):
    path = Path(path)
    plan = sealed(path)
    epoch = path.parent
    cases = []
    for case in plan['cases']:
        spec = sealed(epoch / case['protocol'])
        if spec['identity'] != case['identity'] or spec['source'] != plan['source']:
            raise ValueError('Mixed protocol/source')
        rows, missing, compute = [], [], []
        for seed in plan['seeds']:
            for strategy in case['generators']:
                for policy in case['policies']:
                    label = dict(seed=seed, generator=strategy, policy=policy)
                    root = epoch / case['name'] / f'seed-{seed}' / strategy / policy
                    result_path = root / 'comparison.json'
                    if not result_path.exists():
                        missing.append(label)
                        continue
                    data = json.loads(result_path.read_text())
                    if data['protocol'] != spec['identity'] or any(data[k] != v for k, v in label.items()):
                        raise ValueError('Comparison identity mismatch')
                    state = data['state']
                    receipt = compute_receipt(root)
                    compute.append(dict(**label, **receipt,
                        completed_proposals=state['index'], distinct_compiled_pairs=len(state['pairs']),
                        construction_outcomes=len(state['outcomes']), aliases=len(state['aliases']),
                        certified_pairs=len(state['positive']),
                        final_sweep_pair_evaluations=sum(e['phase'] == 'final_sweep' for e in state['events']),
                        last_phase=state['phase'], status=state['status']))
                    for point in data['checkpoints']:
                        coverage = measured_coverage(point, receipt)
                        rows.append(dict(**label, cpu_checkpoint=point['cpu'], raw_coverage=point['coverage'], coverage=coverage,
                            valid_comparison=coverage == 'OBSERVED' and not data['accounting_censored'],
                            hypervolume=point['hypervolume'], frontier=point['frontier'],
                            best={k: min((p['resources'][k] for p in point['frontier']), default=None)
                                  for k in ('Q', 'D', 'QD', 'two_q_gates')}))
        contrasts = []
        for strategy in case['generators']:
            differences = []
            for seed in plan['seeds']:
                matched = {r['policy']: r for r in rows if r['seed'] == seed and r['generator'] == strategy
                           and r['cpu_checkpoint'] == spec['total_cpu_checkpoints'][-1] and r['valid_comparison']}
                if 'frontier' in matched and 'legacy' in matched:
                    differences.append(dict(seed=seed, difference=matched['frontier']['hypervolume'] - matched['legacy']['hypervolume']))
            values = [d['difference'] for d in differences]
            complete = len(values) == len(plan['seeds'])
            contrasts.append(dict(generator=strategy, paired_seeds=differences, complete=complete,
                median=statistics.median(values) if values else None,
                sign_randomization=sign_randomization(values) if complete else None))
        cases.append(dict(name=case['name'], protocol=spec['identity'], records=rows, compute=compute,
                          missing=missing, frontier_minus_legacy=contrasts))
    result = dict(plan=plan['identity'], source=plan['source'], analysis_convention=ANALYSIS_CONVENTION, cases=cases,
        qualification='Adaptive results are separate from fixed-pool results. Generation comparisons must join '
                      'the prospectively shared main72/hybrid/frontier control; absent strategy arms are NOT_RUN. '
                      'No final-sweep evaluations does not prove that a sweep would be ineffective with more compute.')
    result['identity'] = digest(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = analyze(args.plan)
    save(args.output, result)
    print(json.dumps({c['name']: dict(completed_snapshots=len(c['compute']), missing=len(c['missing'])) for c in result['cases']}))


if __name__ == '__main__':
    main()
