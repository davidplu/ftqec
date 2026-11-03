"""Independent delivery of the first closed large campaign; not final cross-family results."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
s=source_identity();paths=list((Path('results/large_scale/audit')/s/'subsets').glob('*/summary.json'))
choices=[p for p in paths if json.loads(p.read_text())['runs'][0]['job']['name']=='surface3_hybrid_p1000_n10000_s2001'];assert len(choices)==1
path=choices[0];audit=json.loads(path.read_text());root=Path('results/exports/large_scale')/s/'first_closed_campaign';root.mkdir(parents=True,exist_ok=True)
protocol=dict(source=s,audit=str(path),audit_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),representatives=audit['export_representatives'],scope='Provisional delivery from one fully closed, audited large campaign. Does not substitute for matched-compute or cross-family results.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
records=[]
for point in protocol['representatives']:
 bundle=root/point['circuit'];receipt=root/'receipts'/(point['circuit']+'.json')
 if receipt.exists():records.append(json.loads(receipt.read_text()));continue
 if not bundle.exists():export_result(point['run'],point['id'],bundle,'bundle')
 start=time.perf_counter();cpu=time.process_time();check=verify_bundle(bundle,20000000)
 assert check['positive_certificate_verified'] and check['reconstruction_verified'] and check['resource_recomputation_verified']
 row=dict(point,bundle=str(bundle),verification=check,verification_cpu=time.process_time()-cpu,verification_wall=time.perf_counter()-start);save(receipt,row);records.append(row);print('FIRST_LARGE_VERIFIED',point['resources'],flush=True)
save(root/'index.json',dict(source=s,records=records));print('FIRST_LARGE_EXPORTS_VERIFIED',len(records),flush=True)