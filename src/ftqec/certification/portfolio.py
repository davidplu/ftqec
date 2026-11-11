"""Measured structural selection; exact backends retain their own checkers."""
import math,time
from . import mechanism_ir


def certify(c,target,work,directory=None):
    from .high_distance import certify as old
    from .relaxation_portfolio import certify as collapsed
    tick=time.perf_counter();cpu=time.process_time()
    features=dict(rounds=c.experiment.get('rounds',1),target=target,
                  detectors=len(c.detectors),logicals=len(c.observables),
                  graph_eligibility='backend validates; not inferred from raw detector degree')
    if c.boundary_model!='repeated_noisy_memory' or target<=3:
        result=old(c,target,work,directory,'auto');selected='legacy_auto'
    else:
        ir=mechanism_ir.build(c)
        projected=mechanism_ir.project(ir,mechanism_ir.memory_projection(c,sector=True))
        n=len(projected['columns']);pairs=math.comb(n,2);triples=math.comb(n,3)
        features.update(locations=len({r[0] for r in ir['alternatives']}),alternatives=len(ir['alternatives']),
                        distinct_signatures=len(ir['columns']),projected_mechanisms=n,
                        projected_pair_entries=pairs,projected_triple_scan=triples,
                        calibration='Nov9: 180-column repeated-memory proofs completed; full-sector 2376-column pair tables censored')
        # Work units are backend-specific. This is a conservative admission
        # estimate, not a guarantee or a claim of universal fastest selection.
        fits=pairs<=500000 and (target<=4 or triples<=work)
        if fits:
            result=collapsed(c,target,work,directory,prepared=ir);selected='time_collapse'
            if result['status']=='UNKNOWN':
                fallback=old(c,target,min(work,200000),directory,'graph')
                features['fallback']=dict(status=fallback['status'],lower_bound=fallback.get('lower_bound'),method='graph')
                if fallback['status']=='INVALID' or fallback.get('lower_bound',1)>result.get('lower_bound',1):
                    features['unresolved_projection']=dict(lower_bound=result.get('lower_bound'),reason=result.get('reason'))
                    result=fallback;selected='graph_after_projection'
        else:
            result=old(c,target,work,directory,'auto');selected='legacy_auto'
    result['portfolio_selection']=dict(selected=selected,features=features,cpu=time.process_time()-cpu,wall=time.perf_counter()-tick)
    return result
