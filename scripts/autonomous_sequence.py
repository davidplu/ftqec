"""Sequential study controller; workers inside each study remain parallel."""
import subprocess,sys,json,time,psutil
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
root=Path("results/autonomous");source=source_identity()
steps=[("autonomous_campaign.py","campaign_console.txt","campaign/complete.json"),
       ("autonomous_comparisons.py","comparison_console.txt","../../benchmarks/policy_comparison/autonomous_generation/complete.json"),
       ("autonomous_scaling.py","scaling_console.txt","../../benchmarks/population_scaling/autonomous/complete.json"),
       ("autonomous_retention.py","retention_console.txt","../../benchmarks/positive_retention/autonomous/complete.json"),
       ("autonomous_decoders.py","decoder_console.txt","../ler/autonomous_decoder/complete.json"),
       ("autonomous_references.py","reference_console.txt","../certificates/reference_validation/summary.json")]
for script,console,complete in steps:
 if (root/complete).exists():continue
 assert source_identity()==source
 # Admission waits are operational, not negative scientific outcomes.
 while psutil.virtual_memory().available<1152*1024**2:
  save(root/"sequence_status.json",dict(source=source,stage=script,status="WAITING_FOR_HOST_MEMORY",available=psutil.virtual_memory().available))
  time.sleep(10)
 save(root/"sequence_status.json",dict(source=source,stage=script,status="RUNNING"))
 with (root/console).open("a",encoding="utf-8") as out:result=subprocess.run([sys.executable,str(Path("scripts")/script)],stdout=out,stderr=subprocess.STDOUT)
 if result.returncode or not (root/complete).exists():
  save(root/"sequence_status.json",dict(source=source,stage=script,status="NEEDS_RECOVERY",returncode=result.returncode));raise SystemExit(2)
 print("COMPLETED",script,flush=True)
save(root/"sequence_status.json",dict(source=source,status="COMPLETE"))
