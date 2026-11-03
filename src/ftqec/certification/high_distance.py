"""Progressive exact extraction-distance certification, source-bound and independently checked."""
import time
from .inventory import backward,forward,fault_at
from .structural import graph,produce,check,projections,dp
from .exact import MODEL,SCOPE
from ..faults.verification import replay,verify_witness
from ..results.artifacts import digest,source_identity


def negative(c,ids):
    if not ids:return None
    faults=[fault_at(c,int(op),label).to_dict() for op,label in ids]
    if len({f["location"] for f in faults})!=len(faults):return None
    actual=replay(c,faults);w=dict(faults=faults,fault_count=len(faults),**actual)
    return w if verify_witness(c,w)["verified"] else None

def logical_upper_witness(c):
    from ..codes.logicals import logical_basis
    last={q:i for i,op in enumerate(c.operations) if op.gate not in ("M","BARRIER") for q in op.qubits if q<c.code.n}
    found=[]
    for pair in logical_basis(c.code):
        for p in pair:
            grouped={};valid=True
            for q,label in enumerate(str(p)):
                if label=="I":continue
                if q not in last:valid=False;break
                i=last[q];op=c.operations[i];labels=grouped.setdefault(i,["I"]*len(op.qubits));labels[op.qubits.index(q)]=label
            if valid:
                witness=negative(c,[(i,"".join(labels)) for i,labels in grouped.items()])
                if witness:found.append(witness)
    return min(found,key=lambda w:len(w["faults"])) if found else None

def pairs(inv):
    groups={}
    for op,label,d,l,data in inv.rows():
        if not d and l:return 1,[(op,label)]
        items=groups.setdefault(d,[])
        # At most three representatives suffice for the two-coordinate inequality test.
        for old_l,old_op,old_label in items:
            if l!=old_l and op!=old_op:return 2,[(old_op,old_label),(op,label)]
        if len(items)<3 and not any(l==a and op==b for a,b,c in items):items.append((l,op,label))
    return 3,None

def independent_pairs(inv):
    # Separate ordered detector scan, different from producer representative search.
    c=inv.connection;c.execute("CREATE INDEX IF NOT EXISTS effects ON entries(d,l,op)")
    previous=None;logic=location=None;different_l=different_loc=False
    for d,l,op in c.execute("SELECT d,l,op FROM entries ORDER BY d,l,op"):
        if int(d,16)==0 and int(l,16):return 1
        if d!=previous:previous=d;logic=l;location=op;different_l=different_loc=False
        different_l|=l!=logic;different_loc|=op!=location
        if different_l and different_loc:return 2
    return 3

def independent_dp(inv,target,work_limit,state_limit=100000):
    groups={}
    for op,label,d,l,data in inv.rows():groups.setdefault(op,[]).append((d,l))
    locations=list(groups);future=[0]*(len(locations)+1)
    for i in range(len(locations)-1,-1,-1):
        future[i]=future[i+1]
        for d,l in groups[locations[i]]:future[i]|=d
    if inv.count>50000:return False
    max_weight=min(target-1,len(locations))
    levels=[{(0,0)}]+[set() for _ in range(max_weight)];work=0
    for i,op in enumerate(locations):
        new=[{(d,l) for d,l in level if not d&~future[i+1]} for level in levels]
        for weight in range(max_weight):
            for d,l in levels[weight]:
                for dd,ll in groups[op]:
                    work+=1
                    if work>work_limit:return False
                    nd=d^dd
                    if not nd&~future[i+1]:new[weight+1].add((nd,l^ll))
        if sum(map(len,new))>state_limit:return False
        levels=new
    return not any(l for level in levels for d,l in level if not d)

