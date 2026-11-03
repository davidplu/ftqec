"""Local sequential validation workload, admitted after the priority run finishes."""
import json,time,subprocess,sys
from pathlib import Path
p=Path("results/discovery/autonomous/surface_target10/checkpoint.json")
while True:
 if p.exists():
  try:state=json.loads(p.read_text())
  except (OSError,json.JSONDecodeError):state={}
  if state.get("status") in ("OPERATIONAL_FRONTIER_PLATEAU","RESOURCE_SAFETY_INTERVENTION","CANCELLED"):break
 time.sleep(10)
if state.get("status")!="OPERATIONAL_FRONTIER_PLATEAU":raise SystemExit("Priority run needs attention")
for script in ("autonomous_retention.py","autonomous_comparisons.py"):
 print("START",script,flush=True)
 subprocess.run([sys.executable,str(Path("scripts")/script)],check=True)
print("VALIDATION_COMPLETE",flush=True)
