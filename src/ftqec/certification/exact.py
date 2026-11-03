import time
from itertools import combinations
from ..faults.signatures import signatures,signatures_forward
from ..faults.search import search_faults
from ..faults.verification import verify_witness,replay
from ..results.artifacts import digest,source_identity

MODEL="operation-local uniform Pauli alternatives; measurement flips; explicit gates only; perfect code-space boundaries"
SCOPE="detector_model_with_ideal_initial_and_final_syndrome_not_complete_physical_memory"

def screen(c,work=100000,target=3):
    if type(target) is not int or target<1:raise ValueError("Positive target required")
    if target==1:return dict(status="NO_WITNESS_FOUND",scope=SCOPE,work=0,reason="No positive fault weights below target one")
    from .inventory import backward,fault_at
    inv=backward(c);examined=0
    try:
        for op,label,d,l,data in inv.rows():
            if examined>=work:break
            examined+=1
            if d or not l:continue
            faults=[fault_at(c,op,label).to_dict()];actual=replay(c,faults)
            witness=dict(faults=faults,fault_count=1,**actual);v=verify_witness(c,witness)
            if not v["verified"]:raise ValueError("Independent witness replay failed")
            return dict(status="FAULT_INVALID",witness=witness,verification=v,scope=SCOPE,work=examined)
        return dict(status="NO_WITNESS_FOUND",scope=SCOPE,work=examined,complete=examined==inv.count)
    finally:inv.close()


def legacy_certify(c,target=3,work=200000):
    if not 2<=target<=4:raise ValueError("Supported target range 2..4")
    if c.code.k==0:return dict(status="UNKNOWN",reason="No encoded logical degrees of freedom",scope=SCOPE)
    from ..screening.structural import check
    check(c)
    ss=signatures(c);result=search_faults(c,ss,target-1,work)
    cert=dict(circuit=digest(c.to_dict()),source=source_identity(),fault_model=MODEL,scope=SCOPE,target=target,result=result)
    cert["status"]="INVALID" if result["witness"] else "CERTIFIED" if result["excluded_through"]>=target-1 else "UNKNOWN"
    tick=time.perf_counter();cpu=time.process_time()
    cert["independent"]=legacy_verify(c,cert,work)
    cert["independent_cost"]=dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-tick)
    if not cert["independent"]["verified"]:cert["status"]="UNKNOWN"
    return cert

def legacy_verify(c,cert,work=200000):
    if type(cert.get("target")) is not int or not 2<=cert["target"]<=4:return dict(verified=False,reason="target")
    if cert["circuit"]!=digest(c.to_dict()) or cert["source"]!=source_identity() or cert["fault_model"]!=MODEL or cert["scope"]!=SCOPE:return dict(verified=False,reason="identity")
    if cert["status"]=="INVALID":return verify_witness(c,cert["result"]["witness"])
    if cert["status"]!="CERTIFIED":return dict(verified=False,reason="producer incomplete")
    # Distinct forward propagation inventory and ungrouped exhaustive combinations.
    rows=signatures_forward(c);count=0
    for w in range(1,cert["target"]):
        for group in combinations(rows,w):
            if len({s.fault.location for s in group})!=w:continue
            count+=1
            if count>work:return dict(verified=False,reason="independent_work_limit",examined=count-1)
            d=l=0
            for s in group:d^=s.detectors;l^=s.logical
            if not d and l:return dict(verified=False,reason="counterexample")
    return dict(verified=True,examined=count,method="forward_effects_ungrouped_exhaustion")

def certify(c,target=3,work=200000,directory=None,method="auto"):
    from .high_distance import certify as high
    out=high(c,target,work,directory,method)
    out["result"]=dict(status="UPPER_BOUND" if out["status"]=="INVALID" else "LOWER_BOUND" if out.get("lower_bound",1)>1 else "UNRESOLVED",lower_bound=out.get("lower_bound",1),upper_bound=out.get("upper_bound"),excluded_through=out.get("lower_bound",1)-1,witness=out.get("witness"),reason=out.get("unresolved"),requested_weight=target-1)
    return out

def verify(c,cert,work=200000):
    if "proof" not in cert:return legacy_verify(c,cert,work)
    if "result" in cert:
        summary=cert["result"]
        if summary.get("lower_bound")!=cert.get("lower_bound") or summary.get("upper_bound")!=cert.get("upper_bound") or summary.get("witness")!=cert.get("witness") or summary.get("excluded_through")!=cert.get("lower_bound",1)-1 or summary.get("requested_weight")!=cert.get("target",1)-1:return dict(verified=False,reason="inconsistent bound summary")
    from .high_distance import verify as high
    return high(c,cert,work)