def certify(c,target=3,work=200000,directory=None,method="auto"):
    if method not in ("auto","graph","dp","mitm","sat","decomposition","decomposition_legacy","decomposition_span"):
        raise ValueError("Unsupported proof method: "+str(method))
    if type(target) is not int or target<1:raise ValueError("Requested target must be a positive integer")
    from ..screening.structural import check as structural_check
    structural_check(c)
    base=dict(circuit=digest(c.to_dict()),source=source_identity(),fault_model=MODEL,scope=SCOPE,target=target,requested_target=target)
    if c.boundary_model!="ideal_initial_and_final_syndrome" or c.code.k<1:return dict(base,status="UNKNOWN",lower_bound=1,unresolved=["unsupported task semantics"])
    inv=backward(c)
    try:
        if target==1:
            result=dict(base,status="CERTIFIED",lower_bound=1,proof=dict(method="zero_fault",inventory_hash=inv.hash,inventory_count=inv.count))
            result["independent"]=verify(c,result,work)
            if not result["independent"]["verified"]:result["status"]="UNKNOWN";result["unresolved"]=[result["independent"]]
            return result
        lower,ids=pairs(inv);proof=dict(method="pairs",inventory_hash=inv.hash,inventory_count=inv.count);witness=negative(c,ids) if ids else None
        if witness and len(witness["faults"])<target:
            return dict(base,status="INVALID",lower_bound=1,producer_lower_bound=lower,upper_bound=len(witness["faults"]),witness=witness,independent=verify_witness(c,witness),proof=proof)
        candidate_upper=logical_upper_witness(c)
        if candidate_upper and len(candidate_upper["faults"])<target:
            return dict(base,status="INVALID",lower_bound=1,producer_lower_bound=lower,upper_bound=len(candidate_upper["faults"]),witness=candidate_upper,proof=dict(proof,negative_method="logical support physical replay"),independent=verify_witness(c,candidate_upper))
        if target<=3 and method not in ("decomposition","decomposition_legacy","decomposition_span"):
            result=dict(base,status="CERTIFIED",lower_bound=target,proof=proof)
        else:
            channels=[];graph_lower=target
            for bit,choices in (projections(c).items() if method in ("auto","graph") else []):
                best=None
                for masks in choices:
                    g=graph(inv,masks,bit)
                    if g is None:continue
                    p=produce(g,target,checkpoint=(str(directory)+"/"+digest(base)+"/bit"+str(bit)+"/"+digest(masks)) if directory else None,work_limit=work)
                    if not p["complete"]:continue
                    candidate=dict(bit=bit,masks=masks,graph_hash=digest(g),**p)
                    if best is None or candidate["lower_bound"]>best["lower_bound"]:best=candidate
                    w=negative(c,p.get("relaxed_witness"))
                    if w and len(w["faults"])<target:return dict(base,status="INVALID",lower_bound=1,producer_lower_bound=3,upper_bound=len(w["faults"]),witness=w,proof=proof,independent=verify_witness(c,w))
                    if p["lower_bound"]>=target:break
                if best is None:channels=[];break
                channels.append(best);graph_lower=min(graph_lower,best["lower_bound"])
            if channels and graph_lower>=target:
                result=dict(base,status="CERTIFIED",lower_bound=target,proof=dict(proof,method="graph_potentials",channels=channels))
            else:
                lower=min(3,target);dp_parts=[];accepted_proof=proof
                if channels and graph_lower>lower:
                    lower=graph_lower
                    for channel in channels:
                        channel["potentials"]=[[min(x,lower) for x in row] for row in channel["potentials"]];channel["lower_bound"]=lower
                    accepted_proof=dict(proof,method="graph_potentials",channels=channels)
                if method in ("auto","decomposition","decomposition_legacy","decomposition_span"):
                    from . import decomposition,span_decomposition,quotient_decomposition
                    backend=decomposition if method=="decomposition_legacy" else span_decomposition if method=="decomposition_span" else quotient_decomposition
                    p=backend.prove(inv,target,work);dp_parts.append(p)
                    if p.get("witness"):
                        w=negative(c,p["witness"])
                        if w:return dict(base,status="INVALID",lower_bound=1,producer_lower_bound=lower,upper_bound=len(w["faults"]),witness=w,proof=p,independent=verify_witness(c,w))
                    elif p["complete"]:lower=target;accepted_proof=p
                if method=="sat":
                    from . import sat
                    p=sat.prove(inv,target,work);dp_parts.append(p)
                    if p.get("witness"):
                        w=negative(c,p["witness"])
                        if w:return dict(base,status="INVALID",lower_bound=1,producer_lower_bound=lower,upper_bound=len(w["faults"]),witness=w,proof=p,independent=verify_witness(c,w))
                    elif p["complete"]:lower=target;accepted_proof=p
                if method in ("auto","mitm") and lower<target:
                    from . import mitm
                    p=mitm.prove(inv,target,work,directory,start_weight=3)
                    dp_parts.append(p)
                    if p.get("witness"):
                        w=negative(c,p["witness"])
                        if w:return dict(base,status="INVALID",lower_bound=1,producer_lower_bound=lower,upper_bound=len(w["faults"]),witness=w,proof=p,independent=verify_witness(c,w))
                    if p["lower_bound"]>lower:
                        lower=p["lower_bound"];accepted_proof=p
                for milestone in (sorted({min(target,x) for x in range(4,target+1) if min(target,x)>lower}) if method in ("auto","dp") else []):
                    p=dp(inv,milestone,work_limit=work);dp_parts.append(dict(target=milestone,**p))
                    if p.get("witness"):
                        w=negative(c,p["witness"])
                        if w:return dict(base,status="INVALID",lower_bound=1,producer_lower_bound=lower,upper_bound=len(w["faults"]),witness=w,proof=proof,independent=verify_witness(c,w))
                    if not p["complete"]:break
                    lower=milestone;accepted_proof=dict(proof,method="dp",dp_parts=list(dp_parts))
                result=dict(base,status="CERTIFIED" if lower>=target else "UNKNOWN",lower_bound=lower,proof=accepted_proof,progress=dp_parts,unresolved=[] if lower>=target else [dict(first_weight=lower,last_weight=target-1,reason="selected exact methods incomplete; inspect progress and work limits")])
        tick=time.perf_counter();cpu=time.process_time();checked=verify(c,result,work);result["independent_cost"]=dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-tick);result["independent"]=checked
        if not checked["verified"]:result["status"]="UNKNOWN";result["lower_bound"]=1;result["unresolved"]=[checked]
        if result["status"]=="CERTIFIED":
            upper=candidate_upper
            if upper:
                result["upper_bound"]=len(upper["faults"]);result["upper_witness"]=upper;result["upper_independent"]=verify_witness(c,upper)
                if result["upper_bound"]<target:raise ArithmeticError("Positive lower proof contradicts independently replayed logical witness")
                if result["upper_bound"]==target:result["exact_distance"]=target
        result["milestones"]=list(range(1,result["lower_bound"]+1))
        return result
    finally:inv.close()

