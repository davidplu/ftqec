"""Separate prospective finalist simulation/retention audit; no optimizer seeds changed."""
import json,time,sys,os,subprocess,hashlib
from pathlib import Path
import psutil
from ftqec.results.artifacts import save,digest,source_identity
from ftqec.circuits.model import Circuit
from ftqec.certification.exact import certify,verify,screen
from ftqec.simulation.monte_carlo import evaluate
from ftqec.simulation.sequential import combine
from ftqec.execution.tasks import worker_command,completed_process_cpu
ROOT=Path("benchmarks/high_distance/finalist_evaluation")

def worker(inp,out):
    p=json.loads(inp.read_text());start=time.perf_counter();cpu=time.process_time();c=Circuit.from_dict(p["circuit"])
    if p["source"]!=source_identity():raise ValueError("source")
    try:
        if p["kind"]=="screen":result=screen(c,20000000)
        elif p["kind"]=="censor":result=certify(c,9,0,str(out.parent/"partial_proofs"))
        else:result=evaluate(c,.001,p["shots"],p["seed"],max_decoder_faults=100000)
    except Exception as e:result=dict(status="UNKNOWN",reason=type(e).__name__,message=str(e))
    save(out,dict(result=result,pid=os.getpid(),body_cpu=time.process_time()-cpu,body_wall=time.perf_counter()-start,rss=psutil.Process().memory_info().rss))

def run(payload):
    identity=digest(payload);folder=ROOT/"workers"/identity;folder.mkdir(parents=True,exist_ok=True);input=folder/"input.json";output=folder/"answer.json";receipt=folder/"receipt.json"
    if receipt.exists():return json.loads(receipt.read_text())
    if psutil.virtual_memory().available<1024**3:raise MemoryError("Unchanged512MiB worker plus512MiB reserve")
    save(input,payload);cmd=worker_command(input,output)
    if os.name=="nt":cmd[3]=cmd[3].replace("runpy.run_module('ftqec.execution.worker',run_name='__main__')","runpy.run_path("+repr(str(Path(__file__).resolve()))+",run_name='__main__')")
    else:cmd=[sys.executable,str(Path(__file__).resolve()),str(input),str(output)]
    start=time.perf_counter();peak=0;used=0.;reason=None
    with (folder/"stderr.txt").open("w") as log:
        process=subprocess.Popen(cmd,stdout=log,stderr=log);monitor=psutil.Process(process.pid)
        while process.poll() is None:
            try:
                peak=max(peak,monitor.memory_info().rss);t=monitor.cpu_times();used=t.user+t.system
            except psutil.NoSuchProcess:break
            if peak>512*1024**2:reason="MEMORY_LIMIT"
            if used>900 or time.perf_counter()-start>1200:reason="ACTION_LIMIT"
            if reason:process.kill();break
            time.sleep(.02)
        process.wait();used,scope=completed_process_cpu(process,used)
    answer=json.loads(output.read_text()) if output.exists() and not reason else dict(result=dict(status="UNKNOWN",reason=reason or "WORKER_ERROR"),pid=process.pid,rss=peak)
    if answer["pid"]!=process.pid:raise ValueError("PID mismatch")
    answer.update(cpu=used,wall=time.perf_counter()-start,peak_rss=max(peak,answer["rss"]),cpu_scope=scope);save(receipt,dict(payload=payload,answer=answer));return dict(payload=payload,answer=answer)

def main():
    ROOT.mkdir(parents=True,exist_ok=True);source=source_identity();helper=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();ladder=json.loads(Path("benchmarks/high_distance/ladder.json").read_text());cases=[]
    for row in ladder["rows"]:
        cert=row["answer"]["result"]
        if cert.get("status")=="CERTIFIED":cases.append(dict(name=row["name"],target=row["target"],circuit=json.loads((Path(row["output"])/"circuit.json").read_text()),certificate=cert,resources=row["resources"],origin="reference"))
    population=json.loads(Path("results/high_distance/study/population/checkpoint.json").read_text())
    for row in population["rows"]:
        if row.get("certify",{}).get("status")=="CERTIFIED":cases.append(dict(name=row["id"],target=3,circuit=row["circuit"],certificate=row["certify"],resources=row["resources"],origin="optimizer_discovered"))
    protocol=dict(source=source,helper_sha256=helper,selection="all certified primary references and all certified optimizer outputs; no LER-based selection",cases=[c["name"] for c in cases],p=.001,looks=[64,256],alpha=.05,decoder="unchanged one-mechanism lookup",decoder_capacity=100000,qualification="Capacity increases only the existing decoder's resource ceiling; all mechanisms still processed or UNKNOWN, no physical noise or decoder rule change",memory_mb=512,reserve_mb=512)
    if (ROOT/"protocol.json").exists():assert json.loads((ROOT/"protocol.json").read_text())==protocol
    else:save(ROOT/"protocol.json",protocol)
    rows=[]
    for index,case in enumerate(cases):
        c=Circuit.from_dict(case["circuit"]);receipt=verify(c,case["certificate"],20000000);assert receipt["verified"]
        base=dict(source=source,helper=helper,circuit=case["circuit"],decoder_capacity=100000)
        screened=run(dict(base,kind="screen"));batches=[];attempts=[]
        for look,shots in enumerate((64,256)):
            result=run(dict(base,kind="simulation",shots=shots,seed=71000000+index+look*10**10));attempts.append(result)
            if "shots" not in result["answer"]["result"]:break
            batches.append(result["answer"]["result"])
            if combine(batches)["confidence"][1]-combine(batches)["confidence"][0]<=.2:break
        row=dict(name=case["name"],origin=case["origin"],target=case["target"],resources=case["resources"],certificate_receipt=receipt,screen=screened,simulation=combine(batches) if batches else dict(status="UNKNOWN"),attempts=attempts)
        rows.append(row);save(ROOT/"results.json",dict(source=source,rows=rows,qualification="Conditional logical-Z-sector task and declared limited decoder, not optimal-decoder or arbitrary-input LER"));print(case["name"],row["simulation"].get("rate"),row["simulation"].get("shots"),flush=True)
    nine=next(c for c in cases if c["name"]=="surface_d9_r1_t9");censored=run(dict(source=source,helper=helper,circuit=nine["circuit"],kind="censor",decoder_capacity=100000));save(ROOT/"known_positive_budget_censored.json",censored)
    assert censored["answer"]["result"]["status"]=="UNKNOWN" and censored["answer"]["result"]["lower_bound"]<9
    save(ROOT/"retention.json",dict(source=source,positive_controls=len(rows),false_hard_rejections=sum(r["screen"]["answer"]["result"].get("status")=="FAULT_INVALID" for r in rows),unknown_is_not_negative=True,qualification="Diagnostic positive/near-frontier audit, not an untouched final-family performance claim"))
    print("FINALIST_AUDIT_COMPLETE",flush=True)

if __name__=="__main__":
    if len(sys.argv)==3:worker(Path(sys.argv[1]),Path(sys.argv[2]))
    else:main()
