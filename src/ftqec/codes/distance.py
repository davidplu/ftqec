"""Algebraic code-distance lower proofs for graph-eligible Pauli channels."""
from .pauli import Pauli
from .logicals import logical_basis, logical_effect
from ..certification.structural import graph, produce, check
from ..architectures.synthesis import channel_masks, Effects
from ..results.artifacts import digest, source_identity


def certify_code(code, target, work=20000000):
    if type(target) is not int or target < 1: raise ValueError("Positive target required")
    pairs = logical_basis(code); masks = channel_masks(code)
    upper = min((p for pair in pairs for p in pair), key=lambda p:p.weight)
    result = dict(code=code.input_hash, source=source_identity(), target=target,
                  upper_bound=upper.weight, upper_witness=str(upper), status="UNKNOWN",
                  scope="algebraic data Pauli distance, separate from circuit distance")
    if not masks: return dict(result, reason="graph channel ineligible")
    values = []
    for q in range(code.n):
        for axis in "XYZ":
            p = Pauli(code.n, (1 << q) if axis in "XY" else 0, (1 << q) if axis in "YZ" else 0)
            values.append((code.syndrome(p), logical_effect(p, pairs)))
    channels = []
    for bit, selected in enumerate(masks):
        g = graph(Effects(values), selected, bit)
        if g is None: return dict(result, reason="data Pauli channel is not graphlike")
        proof = produce(g, target, work_limit=work)
        if not proof["complete"] or proof["lower_bound"]<target:
            return dict(result, reason="requested algebraic lower bound not proved")
        channels.append(dict(bit=bit, masks=selected, graph_hash=digest(g), **proof))
    result.update(status="CERTIFIED", lower_bound=target, channels=channels)
    result["independent"] = verify_code(code, result)
    if not result["independent"]["verified"]:result.update(status="UNKNOWN", lower_bound=1)
    elif upper.weight==target:result["exact_distance"]=target
    return result


def verify_code(code, certificate):
    if certificate.get("code")!=code.input_hash or certificate.get("source")!=source_identity():
        return dict(verified=False, reason="identity")
    target=certificate.get("target")
    if type(target) is not int or target<1 or certificate.get("lower_bound")!=target:return dict(verified=False)
    pairs=logical_basis(code); channels=certificate.get("channels",[])
    if sorted(x["bit"] for x in channels)!=list(range(2*code.k)):return dict(verified=False)
    # Rebuild every single-data-Pauli syndrome/logical label directly from strings.
    strings=list(map(str,code.generators)); values=[]
    logicals=[str(p) for x,z in pairs for p in (z,x)]
    for q in range(code.n):
        for axis in "XYZ":
            anticommutes=lambda text:text[q]!="I" and text[q]!=axis
            d=sum(int(anticommutes(g))<<i for i,g in enumerate(strings))
            l=sum(int(anticommutes(p))<<i for i,p in enumerate(logicals))
            values.append((d,l))
    for item in channels:
        if any(type(m) is not int or m<0 or m>>len(strings) for m in item["masks"]):return dict(verified=False)
        g=graph(Effects(values),item["masks"],item["bit"])
        if g is None or digest(g)!=item["graph_hash"] or not check(g,item,target):return dict(verified=False)
    upper=Pauli.parse(certificate["upper_witness"])
    if upper.n!=code.n or upper.weight!=certificate["upper_bound"] or code.syndrome(upper) or code.is_stabilizer(upper) or upper.weight<target:return dict(verified=False)
    return dict(verified=True, method="independent string Pauli inventory and integer potentials", lower_bound=target)
