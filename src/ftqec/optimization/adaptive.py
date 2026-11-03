from dataclasses import asdict
from .costs import CostModel
from ..simulation.sequential import combine

def choose(row,target,model,index):
    if row.get("certify",{}).get("status") in ("CERTIFIED","INVALID"):return dict(action="retain",reason="terminal proof result")
    if row.get("screen",{}).get("status")=="FAULT_INVALID":return dict(action="reject_with_proof",reason="independently replayed harmful fault")
    operations=len(row["circuit"]["operations"])
    costs={k:asdict(model.estimate(k,operations,target)) for k in ("screen","simulation","certify")}
    cert=costs["certify"]["cpu"];screen=costs["screen"]["cpu"];sim=costs["simulation"]["cpu"]
    if cert<=screen+sim:return dict(action="certify",reason="direct_certification_cheaper_than_funnel",estimates=costs)
    if index%7==0:return dict(action="certify",reason="prospective_diversity_exploration",estimates=costs)
    benefit=model.rejection_probability()*cert-screen
    if "screen" not in row and benefit>0:return dict(action="screen",reason="positive_expected_avoided_certification_cost",estimates=costs,expected_benefit=benefit)
    if "simulation" not in row:return dict(action="simulation",reason="reliability_uncertainty",estimates=costs)
    return dict(action="certify",reason="uncertainty_retained_not_hard_rejected",estimates=costs)

def drive(rows,evaluate,state,config):
    model=CostModel(state.get("cost_observations",[]));decisions=state.setdefault("action_decisions",[])
    pending=list(rows)
    while pending:
        groups={};next_pending=[]
        for i,row in enumerate(pending):
            decision=choose(row,config.target,model,i);decisions.append(dict(candidate=row["id"],**decision))
            action=decision["action"]
            if action in ("retain","reject_with_proof"):continue
            groups.setdefault(action,[]).append(row)
        for action,group in groups.items():
            evaluate(group,action,config.initial_shots if action=="simulation" else 0)
            for row in group:
                if action=="simulation" and "shots" in row["simulation"]:
                    row["simulation_batches"]=[row["simulation"]];row["simulation"]=combine(row["simulation_batches"])
                    if row["simulation"]["confidence"][1]-row["simulation"]["confidence"][0]>.2:
                        evaluate([row],"simulation",config.further_shots,10**10)
                        if "shots" in row["simulation"]:row["simulation_batches"].append(row["simulation"])
                        row["simulation"]=combine(row["simulation_batches"])
                    row["simulation"]["stopping_rule"]="width<=0.2 or two prospective looks; preserve remaining uncertainty"
                # Failed/UNKNOWN tasks are retained; never spin on a censored action.
                if row[action].get("status")=="UNKNOWN":row["retention"]="UNCERTAIN";continue
                if action!="certify":next_pending.append(row)
        pending=next_pending;model=CostModel(state.get("cost_observations",[]))
