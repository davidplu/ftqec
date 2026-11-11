"""Opt-in portable proof recipe for the physical row-relaxation backend."""
import json
import tempfile
from pathlib import Path
from . import mechanism_ir as physical
from .relaxation import canonical_minima, Incomplete
from .relaxation_verify import exclude_lifts
from ..results.artifacts import digest, source_identity

VERSION = 'physical-row-relaxation-1'


def verify(c, cert, work=50000000):
    from .exact import contract
    from ..faults.verification import verify_witness
    model, scope = contract(c)
    if (cert.get('circuit'), cert.get('source'), cert.get('fault_model'), cert.get('scope')) != (digest(c.to_dict()), source_identity(), model, scope):
        return dict(verified=False, reason='identity')
    try:
        proof = cert['proof']; ir = physical.build(c, independent=True)
        if proof['inventory_hash'] != ir['inventory_hash'] or proof['inventory_count'] != len(ir['alternatives']):
            return dict(verified=False, reason='inventory')
        projected = physical.project(ir, proof['groups'])
        bound = cert['lower_bound']
        # A lower bound d only needs exclusion through d-1. Searching through
        # the requested target can censor a perfectly sufficient partial proof.
        check = (canonical_minima(projected['columns'], min(5, bound-1), work)
                 if bound > 1 else dict(lower_bound=1, minima=[]))
        lower = check['lower_bound']
        if bound > lower:
            from .affine_lifting import verify as affine_verify
            excluded = (affine_verify(ir, projected, check['minima'], proof['affine_lifting'])
                        if 'affine_lifting' in proof else
                        exclude_lifts(ir, projected, check['minima'], work)['excluded'])
            if not check['minima'] or bound != lower+1 or not excluded:
                return dict(verified=False, reason='lifting')
            lower += 1
        if bound > lower:
            return dict(verified=False, reason='lower_bound')
        upper = cert.get('upper_bound')
        if upper is not None:
            witness = cert.get('witness')
            if not witness or len(witness['faults']) != upper or not verify_witness(c, witness)['verified']:
                return dict(verified=False, reason='physical witness')
        valid = (cert['status'] != 'CERTIFIED' or bound >= cert['target']) and (cert['status'] != 'INVALID' or upper is not None and upper < cert['target'])
        lifting='affine parity lifting' if 'affine_lifting' in proof else 'layered lifting'
        return dict(verified=valid, lower_bound=bound, method='forward inventory/canonical branching/'+lifting)
    except (Incomplete, KeyError, ValueError, TypeError) as exc:
        return dict(verified=False, reason=str(exc))


def certify(c, target, work, directory=None, prepared=None):
    from .exact import contract
    from .relaxation_backend import run
    from ..screening.structural import check
    check(c)
    if type(target) is not int or target < 1:
        raise ValueError('Positive target required')
    if directory is None:
        with tempfile.TemporaryDirectory() as root:
            return certify(c, target, work, root, prepared)
    root = Path(directory)
    raw = run(c, target, root, work, sector=c.boundary_model == 'repeated_noisy_memory', prepared=prepared)
    model, scope = contract(c)
    cert = dict(raw, fault_model=model, scope=scope, requested_target=target)
    ir = json.loads((root/'inventory.json').read_text())
    projection = json.loads((root/'projection.json').read_text())
    cert['proof'] = dict(method=VERSION, groups=projection['groups'], inventory_hash=ir['inventory_hash'], inventory_count=len(ir['alternatives']))
    if raw.get('lifting_method') == 'affine_parity':
        cert['proof']['affine_lifting'] = json.loads((root/'affine-lifting.json').read_text())
    if cert.get('upper_bound') is not None:
        witness = json.loads((root/'witness.json').read_text())
        cert['witness'] = dict(witness, fault_count=witness['weight'])
    if cert['status'] in ('CERTIFIED', 'INVALID'):
        cert['independent'] = verify(c, cert, work)
        if not cert['independent']['verified']:
            cert['unresolved'] = [cert['independent']]
            from ..faults.verification import verify_witness
            if (cert.get('upper_bound') is not None and cert['upper_bound'] < target
                    and verify_witness(c, cert['witness'])['verified']):
                # A legal negative witness takes precedence over incomplete
                # lower-bound verification; never retain an unchecked bound.
                cert['producer_lower_bound'] = cert['lower_bound']
                cert['lower_bound'] = 1
                cert.pop('exact_distance', None)
                cert['status'] = 'INVALID'; cert['distance_status'] = 'INVALID_TARGET'
                cert['independent'] = verify(c, cert, work)
            else:
                cert['status'] = 'UNKNOWN'
    return cert