def verify(c,cert,work=200000):
    if cert.get("circuit")!=digest(c.to_dict()) or cert.get("source")!=source_identity() or cert.get("fault_model")!=MODEL or cert.get("scope")!=SCOPE:return dict(verified=False,reason="identity")
    target=cert.get("target")
    if type(target) is not int or target<1 or cert.get("requested_target",target)!=target:return dict(verified=False,reason="target")
    from ..screening.structural import check as structural_check
    structural_check(c)
    if digest(c.to_dict())!=cert["circuit"]:return dict(verified=False,reason="circuit changed during ideal validation")
    if c.boundary_model!="ideal_initial_and_final_syndrome" or c.code.k<1:return dict(verified=False,reason="task semantics")
    if "exact_distance" in cert and (cert["status"]!="CERTIFIED" or cert["exact_distance"]!=target or cert.get("upper_bound")!=target):return dict(verified=False,reason="exact-distance claim")
    if cert["status"]=="INVALID":
        if cert.get("lower_bound")!=1 or cert.get("upper_bound")!=len(cert.get("witness",{}).get("faults",[])):return dict(verified=False,reason="negative bound claim")
        if not cert.get("witness") or len(cert["witness"]["faults"])>=target:return dict(verified=False,reason="upper witness does not violate target")
        return verify_witness(c,cert["witness"])
    if cert["status"] not in ("CERTIFIED","UNKNOWN"):return dict(verified=False,reason="status")
    if cert["status"]=="CERTIFIED" and cert.get("lower_bound")!=target:return dict(verified=False,reason="target not established")
    if "upper_bound" in cert:
        upper=cert.get("upper_witness")
        if not upper or len(upper["faults"])!=cert["upper_bound"] or cert["upper_bound"]<target or not verify_witness(c,upper)["verified"]:return dict(verified=False,reason="upper witness")
    inv=forward(c)
    try:
        proof=cert["proof"]
        if proof.get("inventory_hash")!=inv.hash or proof.get("inventory_count")!=inv.count:return dict(verified=False,reason="independent_inventory_mismatch")
        bound=target if cert["status"]=="CERTIFIED" else cert.get("lower_bound",1)
        if type(bound) is not int or not 1<=bound<=target:return dict(verified=False,reason="bound")
        method=proof["method"]
        if target==1:return dict(verified=method=="zero_fault" and bound==1,lower_bound=1,inventory_count=inv.count,method="independent inventory and zero-fault semantics")
        if method=="pairs":
            achieved=independent_pairs(inv);return dict(verified=bound<=3 and achieved>=bound,lower_bound=min(achieved,bound),method="independent ordered pair scan",inventory_count=inv.count)
        from . import decomposition,span_decomposition,quotient_decomposition
        if method==quotient_decomposition.VERSION:return quotient_decomposition.verify(inv,proof,bound,work)
        if method==span_decomposition.VERSION:return span_decomposition.verify(inv,proof,bound,work)
        if method==decomposition.VERSION:return decomposition.verify(inv,proof,bound,work)
        from . import sat
        if method==sat.VERSION:return sat.verify(inv,proof,bound,work)
        from . import mitm
        if method==mitm.VERSION:
            if proof.get("start_weight")!=3 or independent_pairs(inv)<3:
                return dict(verified=False,reason="MITM singleton/pair prefix")
            return mitm.verify(inv,proof,bound,work)
        if method=="dp":return dict(verified=independent_dp(inv,bound,work),lower_bound=bound,method="independent per-weight suffix-support DP",inventory_count=inv.count)
        if method!="graph_potentials":return dict(verified=False,reason="unknown recipe")
        channels=proof.get("channels",[])
        if sorted(p["bit"] for p in channels)!=list(range(2*c.code.k+len(c.observables))):return dict(verified=False,reason="logical coverage")
        nd=len(c.detectors)+len(c.code.generators)
        for p in channels:
            if any(type(m) is not int or m<0 or m>>nd for m in p["masks"]):return dict(verified=False,reason="projection")
            g=graph(inv,p["masks"],p["bit"])
            if g is None or digest(g)!=p["graph_hash"] or p["lower_bound"]<bound or not check(g,p,bound):return dict(verified=False,reason="graph/potential/root coverage")
        return dict(verified=True,lower_bound=bound,method="independent forward inventory and integer edge inequalities",inventory_count=inv.count)
    finally:inv.close()
