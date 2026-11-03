import hashlib,json,os,tempfile,time
from pathlib import Path

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def source_records(root):
    root=Path(root)
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*.py"))}

def source_identity():
    return digest(source_records(Path(__file__).resolve().parents[1]))

def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(dir=path.parent,suffix=".tmp")
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(value,f,sort_keys=True,allow_nan=False);f.flush();os.fsync(f.fileno())
        for attempt in range(40):
            try:
                os.replace(name,path)
                break
            except PermissionError:
                # Windows readers/antivirus may briefly deny delete-sharing.
                # Retain the complete temporary file and retry atomically.
                if attempt==39:raise
                time.sleep(min(.01*(attempt+1),.1))
    finally:
        if os.path.exists(name):os.unlink(name)
