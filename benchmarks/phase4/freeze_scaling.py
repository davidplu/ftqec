"""Freeze the predeclared 1000-proposal stage without importing promotion answers."""
import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from ftqec.results.artifacts import digest, save, source_identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixed-protocol', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    original = Path(args.fixed_protocol).resolve()
    base = json.loads(original.read_text())
    if digest({k: v for k, v in base.items() if k != 'identity'}) != base['identity']:
        raise ValueError('Parent protocol integrity failure')
    if source_identity() != base['source']:
        raise ValueError('Scientific source differs from parent protocol')
    epoch = Path(args.output).resolve()
    if epoch.exists():
        raise FileExistsError('Use a new epoch; never overwrite a frozen plan')
    snapshot = epoch / 'frozen/src'
    snapshot.mkdir(parents=True)
    shutil.copytree(root / 'src/ftqec', snapshot / 'ftqec',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    excluded = {'identity', 'reused_preparation', 'engineering_regression',
                'amendment', 'supersedes', 'document_sha256', 'protocol_document'}
    spec = {k: v for k, v in base.items() if k not in excluded}
    spec.update(
        schema='controlled-scaling-1', parent_protocol=base['identity'],
        created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        source_snapshot='frozen/src', generator_seeds=[74011], initial_proposals=1000,
        promotion_cpu_checkpoints=[1000, 2500, 5000],
        primary_contrast='Descriptive frontier versus legacy within the same 1000-proposal pool at P+5000',
        prerequisite='Complete the initial fixed-pool and main72 adaptive comparisons before launching this stage',
        interpretation='One seed is descriptive. Within-pool policy comparisons use identical total CPU checkpoints. '
                       'Different pool sizes have different preparation costs; this stage alone cannot establish a '
                       'matched-total-compute population-size advantage.',
        expansion_gate='10000 proposals only if a new certified resource tuple beyond the 100-proposal pool exists, '
                       'at least 10 percent of the last 100 proposals add distinct physical pairs, and measured local '
                       'memory and disk permit execution. Freeze a separate protocol before that stage.',
        driver_sha256=hashlib.sha256((root / 'benchmarks/phase4/run_fixed_pool.py').read_bytes()).hexdigest(),
        policy_semantics='Same fixed-pool policy definitions, physical model, decoder, and verification requirements as parent; '
                         'fresh construction and fresh promotion tasks, with no imported certification answers.')
    spec['identity'] = digest(spec)
    save(epoch / 'protocol-A-v1.json', spec)
    save(epoch / 'input-code72.json', spec['code'])
    for name in ('run_fixed_pool.py', 'freeze_scaling.py'):
        shutil.copy2(root / 'benchmarks/phase4' / name, epoch / 'frozen' / name)
    print(json.dumps(dict(protocol=str(epoch / 'protocol-A-v1.json'), identity=spec['identity'])))


if __name__ == '__main__':
    main()
