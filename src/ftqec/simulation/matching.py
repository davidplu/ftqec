"""Optional correlated matching; failed graph decomposition is explicit."""
import time
from ..results.artifacts import digest


def evaluate_matching(c, p, shots, seed, max_decoder_faults=100000):
    from .monte_carlo import model, interval
    start = time.perf_counter(); cpu = time.process_time()
    try:
        import pymatching
        import numpy as np
    except ImportError:
        return dict(status="UNSUPPORTED_DECODER", reason="pymatching not installed", decoder="correlated_matching")
    sc = model(c, p, detector_basis="temporal")
    build_cpu = time.process_time(); build_wall = time.perf_counter()
    try:
        dem = sc.detector_error_model(decompose_errors=True, approximate_disjoint_errors=False,
                                      ignore_decomposition_failures=False).flattened()
        if dem.num_errors > max_decoder_faults:
            return dict(status="UNSUPPORTED_DECODER", reason="decoder mechanism resource limit", decoder="correlated_matching")
        matching = pymatching.Matching.from_detector_error_model(dem, enable_correlations=True)
    except (ValueError, RuntimeError) as e:
        return dict(status="UNSUPPORTED_DECODER", reason="no supported graphlike decomposition", detail=str(e),
                    decoder="correlated_matching", circuit=digest(c.to_dict()))
    build = dict(cpu=time.process_time()-build_cpu, wall=time.perf_counter()-build_wall)
    det, obs = sc.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    tick = time.perf_counter(); dc = time.process_time()
    try:
        predicted = matching.decode_batch(det, enable_correlations=True)
    except ValueError as e:
        return dict(status="UNSUPPORTED_DECODER", reason="matching inference failed", detail=str(e), decoder="correlated_matching")
    failures = int(np.count_nonzero(np.any(predicted != obs, axis=1)))
    return dict(p=p, shots=shots, failures=failures, decoder_unknown=0, rate=failures/shots,
                confidence=interval(failures, shots), seed=seed, decoder="correlated_matching",
                decoder_version=pymatching.__version__, decoder_build_cost=build,
                decoder_inference_cost=dict(cpu=time.process_time()-dc, wall=time.perf_counter()-tick),
                decoder_assumptions="correlation-aware two-pass matching heuristic, not optimal ML",
                detector_basis="invertible temporal differences",
                noise="operation_depolarizing_reset_X_measurement_flip_perfect_boundaries",
                approximation="no disjoint-channel approximation; suggested correlated decomposition used",
                stim_hash=digest(str(sc)), dem_hash=digest(str(dem)), cpu=time.process_time()-cpu,
                wall=time.perf_counter()-start)
