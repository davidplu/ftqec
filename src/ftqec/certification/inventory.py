"""Disk-backed exact operation-local inventory, two distinct propagation engines."""
import hashlib,json,sqlite3,tempfile
from itertools import product,islice
from pathlib import Path
from ..codes.pauli import Pauli
from ..codes.logicals import logical_basis,logical_effect
from ..faults.signatures import Fault,enumerate_faults

class Inventory:
    def __init__(self):
        self.temp=tempfile.TemporaryDirectory(prefix="ftqec-proof-");self.connection=sqlite3.connect(str(Path(self.temp.name)/"inventory.sqlite"))
        self.connection.execute("PRAGMA cache_size=-2048");self.connection.execute("PRAGMA temp_store=FILE")
        self.connection.execute("CREATE TABLE entries(op INTEGER,label TEXT,d TEXT,l TEXT,data TEXT,PRIMARY KEY(op,label))")
    def add(self,f,d,l,data):self.connection.execute("INSERT INTO entries VALUES(?,?,?,?,?)",(f.operation,f.label,hex(d),hex(l),hex(data)))
    def finish(self):
        self.connection.commit();h=hashlib.sha256()
        for row in self.connection.execute("SELECT * FROM entries ORDER BY op,label"):h.update((json.dumps(row,separators=(",",":"))+"\n").encode())
        self.hash=h.hexdigest();self.count=self.connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    def rows(self):
        for op,label,d,l,data in self.connection.execute("SELECT * FROM entries ORDER BY op,label"):yield op,label,int(d,16),int(l,16),int(data,16)
    def close(self):self.connection.close();self.temp.cleanup()

def fault_at(c,i,label):
    op=c.operations[i];kind="measurement" if op.gate=="M" else "preparation" if op.role=="input_preparation_noise" else "idle_gate" if op.gate=="IDLE" else op.gate.lower()
    return Fault(i,op.qubits,label,kind,f"op:{i}",round_index=op.round_index,check=op.check,role=op.role,interval=op.interval,interaction_position=op.interaction_position)

def backward(c):
    inv=Inventory();nd=len(c.detectors)+len(c.code.generators);nl=2*c.code.k+len(c.observables);pairs=logical_basis(c.code);record_maps={}
    for i,det in enumerate(c.detectors):
        for rec in det:record_maps[rec]=record_maps.get(rec,0)^(1<<i)
    for i,obs in enumerate(c.observables):
        for rec in obs:record_maps[rec]=record_maps.get(rec,0)^(1<<(nd+2*c.code.k+i))
    xm=[];zm=[]
    for q in range(c.num_qubits):
        for z,out in ((False,xm),(True,zm)):
            p=Pauli(c.code.n,0 if z or q>=c.code.n else 1<<q,(1<<q) if z and q<c.code.n else 0)
            out.append((c.code.syndrome(p)<<len(c.detectors))|(logical_effect(p,pairs)<<nd)|(p.packed<<(nd+nl)))
    for i in range(len(c.operations)-1,-1,-1):
        op=c.operations[i];g=op.gate;a=op.qubits[0] if op.qubits else 0
        if g!="BARRIER":
            labels=["I"] if g=="M" else ("".join(p) for p in product("IXYZ",repeat=len(op.qubits)) if any(x!="I" for x in p))
            for label in labels:
                value=record_maps.get(op.record,0) if g=="M" else 0
                if g!="M":
                    for q,p in zip(op.qubits,label):
                        if p in "XY":value^=xm[q]
                        if p in "YZ":value^=zm[q]
                inv.add(fault_at(c,i,label),value&((1<<nd)-1),(value>>nd)&((1<<nl)-1),value>>(nd+nl))
        if g in ("RESET","PREP"):xm[a]=zm[a]=0
        elif g=="M":xm[a]^=record_maps.get(op.record,0)
        elif g=="H":xm[a],zm[a]=zm[a],xm[a]
        elif g in ("S","SDG"):xm[a]^=zm[a]
        elif g=="CX":b=op.qubits[1];xm[a]^=xm[b];zm[b]^=zm[a]
        elif g=="CZ":b=op.qubits[1];xm[a]^=zm[b];xm[b]^=zm[a]
        elif g=="SWAP":b=op.qubits[1];xm[a],xm[b]=xm[b],xm[a];zm[a],zm[b]=zm[b],zm[a]
    inv.finish();return inv

def forward(c,batch_size=128):
    inv=Inventory();faults=iter(enumerate_faults(c));pairs=logical_basis(c.code)
    while batch:=list(islice(faults,batch_size)):
        x=[0]*c.num_qubits;z=[0]*c.num_qubits;records={};events={}
        for lane,f in enumerate(batch):events.setdefault(f.operation,[]).append((lane,f))
        for i,op in enumerate(c.operations):
            g=op.gate;a=op.qubits[0] if op.qubits else 0
            if g in ("PREP","RESET"):x[a]=z[a]=0
            elif g=="M":
                bit=x[a]
                for lane,f in events.get(i,()):bit^=1<<lane
                if op.record:records[op.record]=bit
            elif g=="H":x[a],z[a]=z[a],x[a]
            elif g in ("S","SDG"):z[a]^=x[a]
            elif g=="CX":b=op.qubits[1];x[b]^=x[a];z[a]^=z[b]
            elif g=="CZ":b=op.qubits[1];z[a]^=x[b];z[b]^=x[a]
            elif g=="SWAP":b=op.qubits[1];x[a],x[b]=x[b],x[a];z[a],z[b]=z[b],z[a]
            if g!="M":
                for lane,f in events.get(i,()):
                    for q,p in zip(f.qubits,f.label):
                        if p in "XY":x[q]^=1<<lane
                        if p in "YZ":z[q]^=1<<lane
        ds=[0]*len(batch);ls=[0]*len(batch);data=[0]*len(batch)
        def transpose(bits,out,index):
            while bits:
                bit=bits&-bits;out[bit.bit_length()-1]|=1<<index;bits^=bit
        for j,det in enumerate(c.detectors):
            bits=0
            for rec in det:bits^=records[rec]
            transpose(bits,ds,j)
        for j,p in enumerate(c.code.generators):
            bits=0
            for q in range(c.code.n):
                if p.z>>q&1:bits^=x[q]
                if p.x>>q&1:bits^=z[q]
            transpose(bits,ds,len(c.detectors)+j)
        for j,pair in enumerate(pairs):
            for offset,p in enumerate((pair[1],pair[0])):
                bits=0
                for q in range(c.code.n):
                    if p.z>>q&1:bits^=x[q]
                    if p.x>>q&1:bits^=z[q]
                transpose(bits,ls,2*j+offset)
        for j,obs in enumerate(c.observables):
            bits=0
            for rec in obs:bits^=records[rec]
            transpose(bits,ls,2*c.code.k+j)
        for q in range(c.code.n):transpose(x[q],data,q);transpose(z[q],data,c.code.n+q)
        for lane,f in enumerate(batch):inv.add(f,ds[lane],ls[lane],data[lane])
    inv.finish();return inv
