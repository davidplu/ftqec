import sys,json
from pathlib import Path
from .tasks import Task,execute
from ..results.artifacts import save
if __name__=="__main__":save(sys.argv[2],execute(Task(**json.loads(Path(sys.argv[1]).read_text()))))
