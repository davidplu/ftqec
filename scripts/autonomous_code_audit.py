"""Independent exhaustive algebraic-distance audit for the small final-family inputs."""
from itertools import combinations,product
import json,hashlib,time
from pathlib import Path
from ftqec.results.artifacts import save,source_identity
protocol=json.loads(Path("benchmarks/policy_comparison/autonomous_generation/protocol.json").read_text())
for name,(data,target) in protocol["cases"].items():
 start=time.perf_counter();cpu=time.process_time();strings=data["generators"];n=len(strings[0])
 def pack(text):
  return sum((1<<q) for q,p in enumerate(text) if p in "XY") | (sum((1<<q) for q,p in enumerate(text) if p in "YZ")<<n)
 generators=[pack(s.lstrip("+-")) for s in strings];span={0}
 for g in generators:span|={s^g for s in list(span)}
 def commute(a,b):return (((a&((1<<n)-1))&(b>>n)).bit_count()+((a>>n)&(b&((1<<n)-1))).bit_count())%2==0
 examined={};witness=None
 for weight in range(1,target+1):
  count=0
  for positions in combinations(range(n),weight):
   for axes in product("XYZ",repeat=weight):
    text=["I"]*n
    for q,a in zip(positions,axes):text[q]=a
    packed=pack(text);count+=1
    if all(commute(packed,g) for g in generators) and packed not in span:
     witness="".join(text);break
   if witness:break
  examined[weight]=count
  if witness:break
 assert witness is not None and sum(p!="I" for p in witness)==target
 save(Path("results/autonomous/release/algebraic")/(name+".json"),dict(source=source_identity(),code=data,target=target,
      exact_distance=target,upper_witness=witness,excluded_weights=list(range(1,target)),counts=examined,
      stabilizer_group_size=len(span),method="independent exhaustive Pauli supports and explicit stabilizer group",
      cpu=time.process_time()-cpu,wall=time.perf_counter()-start,driver_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
 print("ALGEBRAIC",name,target,examined,flush=True)
