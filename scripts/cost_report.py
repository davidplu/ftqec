"""Report frozen measured source separately from final release identities."""

import json,statistics,collections,hashlib

from pathlib import Path

from ftqec.results.artifacts import save,source_identity



def read(path):return json.loads(Path(path).read_text())

def stats(rows):

    values=sorted(r["cpu"] for r in rows)

    return dict(n=len(values),total_cpu=sum(values),min_cpu=min(values),median_cpu=statistics.median(values),p90_cpu=values[min(len(values)-1,int(.9*len(values)))],max_cpu=max(values),censored=sum(r.get("censored",False) for r in rows))



def main():

    summary=read("benchmarks/policy_comparison/summary.json");study=summary["protocol"]["source"];profile=read("benchmarks/certification_costs/profile.json")["rows"];training=read("results/cost_profiles/frozen.json")["training"];audits=read("benchmarks/positive_retention/audit.json")["rows"];calibration=read("results/cost_profiles/calibration.json")["rows"]

    actions=[];frontiers=[]

    for path in Path("benchmarks/policy_comparison").glob("*/*.json"):

        outcome=read(path)

        for row in outcome["rows"]:actions+=row["actions"]

        frontiers.append(dict(code=outcome["code"],policy=outcome["policy"],common_reference_frontier=outcome["common_reference_ler_frontier"]))

    reference=[]

    for p in Path("benchmarks/positive_retention").glob("*_reference_ler.json"):reference += [r["cost"] for r in read(p)["rows"]]

    records=profile+[r for r in training if r["tier"]!="certify"]+actions+reference

    groups={}

    for row in records:

        key=row["tier"]+":"+str(row["target"])+":"+row["status"]+":"+("supported" if row.get("supported",True) else "unsupported")

        groups.setdefault(key,[]).append(row)

    distributions={key:stats(rows) for key,rows in groups.items()}

    # The separate target2 baseline labels retain CPU in calibration; do not invent missing wall/subphase receipts.

    counts=dict(compiled=11156,scaling_compiled=11100,screened=sum(r["tier"]=="screen" for r in records),simulation_batches=sum(r["tier"]=="simulation" for r in records),shots=sum(r["result"].get("shots",0) for r in records),supported_certification_actions=sum(r["tier"]=="certify" and r.get("supported",True) for r in records)+len(calibration),unsupported_actions=sum(not r.get("supported",True) for r in records))

    mae={key:statistics.mean(abs(r[key]-r["observed_cpu"]) for r in calibration if not r["censored"] and r[key] is not None) for key in ("rule_cpu","learned_cpu")}

    totals={policy:dict(cpu=sum(r["cpu"] for r in summary["rows"] if r["policy"]==policy),wall_sum=sum(r["wall"] for r in summary["rows"] if r["policy"]==policy),shots=sum(r["shots"] for r in summary["rows"] if r["policy"]==policy)) for policy in summary["protocol"]["policies"]}

    save(Path("results/compute/cost_study.json"),dict(study_source=study,release_source=source_identity(),counts=counts,distributions=distributions,policies=totals,predictor_mae=mae,baseline_label_cpu=sum(r["observed_cpu"] for r in calibration),reference_analysis_cpu=sum(r["cpu"] for r in reference),qualification="Components overlap: do not add independent/decoder subphases to their enclosing tier. Policy CPU includes orchestration and differs from summed action bodies. No fabricated project-wide CPU total; baseline labeling wall/subphase receipts were not separately retained."))

    save(Path("results/pareto/frontiers.json"),dict(source=study,rows=frontiers,qualification="Common finite-shot estimated reference for analysis only; not true LER or a distance certificate"))

    save(Path("benchmarks/population_scaling/reproduction.json"),dict(source=study,seed=982451653,mapping="seed+i for i in range(count)",input="examples/steane.json",driver="scripts/cost_study.py",scope="Reconstructible streaming compilation. Per-circuit IR was not retained for the10000 scaling-only run; full evaluated pools and proof evidence are retained."))

    lines=["# Cost-aware evaluation results","",f"Research source `{study}`, commit `5f562c0`; exact bytes in `results/cost_aware/study/scientific_source.zip`. Final release source `{source_identity()}` includes separate portability/telemetry fixes and is not substituted into these measurements.","","## Main finding","","Direct certification was cheapest on both final-family target2 pools. Cost-aware evaluation reduced fixed-funnel overhead but did not beat direct certification. No overall multi-fidelity superiority is established.","","| Family | Policy | CPU seconds | Certified positives | Shots |","|---|---|---:|---:|---:|"]

    for row in summary["rows"]:lines.append(f"| {row['code']} | {row['policy']} | {row['cpu']:.4f} | {row['certified']} | {row['shots']} |")

    lines += ["","All policies retain47 independently certified positives across two final families, with no false hard rejections or lost certified resource-Pareto points. This is deliberately conservative allocation; it does not demonstrate a powerful elimination rule. Common reference resource–LER frontiers also match, but use only256-shot estimates, not true failure probabilities. Common reference analysis has separate compute and is not an optimizer input.","","## Scaling and proof outcomes",""]

    for count in (100,1000,10000):

        d=read(f"benchmarks/population_scaling/{count}.json");lines.append(f"- {count}: {d['compiled']} compiled/noiseless-checked, {d['unique']} distinct; {d['cpu']:.3f} CPU s / {d['wall']:.3f} wall s; end RSS {d['rss']} bytes. Zero screening/simulation/certification in this scaling arm.")

    lines += ["","Input parsing is hoisted in this streaming benchmark, unlike the preserved initial compilation driver; do not claim a matched speedup against the older39.297 CPU-second result.","","Target3 profiling produced27 verified harmful-witness INVALID results and29 work-censored UNKNOWN results; no target3 positive certificate was obtained. Targets5/7/9 each have eight unsupported-method records, not proof attempts. Zero CPU ticks on the immediate unsupported branch reflect timer resolution, not free higher-distance certification.","","## Twenty requested answers",""]

    answers=[

    "Measured tier costs: complete CPU distributions and raw records are in results/compute/cost_study.json and the profiling/policy files; independent verification and decoder build/inference costs are nested components, not extra totals. Phase end RSS is not a phase peak.",

    "No general distance threshold for expensive positive certification is established. Target3 has early negative witnesses or censored work; no successful positive cost at3 or supported method at5/7/9 was measured.",

    "Direct certification is preferable on these two small target2 pools: aggregate direct CPU %.4f versus fixed %.4f and cost-aware %.4f."%(totals["direct"]["cpu"],totals["fixed"]["cpu"],totals["costaware"]["cpu"]),

    "The real optimizer's cheap cold-prior cases dispatch directly and bypass simulation (integration evidence). The trained study policy still chose too much screening: the empirical cost/rejection estimates did not make optimal decisions on final families.",

    "Actual scoped counts: "+str(counts)+". Compilation counts include repeated size-prefix runs;10000 is the largest distinct scaling pool. Certification actions include negative/censored outcomes, not just successful certificates.",

    "Relative to direct, cost-aware wasted %.4f CPU s on these fixed pools; relative to the fixed funnel it saved %.4f CPU s. This is an observed single-order comparison, not a significance-tested general improvement."%(totals["costaware"]["cpu"]-totals["direct"]["cpu"],totals["fixed"]["cpu"]-totals["costaware"]["cpu"]),

    "No false hard rejection among47 final-family certified positives. This does not establish zero population-level risk or target3 retention.",

    "No certified resource-Pareto point was lost. Valuable true-LER-frontier retention is unestablished.",

    "Common finite-shot reference resource–LER frontiers match because the certified retained sets match. Direct policy does not itself estimate LER; reference-analysis compute is separate. Do not equate external frontier containment with a complete online LER selection result.",

    "Adaptive policy used%d shots versus%d fixed-funnel shots; direct used zero. Two-look Hoeffding alpha spending preserves candidate-wise repeated-inspection coverage, not simultaneous coverage across all candidates."%(totals["costaware"]["shots"],totals["fixed"]["shots"]),

    "No predictor advantage established. Final-family cost MAE: rule %.6f CPU s; log-linear comparator %.6f CPU s. The learned predictor was not adopted."%(mae["rule_cpu"],mae["learned_cpu"]),

    "Matched actual CPU and wall complete-candidate prefix checkpoints are in benchmarks/policy_comparison/matched_compute.json; unfinished work gets no fractional credit. These are analysis checkpoints, not global runtime limits.",

    "Compilation scales to10000 as reported. Full evaluation comparisons use24 candidates per final family;1000/10000 full multi-fidelity evaluations were not run.",

    "Settings froze after training on surface/Perfect5 and before Shor/Steane outcomes. Both final CSS families favor direct certification. There is no held-out non-CSS generalization or broad superiority claim.",

    "UNKNOWN retains observed CPU and censoring reason; unsupported methods are separate. Censored observations are excluded from completion regressions. Scaled floors are heuristics, not mathematical runtime lower bounds for a different circuit. Completion quantiles beyond the censoring horizon are not identifiable here.",

    "Real local subprocess concurrency and resource stopping remain tested. Separate local/serialized-worker comparison verifies matching scientific outputs and positive lifetime overlap.",

    "The serialized worker is scientifically equivalent in the tested local environment. Remote cloud and cross-OS deployment were not demonstrated. Final release canonicalizes source path keys; exact study source predates that fix.",

    "Targets5/7/9 remain unsupported by the retained proof method. No readiness or successful lower-bound exclusion is inferred.",

    "Incomplete gates are listed below; expensive-target allocation, broad generalization, fully evaluated large populations and remote infrastructure remain unestablished.",

    "Most justified next research step: keep direct certification as the measured cheap-case baseline, then preregister a larger independently positive expensive-certification pool to calibrate expected full-path cost and rejection benefit before adopting more complex allocation models."]

    for i,a in enumerate(answers,1):lines.append(f"{i}. {a}")

    gates={"A":("PASS","640 prior evidence/package files unchanged; original repository commit unchanged"),"B":("PARTIAL","Tier CPU/wall and nested components measured; phase peaks and some baseline-label wall receipts unavailable"),"C":("PARTIAL","Real target2/3 profiles, separate unsupported5/7/9; no higher-distance positives"),"D":("PASS","Actual optimizer direct shortcut exercised; it is not universally optimal"),"E":("PASS","Prospective two-look rule, alpha spending, retained seeds and actual reduced shot counts"),"F":("PARTIAL","Working calibrated-cost route, but direct baseline is cheaper on studied pools"),"G":("PASS","Distinct archives and full conservative certified frontier retention in tested scope"),"H":("PARTIAL","47 held-out-development positives, negatives and censored profiles; true LER-frontier/target3 retention unproved"),"I":("PARTIAL","100/1000/10000 compile/noiseless scaling; full allocation populations remain24/family"),"J":("PASS","Actual CPU/wall complete-candidate prefix checkpoints; no superiority claim"),"K":("PARTIAL","Frozen two-family CSS evaluation; no held-out non-CSS generalization"),"L":("PARTIAL","Censoring/unsupported costs preserved and not imputed; censored completion prediction remains heuristic"),"M":("PASS","Actual guarded subprocesses and independently observed overlap"),"N":("PARTIAL","Portable local-worker equivalence; no authorized remote backend demonstration"),"O":("PARTIAL","Frozen source, raw task/pool/proof records and seeds; some label subphase receipts and scaling per-circuit IR not retained"),"P":("PASS","Required documentation, artifacts, manifest and separately versioned source epochs")}

    lines += ["","## Acceptance gates","","| Gate | Status | Scope |","|---|---|---|"]

    for key,(status,note) in gates.items():lines.append(f"| {key} | {status} | {note} |")

    save(Path("results/cost_aware/acceptance.json"),dict(study_source=study,release_source=source_identity(),gates={k:dict(status=v[0],scope=v[1]) for k,v in gates.items()},scientific_superiority=False))

    Path("docs/RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")



if __name__=="__main__":main()

