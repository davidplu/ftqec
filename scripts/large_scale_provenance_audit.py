"""Independently audit frozen input provenance, task binding, and status annotations."""
import argparse,json,time,collections,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.optimization.store import PopulationStore,unpack
from ftqec.codes.input import load
s=source_identity();base=Path('results/large_scale/campaigns')/s;protocol=json.loads((base/'protocol.json').read_text());parser=argparse.ArgumentParser();parser.add_argument('--job',action='append');args=parser.parse_args();jobs=protocol['jobs']
if args.job:jobs=[j for j in jobs if j['name'] in args.job];assert len(jobs)==len(args.job)
else:assert (base/'complete.json').exists()
root=Path('results/large_scale/provenance')/s/digest(dict(jobs=[j['name'] for j in jobs],driver=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()));root.mkdir(parents=True,exist_ok=True);records=[]
for job in jobs:
 path=Path('results/populations')/s/'study'/job['name'];receipt=json.loads((path/'experiment_receipt.json').read_text());assert receipt['status']=='REQUESTED_CANDIDATE_GOAL_COMPLETED'
 out=root/(job['name']+'.json')
 if out.exists():records.append(json.loads(out.read_text()));continue
 inp=load(protocol['codes'][job['family']]);expected=inp.to_dict();counts=collections.Counter();methods=collections.Counter();mutations=collections.Counter();conflicts=[];start=time.perf_counter();cpu=time.process_time()
 with PopulationStore(path/'population.sqlite',readonly=True) as db:
  for packet in db.packets():
   task=packet['task'];answer=packet['answer'];assert task['source']==s;payload=dict(task);payload['limits']=dict(task['limits']);payload['limits'].pop('proof_directory',None);payload['limits'].pop('cancel_file',None);assert digest(payload)==answer['task'];counts['bound_tasks']+=1;counts['worker_attempts']+=len(answer.get('attempts',[answer]))
   if task['tier'].startswith('construct'):
    assert task['code_identity']==inp.identity and task['circuit']['code_input']==expected
    assert set(task['circuit'])<=set(('code_input','genome','synthesis'))
    counts['code_only_construction_inputs']+=1
  for cid,blob,sha in db.db.execute('SELECT id,payload,hash FROM candidates ORDER BY id'):
   row=unpack(blob,sha);mutations[row.get('construction',{}).get('method','unspecified')]+=1;certificate=row.get('certify',{});methods[certificate.get('proof',{}).get('method','NO_PROOF_METHOD_RECORDED')]+=1
   invalid=row.get('screen',{}).get('status')=='FAULT_INVALID' or certificate.get('status')=='INVALID'
   if invalid and row.get('retention')=='DEFERRED_NOT_INVALID':conflicts.append(cid)
 record=dict(source=s,job=job['name'],counts=dict(counts),proof_method_counts=methods,construction_methods=mutations,allocation_label_conflicts=conflicts,canonical_statuses_preserved=True,wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu,scope='Every construction input equals the frozen code-only input, without supplied reference circuit fields. Task/answer identities independently recomputed. Review of the bound synthesis source establishes the code-derived proposal path; this is not formal whole-program information-flow verification.',annotation_limitation='DEFERRED_NOT_INVALID is an allocation tag in this frozen source, not a physical-validity claim. Canonical screen/certify statuses govern invalidity and must take precedence. Conflicting tags are retained and disclosed rather than rewriting historical candidates.');save(out,record);records.append(record);print('PROVENANCE_AUDITED',job['name'],counts['bound_tasks'],len(conflicts),flush=True)
save(root/'summary.json',dict(source=s,records=records));print(root/'summary.json')