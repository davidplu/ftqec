"""Budget selection and incomplete-data handling in offline experiment analysis."""
from benchmarks.phase4.analyze_fixed_pool import analyze
from ftqec.optimization.store import PopulationStore
from ftqec.results.artifacts import digest, save


def test_scaling_analysis_uses_final_frozen_checkpoint_and_reports_missing(tmp_path):
    spec = dict(generator_seeds=[74011, 74023], policies=['frontier', 'legacy'],
                promotion_cpu_checkpoints=[1000, 5000])
    spec['identity'] = digest(spec)
    save(tmp_path / 'protocol-A-v1.json', spec)
    pool_root = tmp_path / 'fixed-pool/seed-74011/pool'
    pool_root.mkdir(parents=True)
    with PopulationStore(pool_root / 'population.sqlite'):
        pass
    pool = dict(protocol=spec['identity'], shared_cpu=0, proposals=0, pairs=[], aliases=[], outcomes=[])
    pool['hash'] = digest(pool)
    save(pool_root / 'pool-accounted.json', pool)
    for policy, values in [('frontier', [0.1, 0.4]), ('legacy', [0.2, 0.2])]:
        root = tmp_path / 'fixed-pool/seed-74011' / policy
        root.mkdir(parents=True)
        with PopulationStore(root / 'population.sqlite'):
            pass
        save(root / 'controller-process-1.json', dict(whole_controller_cpu=6000, wall=6000,
             sampled_peak_rss=100, supervisor_cpu=1))
        save(root / 'comparison.json', dict(protocol=spec['identity'], accounting_censored=False,
             state=dict(positive=[], events=[], index=0, status='EXPERIMENT_CHECKPOINT_REACHED'), checkpoints=[dict(cpu=c, coverage='OBSERVED',
             frontier=[], hypervolume=h) for c, h in zip([1000, 5000], values)]))
    result = analyze(tmp_path)
    assert result['primary_promotion_cpu_checkpoint'] == 5000
    assert result['primary_contrast'] == [dict(seed=74011, difference=0.2)]
    assert not result['primary_complete']
    assert result['sign_randomization'] is None
    assert len(result['missing']) == 2
    assert all(r['controller_cpu'] == 6000 for r in result['compute'])
    assert all(r['external_measurement_driver_cpu'] == 1 for r in result['compute'])


def test_adaptive_analysis_retains_censored_arms_and_sweep_nonactivation(tmp_path):
    from benchmarks.phase4.analyze_adaptive import analyze as adaptive_analysis
    spec = dict(source='test-source', total_cpu_checkpoints=[100])
    spec['identity'] = digest(spec)
    save(tmp_path / 'main72/protocol.json', spec)
    case = dict(name='main72', protocol='main72/protocol.json', identity=spec['identity'],
                generators=['hybrid'], policies=['frontier', 'legacy'])
    plan = dict(source='test-source', cases=[case], seeds=[1])
    plan['identity'] = digest(plan)
    save(tmp_path / 'plan.json', plan)
    root = tmp_path / 'main72/seed-1/hybrid/frontier'
    root.mkdir(parents=True)
    with PopulationStore(root / 'population.sqlite'):
        pass
    save(root / 'comparison.json', dict(protocol=spec['identity'], seed=1, generator='hybrid',
        policy='frontier', accounting_censored=True,
        state=dict(index=10, pairs=[], outcomes=[], aliases=[], positive=[], events=[],
                   phase='window_promotion', status='BLOCKED'),
        checkpoints=[dict(cpu=100, coverage='OBSERVED', hypervolume=0, frontier=[])]))
    result = adaptive_analysis(tmp_path / 'plan.json')['cases'][0]
    assert result['missing'] == [dict(seed=1, generator='hybrid', policy='legacy')]
    assert not result['records'][0]['valid_comparison']
    assert result['compute'][0]['final_sweep_pair_evaluations'] == 0
    assert not result['frontier_minus_legacy'][0]['complete']


def test_queue_exhaustion_does_not_impute_unconsumed_compute():
    from benchmarks.phase4.analyze_fixed_pool import measured_coverage
    point = dict(cpu=1000, coverage='OBSERVED')  # Raw exhausted-queue convention.
    receipt = dict(controller_cpu=20, worker_cpu=80)
    assert measured_coverage(point, receipt, shared_cpu=500) == 'NOT_REACHED'
    assert measured_coverage(point, receipt, shared_cpu=900) == 'OBSERVED'
    assert measured_coverage(point, dict(controller_cpu=None, worker_cpu=2000)) == 'UNCONFIRMED_ACCOUNTING'
