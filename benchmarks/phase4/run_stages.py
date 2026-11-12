"""Resume the frozen controlled studies in order, stopping at any blocker.

This executes experiments, not an autonomous declaration of scientific success.
Finalist selection, reliability, export audits, and final reporting still require
the separate review stage. No worker/global runtime cutoff is introduced.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from ftqec.execution.locking import RunLock
from ftqec.results.artifacts import digest, save, source_identity


def sealed(path):
    row = json.loads(path.read_text())
    if digest({k: v for k, v in row.items() if k != 'identity'}) != row['identity']:
        raise ValueError(f'Protocol hash mismatch: {path}')
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixed-epoch', required=True)
    parser.add_argument('--adaptive-plan', required=True)
    parser.add_argument('--scaling-protocol', required=True)
    parser.add_argument('--analysis-epoch', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    fixed = Path(args.fixed_epoch).resolve()
    adaptive = Path(args.adaptive_plan).resolve()
    scaling = Path(args.scaling_protocol).resolve()
    analysis = Path(args.analysis_epoch).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    fixed_files = list(fixed.glob('protocol-A-v*.json'))
    if len(fixed_files) != 1:
        raise ValueError('One fixed-pool protocol required')
    spec = sealed(fixed_files[0])
    plan = sealed(adaptive)
    scale = sealed(scaling)
    analysis_plan = sealed(analysis / 'protocol.json')
    if not source_identity() == spec['source'] == plan['source'] == scale['source']:
        raise ValueError('Scientific source mismatch')
    for name, expected in analysis_plan['files'].items():
        if hashlib.sha256((analysis / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen analysis implementation mismatch')
    analyze_a = str(analysis / 'benchmarks/phase4/analyze_fixed_pool.py')
    analyze_b = str(analysis / 'benchmarks/phase4/analyze_adaptive.py')
    run_b = str(root / 'benchmarks/phase4/run_adaptive.py')
    stages = [
        ('fixed-analysis', [analyze_a, str(fixed), '--output', str(output / 'fixed-analysis.json')]),
        ('adaptive-main72', [run_b, '--plan', str(adaptive), '--case', 'main72']),
        ('main72-analysis', [analyze_b, '--plan', str(adaptive), '--output', str(output / 'main72-analysis.json')]),
        ('scaling1000', [str(root / 'benchmarks/phase4/run_fixed_pool.py'), '--protocol', str(scaling)]),
        ('scaling-analysis', [analyze_a, str(scaling.parent), '--output', str(output / 'scaling-analysis.json')]),
        ('generation72', [run_b, '--plan', str(adaptive), '--case', 'generation72']),
        ('transfer24', [run_b, '--plan', str(adaptive), '--case', '2bga_D6_n24_k2_d4']),
        ('transfer36', [run_b, '--plan', str(adaptive), '--case', '2bga_D9_n36_k8_d4']),
        ('adaptive-analysis', [analyze_b, '--plan', str(adaptive), '--output', str(output / 'adaptive-analysis.json')]),
    ]
    binding = dict(fixed=spec['identity'], adaptive=plan['identity'], scaling=scale['identity'],
                   analysis=analysis_plan['identity'], source=spec['source'], stages=stages,
                   driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    binding['identity'] = digest(binding)
    state_path = output / 'state.json'
    with RunLock(output / 'run.lock'):
        if (output / 'plan.json').exists():
            if sealed(output / 'plan.json')['identity'] != binding['identity']:
                raise ValueError('Stage queue identity changed')
        else:
            save(output / 'plan.json', binding)
        state = json.loads(state_path.read_text()) if state_path.exists() else dict(completed=[], attempts=[])
        prior_cpu = state.get('queue_supervisor_cpu_snapshot', 0.)

        def record(status, **details):
            state.update(status=status, observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                         queue_supervisor_cpu_snapshot=prior_cpu+time.process_time(),
                         queue_cpu_scope='Outer stage coordination only; final interpreter exit tail unmeasured; never added twice to candidate controllers', **details)
            save(state_path, state)

        def cancelled():
            if (output / 'cancel.json').exists():
                raise InterruptedError('Explicit stage-queue cancellation; separately cancel an active scientific controller if needed')

        try:
            record('WAITING_FOR_FIXED_POOL')
            while True:
                cancelled()
                completed = 0
                for seed in spec['generator_seeds']:
                    for policy in spec['policies']:
                        path = fixed / 'fixed-pool' / f'seed-{seed}' / policy / 'comparison.json'
                        if not path.exists():
                            continue
                        row = json.loads(path.read_text())
                        if row['protocol'] != spec['identity']:
                            raise ValueError('Mixed prerequisite protocols')
                        if row['state']['status'] in ('BLOCKED', 'ERROR') or row['accounting_censored']:
                            raise RuntimeError(f'Prerequisite needs review: {path}')
                        if row['state']['status'] in ('EXPERIMENT_CHECKPOINT_REACHED', 'EXHAUSTED_POLICY_QUEUE'):
                            completed += 1
                record('WAITING_FOR_FIXED_POOL', fixed_arms_complete=completed)
                campaign_log = (fixed / 'fixed-pool-campaign.log').read_text(errors='replace')
                if 'Controller stopped; inspect preserved log' in campaign_log or 'Traceback (most recent call last)' in campaign_log:
                    raise RuntimeError('Fixed-pool driver stopped; inspect its retained log')
                if completed == len(spec['generator_seeds']) * len(spec['policies']) and 'Completed selected fixed-pool seed blocks' in campaign_log:
                    break
                time.sleep(30)
            for name, command in stages:
                if name in state['completed']:
                    continue
                if name == 'generation72':
                    decision_path = output / 'scaling-review.json'
                    result = sealed(output / 'scaling-analysis.json')
                    if not decision_path.exists():
                        record('READY_FOR_SCALING_REVIEW', active_stage=None, stage_pid=None,
                            remaining=['Evaluate the prospectively declared 10000-proposal expansion gate',
                                       'Record a source-bound scaling decision before generation/transfer execution'])
                        return
                    decision = sealed(decision_path)
                    if decision.get('analysis') != result['identity'] or decision.get('decision') != 'CONTINUE_WITHOUT_10000':
                        raise RuntimeError('Scaling review requires a separately frozen expansion study or a justified no-expansion decision')
                cancelled()
                if source_identity() != spec['source']:
                    raise ValueError('Scientific source changed while queued')
                attempt = sum(a['stage'] == name for a in state['attempts']) + 1
                log = output / f'{name}-{attempt}.log'
                start = time.perf_counter()
                with log.open('w', encoding='utf-8') as stream:
                    child = subprocess.Popen([sys.executable, *command], cwd=root,
                        env=dict(os.environ, PYTHONPATH=str(root / 'src')), stdout=stream, stderr=subprocess.STDOUT)
                    record('RUNNING_STAGE', active_stage=name, stage_pid=child.pid)
                    print(json.dumps(dict(stage=name, pid=child.pid, log=str(log))), flush=True)
                    child.wait()
                state['attempts'].append(dict(stage=name, returncode=child.returncode,
                    elapsed=time.perf_counter()-start, log=str(log)))
                if child.returncode:
                    raise RuntimeError(f'{name} stopped; inspect {log}')
                state['completed'].append(name)
                record('STAGE_FINISHED', active_stage=None, stage_pid=None)
            record('READY_FOR_FINALIST_REVIEW', remaining=['Review all comparisons and scaling gate',
                'Freeze resource-selected finalists and run BP-OSD reliability batches',
                'Independently export/replay adopted results, run final tests and integrity audit',
                'Write final scientific report and acceptance gates'])
        except Exception as exc:
            record('BLOCKED', blocker=str(exc))
            raise


if __name__ == '__main__':
    main()
