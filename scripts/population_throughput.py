"""A thousand actual compiled circuits; no certification throughput claim."""
import json,time,subprocess
from pathlib import Path
from ftqec.codes.input import load
from ftqec.circuits.identity import physical_identity
from ftqec.architectures.population import sample,compile
from ftqec.screening.structural import check
from ftqec.results.artifacts import digest,save,source_identity

def main():
    root=Path("benchmarks/population");data=json.loads(Path("examples/steane.json").read_text())
    protocol=dict(source=source_identity(),commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),input=data,seed=982451653,attempts=1000,tier="compile_and_noiseless_flow_only")
    save(root/"protocol.json",protocol);cpu=time.process_time();wall=time.perf_counter();rows=[];seen=set()
    for i in range(1000):
        g=sample(load(data),protocol["seed"]+i);c=compile(load(data),g);receipt=check(c);identity=physical_identity(c)
        rows.append(dict(seed=protocol["seed"]+i,circuit=identity,family=g.family,duplicate=identity in seen,receipt=receipt));seen.add(identity)
    elapsed=time.perf_counter()-wall
    save(root/"result.json",dict(protocol=protocol,rows=rows,compiled=len(rows),unique=len(seen),cpu=time.process_time()-cpu,wall=elapsed,compiled_per_wall_second=len(rows)/elapsed,scope="Compilation and structural checks only. No claim that 1000 candidates received simulation or certification."))

if __name__=="__main__":main()
