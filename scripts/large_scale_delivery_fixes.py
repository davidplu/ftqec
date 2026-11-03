"""Apply delivery fixes after the frozen study and all its checks close."""
import argparse,json,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,source_records,digest
parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--stage',type=Path);args=parser.parse_args();before=source_identity();expected='3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab';assert before==expected,'Requires the exact frozen study source'
changes={
 'src/ftqec/optimization/disk_engine.py':("if row['id'] not in chosen:row['retention']='DEFERRED_NOT_INVALID';db.put(row)","if row['id'] not in chosen:row['retention']='NOT_PROMOTED';db.put(row)"),
 'src/ftqec/execution/tasks.py':('                answers.append(answer)\n                if on_result is not None:on_result(task,answer)', '                answer["admission"]=dict(requested_workers=workers,admitted_workers=admitted,available_memory_bytes=available,worker_memory_mb=memory_mb,safety_reserve_bytes=512*1024**2)\n                answers.append(answer)\n                if on_result is not None:on_result(task,answer)')}
prepared={}
for filename,(old,new) in changes.items():
 path=Path(filename);text=path.read_text();assert text.count(old)==1,filename;prepared[filename]=text.replace(old,new)
 if filename.endswith('disk_engine.py'):
  guard="if config.candidate_goal is not None and db.meaningful_count()>=config.candidate_goal:"
  assert prepared[filename].count(guard)==1
  prepared[filename]=prepared[filename].replace(guard,"if config.candidate_goal is not None and not state.get('pending') and db.meaningful_count()>=config.candidate_goal:")
print('PREPARED',list(prepared),flush=True)
if args.stage:
 stage=args.stage.resolve();assert stage.is_relative_to((Path.cwd()/'.private').resolve())
 stage.mkdir(parents=True,exist_ok=False)
 for path in Path('src').rglob('*.py'):
  target=stage/path.relative_to('src');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
 for filename,text in prepared.items():(stage/Path(filename).relative_to('src')).write_bytes(text.encode('utf-8'))
 staged=digest(source_records(stage/'ftqec'));save(stage.parent/'source_stage.json',dict(study_source=before,staged_source=staged,path=str(stage),files=list(prepared),scope='Isolated engineering validation; active scientific study source is unchanged.'))
 print('STAGED_SOURCE',staged,flush=True);raise SystemExit(0)
if not args.apply:raise SystemExit(0)
assert digest(source_records('src/ftqec'))==before
planned=source_records('src/ftqec')
for filename,text in prepared.items():planned[Path(filename).relative_to('src/ftqec').as_posix()]=hashlib.sha256(text.encode('utf-8')).hexdigest()
assert digest(planned)=='ca8dc79975cc2761c2ab91a6ce28e0dfcf5cce85df8a1e1ce75c42a6054b02e0','Delivery changes differ from the tested staging source'
test_source=Path('benchmarks/recovery/test_pending_window.py');test_target=Path('tests/scientific/test_large_scale_recovery.py');assert test_source.exists() and not test_target.exists()
marker=Path('results/large_scale/release')/before/'READY_FOR_DELIVERY_FIXES.json';assert marker.exists(),'Do not change source while frozen experiments or validation are still active';assert json.loads(marker.read_text())['study_source']==before
state=json.loads((Path('results/large_scale/validation_pipeline')/before/'state.json').read_text());assert state['status']=='STAGES_COMPLETE_REPORT_AND_RELEASE_AUDIT_STILL_REQUIRED'
supplement=json.loads((Path('results/large_scale/supplemental_validation')/before/'state.json').read_text());assert supplement['status']=='COMPLETE_FINAL_REPORT_REQUIRED'
policy_audit=json.loads((Path('results/large_scale/policy_evidence_audit')/before/'state.json').read_text());assert policy_audit['status']=='COMPLETE_REPORT_INTERPRETATION_REQUIRED'
root=Path('results/large_scale/delivery_fixes')/before
for filename,text in prepared.items():
 path=Path(filename);backup=root/'before'/filename;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(path.read_bytes());path.write_bytes(text.encode('utf-8'))
test_target.write_bytes(test_source.read_bytes())
after=source_identity();save(root/'changes.json',dict(study_source=before,delivery_source=after,files=list(prepared),scope='Allocation annotation renamed to neutral NOT_PROMOTED; actual batch admission decisions attached to returned task receipts. Resume completes a pending final window before recognizing the finite candidate goal. No compiler, fault-model, decoder, scheduling, or proof kernel changes. Frozen experiment records are not rewritten. New delivery source requires its own full tests, package check, and fresh adopted-certificate receipts.'))
print('DELIVERY_SOURCE',after,flush=True)