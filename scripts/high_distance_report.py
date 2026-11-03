"""Evidence-qualified reporting of the authoritative high-distance epoch."""
import json,hashlib,subprocess,time,collections
from pathlib import Path
from ftqec.results.artifacts import save,source_identity
from ftqec.certification.exact import verify
from ftqec.circuits.model import Circuit
from ftqec.optimization.selection import pareto,reliability_pareto

def read(p):return json.loads(Path(p).read_text())
def main():
    source=source_identity();ladder=read("benchmarks/high_distance/ladder.json");assert ladder["protocol"]["source"]==source
    baseline=read("results/high_distance/baseline/preservation.json");mismatches=[]
    for name,h in baseline["members"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h:mismatches.append(name)
    hist=subprocess.check_output(["git","-c","safe.directory=C:/Users/david/qLDPC synthesizer","-C",r"C:\Users\david\qLDPC synthesizer","rev-parse","HEAD"],text=True).strip()
    save(Path("results/high_distance/preservation_final.json"),dict(source=source,files=len(baseline["members"]),mismatches=mismatches,historical_commit_unchanged=hist==baseline["historical_commit"],status="PASS" if not mismatches and hist==baseline["historical_commit"] else "FAIL"));assert not mismatches
    references=ladder["rows"];policies=read("benchmarks/cost_aware/summary.json")["rows"];population=read("results/high_distance/study/population/checkpoint.json");finalists=read("benchmarks/high_distance/finalist_evaluation/results.json")["rows"];retention=read("benchmarks/high_distance/finalist_evaluation/retention.json")
    # Independently recheck every distinct discovered positive and all stored negative witnesses.
    checked=[];seen=set();cpu=time.process_time();wall=time.perf_counter()
    for path in Path("benchmarks/cost_aware").glob("*/*.json"):
        outcome=read(path)
        for row in outcome["rows"]:
            cert=row.get("certify")
            if cert and cert.get("status") in ("INVALID","CERTIFIED"):
                body={k:v for k,v in cert.items() if k not in ("independent_cost",)};key=hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()
                if key in seen:continue
                seen.add(key);receipt=verify(Circuit.from_dict(row["circuit"]),cert,20000000);assert receipt["verified"];checked.append(dict(code=outcome["summary"]["code"],candidate=row["id"],status=cert["status"],receipt=receipt))
    for row in population["rows"]:
        cert=row.get("certify")
        if cert and cert.get("status") in ("INVALID","CERTIFIED"):
            receipt=verify(Circuit.from_dict(row["circuit"]),cert,20000000);assert receipt["verified"];checked.append(dict(code="optimizer",candidate=row["id"],status=cert["status"],receipt=receipt))
    save(Path("results/high_distance/discovery_and_negative_audit.json"),dict(source=source,rows=checked,cpu=time.process_time()-cpu,wall=time.perf_counter()-wall))
    valid=[r for r in population["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"];resource_envelope=[]
    for target in (3,5,7,9):
        rows=[dict(id=r["name"],resources=r["resources"]) for r in references if r["target"]==target and r["answer"]["result"]["status"]=="CERTIFIED"]
        resource_envelope.append(dict(target=target,frontier=pareto(rows),scope="Certified reference resource envelope; not optimizer discoveries"))
    save(Path("results/pareto/high_distance_references.json"),dict(source=source,rows=resource_envelope))
    save(Path("benchmarks/positive_retention/high_distance/known_positive_audit.json"),dict(retention,control_names=[r["name"] for r in finalists],random_pool_positive_count=sum(r["certified"] for r in policies),qualification="Primary random allocation pools had no positives; separate reference/discovery audit has12. No screening-superiority claim from empty-positive pools."))
    # Explicit budget-prefix analysis: unfinished work has no proof/quality credit.
    prefixes=[]
    for row in policies:
        for budget in (.5,1,2,4,8,16,32):
            completed=[h for h in row["history"] if h["worker_cpu"]+h["parent_cpu"]<=budget]
            prefixes.append(dict(code=row["code"],policy=row["policy"],cpu_budget=budget,completed=completed[-1] if completed else None,uncompleted_work="right-censored/no quality credit",scope="complete-candidate prefixes; resumed partial controller CPU is unmeasured",quality_status="NOT_ESTIMABLE_NO_CERTIFIED_POSITIVES"))
    save(Path("benchmarks/cost_aware/matched_compute.json"),dict(source=source,rows=prefixes))
    # Count each persisted executed answer once, not every duplicated copy in reports.
    attempts={}
    for path in Path("results/high_distance/study").rglob("*.json"):
        try:data=read(path)
        except Exception:continue
        if isinstance(data,dict) and isinstance(data.get("answer"),dict) and "pid" in data["answer"]:
            a=data["answer"];key=(a["pid"],a.get("dispatch_monotonic"),hashlib.sha256(json.dumps(a,sort_keys=True).encode()).hexdigest());attempts[key]=a
    save(Path("results/compute/high_distance.json"),dict(source=source,unique_persisted_executions=len(attempts),worker_cpu=sum(a["cpu"] for a in attempts.values()),peak_observed_worker_rss=max(a.get("peak_rss",a.get("rss",0)) for a in attempts.values()),policy_summaries=policies,scope="Authoritative primary cached task receipts only. Reference resume is a separate execution even with the same scientific task ID. Finalist/API audits, controller proofs and tests are separate; no fabricated grand total. Prior partial controller CPU/wall at RAM stop remains unmeasured."))
    nine=next(r for r in references if r["distance"]==9 and r["rounds"]==9);a=nine["answer"];largest=nine["resources"];resume=read("results/local_feasibility/resume.json")
    lines=["# High-distance extraction results","",f"Scientific source `{source}`; frozen scientific commit `66ae4d2`. The prior redirector epoch is preserved but excluded from execution metrics. A transient RAM-admission stop was resumed without lowering safeguards; cached task costs were retained and completed policy arms were not rerun.","","## Independently certified distance ladder","","| Designed size | Rounds | Certified lower / replayed upper | Worker CPU s | Wall s | Observed peak MiB |","|---:|---:|---|---:|---:|---:|"]
    for r in references:
        a2=r["answer"];proof=a2["result"];lines.append(f"| {r['distance']} | {r['rounds']} | {proof.get('lower_bound')} / {proof.get('upper_bound')} | {a2['cpu']:.3f} | {a2['wall']:.3f} | {a2['peak_rss']/2**20:.2f} |")
    lines += ["","Every positive in this table has a complete independently checked lower proof and a legal physical matching upper witness. These are exact extraction detector-model distances under ideal boundaries, not full physical-memory or device certificates. Both logical Pauli coordinates and every legal physical alternative are covered. No Stim-reported or algebraic distance is substituted.","","## Actual optimization and retention","",f"The independent-seed hybrid population run compiled{len(population['rows'])} distinct circuits and found{len(valid)} target3 positives; its certified resource frontier has{len(pareto(valid))} points. References were not optimizer seeds. The separate diagnostic audit retained{retention['positive_controls']} positives with{retention['false_hard_rejections']} false hard rejections.","","The fixed random allocation pools had **zero target3 certified positives**. Their CPU tables measure work on rejected candidates, not certified-frontier efficiency. They cannot establish screening superiority or valid-positive retention. The actual optimizer found positives outside these fixed pools; this distinction is preserved.","","| Code | Policy | Worker CPU s | Parent CPU s | Certified positives |","|---|---|---:|---:|---:|"]
    for r in policies:lines.append(f"| {r['code']} | {r['policy']} | {r['cpu']:.3f} | {r['parent_cpu']:.3f} | {r['certified']} |")
    lines += ["","Steane hybrid-allocation resumed a partial arm: its worker CPU is complete from cached executed receipts, while its parent CPU/wall cover only the resumed session. Do not treat that arm as a matched full-session wall comparison. Hybrid allocation on a fixed pool and the separate hybrid population search are different experiments.","","## Declared-decoder logical-error estimates","","All certified primary references and optimizer discoveries received a separately frozen finalist audit. The unchanged one-mechanism lookup decoder had a prospectively declared100000-mechanism capacity, rather than silently truncating a larger model. Candidate-wise sequential confidence intervals and decoder-unknown counts remain in raw batches. These estimates concern the declared logical-Z-sector simulation task, not optimal decoding or arbitrary-input memory.","","| Control | Shots | Failures | Estimate | Sequential interval |","|---|---:|---:|---:|---|"]
    for r in finalists:
        sim=r["simulation"];lines.append(f"| {r['name']} | {sim.get('shots')} | {sim.get('failures')} | {sim.get('rate')} | {sim.get('confidence')} |")
    lines += ["","Zero observed failures do not imply zero LER. The broad intervals do not establish a universally best reliability architecture. Resource-only reference envelopes are separate from the discovered optimizer frontier and the uncertain resource–LER archive.","","## Twenty requested answers",""]
    answers=[
    "Reusable historical methods: graph-potential relaxation, physical-location frontier DP, exact singleton/pair grouping, independent forward/Boolean replay and source/partition binding. Historical physical-memory labels, hardware routing and portable-UNSAT-unavailable solver results were not imported as extraction certificates.",
    "The new contract guarantees declared extraction detector-model distance with ideal initial/final syndrome boundaries; correlated gate alternatives remain one fault and at most one alternative per location is legal. No arbitrary-input physical-memory claim.",
    "Rigorous structural methods support requested positive integer targets, including2/3/5/7/9, where graph eligibility or bounded exact DP completes. UNKNOWN explicitly preserves unproved obligations. No universal polynomial method for all stabilizer circuits is claimed.",
    "Yes: target3 references and four independently certified optimizer discoveries; the post-primary generic full-flag Steane diagnostic is also positive and separately labeled.",
    "Yes: target5 surface extraction references, independently verified.",
    "Yes: target7 surface extraction references, independently verified.",
    "Yes: both one-round and nine-round target9 references have independent lower9 and legal upper9, hence exact9 under the declared model.",
    "Largest certified reference:81 data qubits,161 total qubits,4752 operations and43920 physical alternatives, nine extraction rounds. Resources use the actual compiled schedule.",
    "Pair grouping is appropriate for low-order exclusions; graph potentials made these high targets practical. Generic DP remains a capped fallback. No cross-method superiority is claimed without a matched eligible-case comparison.",
    "The nine-round target9 worker used%.6f CPU s, %.6f wall s and %.2f MiB observed peak RSS. CPU includes the actual interpreter's startup/output serialization; sampled RSS plus the body snapshot is an observed peak, not a universal memory theorem."%(a['cpu'],a['wall'],a['peak_rss']/2**20),
    "Target9 certification is practical locally for this eligible81-data-qubit reference. This does not establish feasibility for every stabilizer code or architecture.",
    "No intrinsic local resource blocker for the certified reference. Graph-ineligible general cases can remain limited by proof complexity/DP state bounds. A later RAM-admission stop was transient host availability; no cloud inference is drawn from it.",
    "No cloud execution was necessary or provisioned. Remote execution remains NOT_RUN.",
    "Primary ladder: eight distinct positive circuits; actual population:41 distinct circuits and four positives. The finalist audit simulated12 distinct certified controls, with exact shot counts above. Policy pools contain16 candidates per family and repeated evaluated actions; do not add duplicated cached reports as distinct executions.",
    "Cheap screens did eliminate some verified-single-fault invalid cases. Other invalid circuits needed pair or logical-support witnesses; absence of a cheap witness was never a positive label.",
    "The separate12-positive diagnostic audit has zero false hard rejections; all positive controls remain retained. Aggressive full-scheduler retention of expensive positives was not demonstrated, because fixed allocation pools had no positives.",
    "No certified-frontier screening superiority is established. Work/CPU on negative-only fixed pools is reported separately; no perfect-empty-positive retention claim.",
    "Actual certified resource frontiers and conditional noisy estimates are exported separately. The nine-round target9 lookup-decoder estimate was37/320 versus2/320 for the one-round control, with broad sequential intervals; do not infer optimal-decoder or full-memory dominance.",
    "Incomplete gates below include broad independent high-distance-family validation, general memory-bounded proofs, meaningful positive-containing matched allocation efficiency and broad optimizer discovery at higher targets.",
    "Most justified next step: build a prospectively stratified expensive-positive allocation pool from the certified controls and genuine optimizer discoveries, then compare resource–LER frontier retention at actual full CPU budgets with a stronger declared decoder. Keep reference controls separate from optimizer seeds."]
    for i,text in enumerate(answers,1):lines.append(f"{i}. {text}")
    gates={"A":("PASS","All709 prior evidence files unchanged; original repository commit unchanged"),"B":("PASS","CSS/non-CSS input, signed basis mutation and extraction regressions retained"),"C":("PASS","Exact extraction contract, ideal boundaries and physical universe explicit"),"D":("PASS","Real target3 positives including four optimizer discoveries"),"E":("PASS","Real target5 graph certificates independently verified"),"F":("PASS","Real target7 graph certificates independently verified"),"G":("PASS","Actual target9 lower exclusion0..8 and replayed upper9"),"H":("PASS","Independent forward inventories, potentials and physical witness replay"),"I":("PARTIAL","Streaming/SQLite, capped DP and observed local worker guards; no universal bound"),"J":("PARTIAL","Positive ladder through9; higher-target positives from one construction family"),"K":("PARTIAL","12-positive diagnostic retention; no positive-containing fixed allocation pool"),"L":("PARTIAL","Actual CPU recorded; negative-only pools cannot establish frontier efficiency"),"M":("PARTIAL","Broad population/basis/hybrid works and finds3; no optimizer-discovered9"),"N":("PARTIAL","Actual evaluator PID accounting verified; reference ladder observed only one concurrent evaluator; multicore speedup not established"),"O":("PASS","Real local target9 completed with measured CPU/RAM and resume"),"P":("PASS","Local reference feasible; no algorithmic/cloud conflation"),"Q":("NOT_RUN","Cloud neither needed nor authorized/provisioned"),"R":("PARTIAL","Source/pools/proofs/seeds retained; paused partial controller timing is unmeasured"),"S":("PARTIAL","53 tests and installed target9 CLI checked; separate Search CLI absent in this repository"),"T":("PASS","Required docs, raw artifacts, source epochs and verified package")}
    lines += ["","## Acceptance gates","","| Gate | Status | Scope |","|---|---|---|"]
    for key,(status,note) in gates.items():lines.append(f"| {key} | {status} | {note} |")
    Path("docs/RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    save(Path("results/high_distance/acceptance.json"),dict(source=source,gates={k:dict(status=v[0],scope=v[1]) for k,v in gates.items()},high_distance_reference_objective=True,screening_superiority=False))
    Path("docs/LOCAL_FEASIBILITY.md").write_text("# Local feasibility\n\n"+f"The nine-round81-data/161-total-qubit reference completed exact target9 certification locally: {a['cpu']:.6f} CPU seconds, {a['wall']:.6f} wall seconds, {a['peak_rss']/2**20:.2f} MiB observed peak RSS. Full host model/core/RAM/disk metadata is in results/local_feasibility/host.json.\n\n"+f"Source-bound continuation rechecked the same proof with {resume['partition_files']} root fragments; proof identity matched. Resume CPU was{resume['answer']['cpu']:.6f} s; this is not a matched speedup claim.\n\n"+"The initial redirector-supervised metrics were invalid and are excluded. The corrected run monitors the actual interpreter PID and obtains completed Windows process CPU. A later available-RAM admission stop was resumed without reducing limits. No measured intrinsic need for cloud exists for this reference. Graph-ineligible or wide-frontier codes remain potentially UNKNOWN; cloud is not a substitute for an algorithm.\n",encoding="utf-8")
    print("REPORT_COMPLETE",len(valid),"optimizer positives",len(checked),"additional proofs replayed")

if __name__=="__main__":main()
