"""Graph-relaxation lower bounds and location-exclusive frontier dynamic programming."""
from collections import deque
from ..results.artifacts import digest


def projections(c):
    nd=len(c.detectors)+len(c.code.generators);syndrome={};other=[];records={o.record:o for o in c.operations if o.record}
    for i,row in enumerate(c.detectors):
        relevant=[records[r] for r in row if "_s" in r or records[r].role=="syndrome_readout"]
        if relevant and relevant[0].check is not None:syndrome[(relevant[0].check,relevant[0].round_index)]=i
        else:other.append(1<<i)
    masks={}
    for bit in range(2*c.code.k+len(c.observables)):
        choices=[]
        if bit<2*c.code.k:
            from ..codes.logicals import logical_basis
            p=logical_basis(c.code)[bit//2][1 if bit%2==0 else 0];axes=set(str(p))-{ "I" }
            selected=[i for i,g in enumerate(c.code.generators) if set(str(g))-{ "I" }==axes] if len(axes)==1 else list(range(len(c.code.generators)))
            choices.append([1<<(len(c.detectors)+i) for i in selected])
            temporal=[]
            for check in selected:
                rows=sorted((rd,j) for (ch,rd),j in syndrome.items() if ch==check and rd is not None)
                previous=None
                for rd,j in rows:temporal.append((1<<j)^(0 if previous is None else 1<<previous));previous=j
                temporal.append((1<<(len(c.detectors)+check))^(0 if previous is None else 1<<previous))
            if temporal:choices.extend([temporal,temporal+other])
        choices.append([1<<j for j in range(nd)]);masks[bit]=choices
    return masks

def graph(inv,masks,bit):
    boundary=len(masks);edges={}
    for op,label,d,l,data in inv.rows():
        support=[i for i,mask in enumerate(masks) if (d&mask).bit_count()%2]
        if len(support)>2:return None
        if not support:
            if not (l>>bit&1):continue
            support=[boundary,boundary]
        elif len(support)==1:support.append(boundary)
        u,v=sorted(support);flip=l>>bit&1;edges.setdefault((u,v,flip),(u,v,flip,op,label))
    return dict(vertices=boundary+1,edges=list(edges.values()))

def produce(g,target,entry_limit=3000000,checkpoint=None,work_limit=200000):
    n=g["vertices"]
    if 2*n*n>entry_limit:return dict(complete=False,reason="potential_entry_limit",entries=2*n*n)
    adj=[[] for _ in range(2*n)]
    for i,(u,v,flip,op,label) in enumerate(g["edges"]):
        for parity in (0,1):a=2*u+parity;b=2*v+(parity^flip);adj[a].append((b,i));adj[b].append((a,i))
    rows=[];bound=target;witness=None;work=0
    from pathlib import Path
    from ..results.artifacts import save
    import json
    directory=Path(checkpoint) if checkpoint else None
    if directory:directory.mkdir(parents=True,exist_ok=True)
    context=digest(dict(graph=g,target=target))
    for root in range(n):
        cached=directory/(str(root)+".json") if directory else None
        if cached and cached.exists():
            packet=json.loads(cached.read_text());dist=packet["values"]
            if packet.get("context")!=context or packet.get("root")!=root or len(dist)!=2*n or dist[2*root]!=0 or any(type(x) is not int or not 0<=x<=target for x in dist):return dict(complete=False,reason="checkpoint identity")
            if any(abs(dist[a]-dist[b])>1 for a,edges in enumerate(adj) for b,e in edges):return dict(complete=False,reason="checkpoint edge inequality")
            bound=min(bound,dist[2*root+1]);rows.append(dist);continue
        dist=[target]*(2*n);start=2*root;dist[start]=0;queue=deque([start]);parents={}
        while queue:
            a=queue.popleft()
            if dist[a]>=target:continue
            for b,e in adj[a]:
                work+=1
                if work>work_limit:return dict(complete=False,reason="graph_work_limit",completed_roots=len(rows),work=work)
                if dist[b]>dist[a]+1:dist[b]=dist[a]+1;parents[b]=(a,e);queue.append(b)
        if dist[start+1]<bound:
            bound=dist[start+1];path=[];node=start+1
            while node!=start:node,e=parents[node];path.append(e)
            witness=[g["edges"][e][3:] for e in path]
        rows.append(dist)
        if cached:save(cached,dict(context=context,root=root,values=dist))
    return dict(complete=True,lower_bound=bound,potentials=[[min(x,bound) for x in row] for row in rows],relaxed_witness=witness)

def check(g,proof,bound):
    n=g["vertices"];rows=proof.get("potentials",[])
    if len(rows)!=n:return False
    for root,values in enumerate(rows):
        if len(values)!=2*n or any(type(x) is not int or not 0<=x<=bound for x in values):return False
        if values[2*root]!=0 or values[2*root+1]!=bound:return False
        for u,v,flip,op,label in g["edges"]:
            for p in (0,1):
                if abs(values[2*u+p]-values[2*v+(p^flip)])>1:return False
    return True

def dp(inv,target,work_limit=200000,state_limit=100000):
    if inv.count>50000:return dict(complete=False,reason="dp_inventory_entry_cap",work=0,layers=[])
    width=inv.connection.execute("SELECT MAX(length(d)+length(l)) FROM entries").fetchone()[0] or 1
    state_limit=min(state_limit,max(1,64*1024**2//(512+2*width)))
    groups={};last={}
    for op,label,d,l,data in inv.rows():
        groups.setdefault(op,[]).append((label,d,l))
        bits=d
        while bits:bit=bits&-bits;last[bit]=op;bits^=bit
    closing={}
    for bit,op in last.items():closing[op]=closing.get(op,0)|bit
    states={(0,0):(0,())};work=0;hashes=[]
    for op,options in groups.items():
        following={};close=closing.get(op,0)
        for (d,l),(weight,ids) in states.items():
            for label,dd,ll in [(None,0,0)]+options:
                work+=1
                if work>work_limit:return dict(complete=False,reason="dp_work_limit",work=work,layers=hashes)
                w=weight+(label is not None);nd=d^dd;nl=l^ll
                if w>=target or nd&close:continue
                key=(nd,nl)
                if key not in following or w<following[key][0]:following[key]=(w,ids+(((op,label),) if label is not None else ()))
                if len(following)>state_limit:return dict(complete=False,reason="dp_state_limit",work=work,layers=hashes)
        states=following;hashes.append(digest(sorted((hex(d),l,w) for (d,l),(w,ids) in states.items())))
    harmful=[v for (d,l),v in states.items() if not d and l]
    return dict(complete=True,work=work,layers=hashes,witness=min(harmful)[1] if harmful else None,lower_bound=target if not harmful else min(harmful)[0])
