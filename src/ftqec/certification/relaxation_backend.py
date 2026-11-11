"""Checked row-relaxation experiment; keeps upstream solver claims separate."""
from pathlib import Path
from . import mechanism_ir as physical
from .relaxation import enumerate_minima, canonical_minima, lift_minima, Incomplete
from ..results.artifacts import save, digest, source_identity


def run(c, target, directory, work=50000000, sector=False, prepared=None):
    root = Path(directory)
    result = dict(status='UNKNOWN', target=target, lower_bound=1, upper_bound=None,
                  source=source_identity(), circuit=digest(c.to_dict()),
                  method='physical_mechanism_row_relaxation',
                  qualification='Independent Python reduction/verification path; not upstream accelerated kernel timing')
    save(root/'circuit.json', c.to_dict())
    def checkpoint(stage):
        result['stage'] = stage; save(root/'result.json', result)
    try:
        ir = prepared if prepared is not None else physical.build(c); save(root/'inventory.json', ir)
        physical.validate(c, ir, independent=True)
        result['inventory_verified'] = True; result['inventory_identity'] = ir['identity']
        result['alternatives'] = len(ir['alternatives']); result['mechanisms'] = len(ir['columns'])
        groups = (physical.memory_projection(c, sector=sector) if c.boundary_model == 'repeated_noisy_memory'
                  else [[i] for i in range(ir['detectors'])])
        reduced = physical.project(ir, groups); save(root/'projection.json', reduced)
        result['projected_mechanisms'] = len(reduced['columns']); result['projected_detectors'] = len(groups)
        checkpoint('inventory_and_projection')
        def progress(bound):
            result['producer_lower_bound']=bound
            checkpoint('projected_prefix_complete_not_yet_independently_verified')
        answer = enumerate_minima(reduced['columns'], min(5, target), work, on_progress=progress)
        save(root/'projected-enumeration.json', answer)
        checkpoint('projected_enumeration_complete')
        independent = canonical_minima(reduced['columns'], min(answer['lower_bound'], 5, target), work)
        save(root/'projected-independent.json', independent)
        if (answer['lower_bound'], answer['minima']) != (independent['lower_bound'], independent['minima']):
            raise ValueError('Independent projected enumeration disagreement')
        result['lower_bound'] = answer['lower_bound']
        result['independent'] = dict(verified=True, method='forward physical inventory and canonical residual branching')
        checkpoint('projected_minimum_verified')
        from .affine_lifting import prove as affine_prove, verify as affine_verify
        affine = affine_prove(ir, reduced, answer['minima']) if answer['minima'] else None
        if affine is not None:
            save(root/'affine-lifting.json', affine)
        if affine is not None and affine['complete']:
            if not affine_verify(ir, reduced, independent['minima'], affine):
                raise ValueError('Independent affine parity verification failed')
            result['lower_bound'] += 1
            result['independent']['lifting_verified'] = True
            result['lifting_method'] = 'affine_parity'
        elif answer['minima']:
            lifted = lift_minima(ir, reduced, answer['minima'], work_limit=work)
            save(root/'lifting.json', lifted)
            if lifted['witness'] is not None:
                witness = physical.lift_and_replay(c, ir, lifted['witness'])
                if not witness['verified']:
                    raise ValueError('Lifted physical witness failed replay')
                save(root/'witness.json', witness)
                result['upper_bound'] = witness['weight']
            else:
                from .relaxation_verify import exclude_lifts
                independent_lift = exclude_lifts(ir, reduced, independent['minima'], work)
                save(root/'lifting-independent.json', independent_lift)
                if not independent_lift['excluded']:
                    raise ValueError('Independent lifting disagreement')
                result['lower_bound'] += 1
                result['independent']['lifting_verified'] = True
        if result['upper_bound'] is not None and result['upper_bound'] < target:
            result['status'] = 'INVALID'
            result['distance_status'] = 'INVALID_TARGET'
        elif result['lower_bound'] >= target:
            result['status'] = 'CERTIFIED'
            result['distance_status'] = 'CERTIFIED_AT_LEAST_TARGET'
        if result['upper_bound'] == result['lower_bound']:
            result['exact_distance'] = result['lower_bound']
            result['distance_status'] = 'EXACT_DISTANCE'
        checkpoint('complete')
    except Incomplete as exc:
        result['reason'] = str(exc)
        # Preserve a cheaper verified prefix when the full obligation censors.
        prefix=min(4,result.get('producer_lower_bound',1))
        if prefix>result['lower_bound']:
            try:
                prefix_check=canonical_minima(reduced['columns'],prefix-1,work)
                if prefix_check['lower_bound']>=prefix:
                    result['lower_bound']=prefix
                    result['independent']=dict(verified=True,method='forward inventory and canonical prefix exclusion')
                    save(root/'independent-prefix.json',prefix_check)
            except Incomplete:pass
        result['unresolved_weights']=list(range(result['lower_bound'],target))
        checkpoint('incomplete')
    return result
