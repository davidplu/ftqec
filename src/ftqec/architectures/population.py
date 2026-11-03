import random
from dataclasses import dataclass
from ..codes.input import load
from ..circuits.model import Circuit
from ..circuits.gadgets import append_gadget
from ..results.artifacts import digest

FAMILIES=("bare","flagged","cat","verified_cat")

@dataclass(frozen=True)
class Genome:
    family: str
    orders: tuple
    checks: tuple
    rounds: int=1
    shared: bool=True
    reverse_flags: bool=False
    basis: tuple=()
    flag_style: str="single"
    verification_rounds: int=1
    schedule: str="check_serial"
    ancilla_slots: int|None=None
    interaction_layers: tuple=()
    native_css: bool=False
    compact_ancillas: bool=False
    def to_dict(self):return dict(family=self.family,orders=[list(x) for x in self.orders],checks=list(self.checks),rounds=self.rounds,shared=self.shared,reverse_flags=self.reverse_flags,basis=list(self.basis),flag_style=self.flag_style,verification_rounds=self.verification_rounds,schedule=self.schedule,ancilla_slots=self.ancilla_slots,interaction_layers=[list(x) for x in self.interaction_layers],native_css=self.native_css,compact_ancillas=self.compact_ancillas)
    @classmethod
    def from_dict(cls,d):return cls(d["family"],tuple(tuple(x) for x in d["orders"]),tuple(d["checks"]),d["rounds"],d["shared"],d["reverse_flags"],tuple(d.get("basis",())),d.get("flag_style","single"),d.get("verification_rounds",1),d.get("schedule","check_serial"),d.get("ancilla_slots"),tuple(tuple(x) for x in d.get("interaction_layers",())),d.get("native_css",False),d.get("compact_ancillas",False))

def sample(inp,seed,target=3):
    if type(target) is not int or target<1:raise ValueError("Positive target required")
    rng=random.Random(seed);orders=[]
    for p in inp.code.generators:
        support=[q for q in range(inp.code.n) if (p.x|p.z)>>q&1];rng.shuffle(support);orders.append(tuple(support))
    checks=list(range(len(orders)));rng.shuffle(checks)
    return Genome(rng.choice(FAMILIES),tuple(orders),tuple(checks),rng.choice(tuple(sorted({1,2,target}))),rng.choice((True,False)),rng.choice((True,False)),(),rng.choice(("single","adjacent","nested","overlap")),rng.choice((1,max(1,(target-1)//2))),rng.choice(("check_serial","axis_grouped")))

def mutate(inp,parent,seed,witness=None,target=3,compact_ancillas=True):
    rng=random.Random(seed);d=parent.to_dict();which=rng.randrange(10)
    if witness:
        from .repair import propose
        return Genome.from_dict(propose(inp,parent.to_dict(),witness,seed,target,compact_ancillas))
    elif which==0:d["family"]=rng.choice(FAMILIES)
    if which==1:rng.shuffle(d["orders"][rng.randrange(len(d["orders"]))])
    if which==2:rng.shuffle(d["checks"])
    if which==3:d["shared"]=not d["shared"]
    if which==4:d["rounds"]=rng.choice(tuple(sorted({1,2,target,parent.rounds+1})))
    if which==5 and len(inp.code.generators)>1:
        import stim
        strings=list(parent.basis) if parent.basis else [("-" if sign else "+")+str(p) for p,sign in zip(inp.code.generators,inp.signs)]
        a,b=rng.sample(range(len(strings)),2);strings[a]=str(stim.PauliString(strings[a])*stim.PauliString(strings[b])).replace("_","I");d["basis"]=strings
        changed=load(dict(n=inp.code.n,generators=strings));orders=[]
        for p in changed.code.generators:
            support=[q for q in range(p.n) if (p.x|p.z)>>q&1];rng.shuffle(support);orders.append(support)
        d["orders"]=orders
    if which==6:d["flag_style"]=rng.choice(("single","adjacent","nested","overlap"))
    if which==7:d["verification_rounds"]=rng.choice((1,max(1,(target-1)//2),parent.verification_rounds+1))
    if which==8:d["schedule"]=rng.choice(("check_serial","axis_grouped","list","critical_path","conflict_color","resource"))
    if which==9:d["ancilla_slots"]=rng.randint(1,len(inp.code.generators))
    if d["schedule"] in ("colored","joint_colored"):d["schedule"]="critical_path";d["interaction_layers"]=[];d["compact_ancillas"]=compact_ancillas
    return Genome.from_dict(d)

def recombine(a,b):return Genome(a.family,b.orders,a.checks,b.rounds,a.shared,b.reverse_flags,b.basis,a.flag_style,b.verification_rounds,"critical_path" if a.schedule in ("colored","joint_colored") else a.schedule,a.ancilla_slots,native_css=a.native_css,compact_ancillas=a.compact_ancillas)

def compile(inp,g):
    original=inp
    if g.basis:
        import stim
        changed=load(dict(n=inp.code.n,name=inp.code.name,generators=list(g.basis)))
        if changed.code.rank!=inp.code.rank or any(not inp.code.is_stabilizer(p) for p in changed.code.generators):raise ValueError("Changed stabilizer group")
        from ..codes.logicals import logical_basis
        stabilizers=[stim.PauliString(("-" if sign else "+")+str(p)) for p,sign in zip(inp.code.generators,inp.signs)]+[stim.PauliString(str(z)) for x,z in logical_basis(inp.code)]
        sim=stim.TableauSimulator();sim.do(stim.Tableau.from_stabilizers(stabilizers).to_circuit())
        if any(sim.peek_observable_expectation(stim.PauliString(str(p)))!=(-1 if sign else 1) for p,sign in zip(changed.code.generators,changed.signs)):raise ValueError("Changed stabilizer phases")
        inp=changed
    code=inp.code;m=len(code.generators)
    if g.family not in FAMILIES or sorted(g.checks)!=list(range(m)) or len(g.orders)!=m or type(g.rounds) is not int or g.rounds<1 or type(g.verification_rounds) is not int or g.verification_rounds<1 or g.flag_style not in ("single","adjacent","nested","overlap") or g.schedule not in ("check_serial","axis_grouped","list","critical_path","conflict_color","resource","colored","joint_colored"):raise ValueError("Invalid genome")
    if type(g.native_css) is not bool:raise ValueError("Native CSS option must be boolean")
    for p,order in zip(code.generators,g.orders):
        if sorted(order)!=[q for q in range(code.n) if (p.x|p.z)>>q&1]:raise ValueError("Interaction support")
    cat=g.family in ("cat","verified_cat");width=max(p.weight for p in code.generators)
    slots=(1 if g.shared else m) if g.ancilla_slots is None else g.ancilla_slots
    if type(slots) is not int or not 1<=slots<=m:raise ValueError("Invalid ancilla allocation")
    per=width if cat else 1
    syn=tuple(range(code.n,code.n+slots*per));flag_count=slots if g.family in ("flagged","verified_cat") else 0
    flag_width=max(1,width-1) if g.family=="flagged" and g.flag_style!="single" else 1
    flag_count*=flag_width
    flags=tuple(range(code.n+len(syn),code.n+len(syn)+flag_count));c=Circuit(code,syn,flags)
    c.experiment=dict(scope="syndrome_extraction_with_ideal_code_space_boundaries",rounds=g.rounds,generator_signs=list(inp.signs),family=g.family,flag_style=g.flag_style,verification_rounds=g.verification_rounds,schedule_variant=g.schedule)
    if g.basis:c.experiment.update(reference_code=original.code.to_dict(),reference_signs=list(original.signs),basis_provenance=list(g.basis))
    for rd in range(g.rounds):
        checks=sorted(g.checks,key=lambda i:(set(str(code.generators[i]))-{"I"}!={"X"})) if g.schedule!="check_serial" else g.checks
        for check in checks:
            slot=check%slots;order=g.orders[check];start=len(c.operations)
            if not cat:
                intervals=(((len(order)//2 if g.reverse_flags else 0),len(order)),) if g.family=="flagged" else ()
                if g.family=="flagged" and g.flag_style=="adjacent":intervals=tuple((i,i+2) for i in range(max(0,len(order)-1)))
                if g.family=="flagged" and g.flag_style=="overlap":intervals=tuple((i,min(i+3,len(order))) for i in range(max(0,len(order)-1)))
                if g.family=="flagged" and g.flag_style=="nested":intervals=tuple((i,len(order)) for i in range(max(0,len(order)-1)))
                append_gadget(c,check,order,intervals,syn[slot],flags[slot*flag_width:(slot+1)*flag_width],native_z=g.native_css and g.family=="bare" and set(str(code.generators[check]))-{"I"}=={"Z"})
            else:
                anc=syn[slot*per:slot*per+len(order)]
                for q in anc:c.add("RESET",[q],check=check)
                c.add("H",[anc[0]],check=check)
                for q in anc[1:]:c.add("CX",[anc[0],q],check=check)
                if g.family=="verified_cat":
                    f=flags[slot]
                    for vr in range(g.verification_rounds):
                        for j in range(1,len(anc)):
                            c.add("RESET",[f],check=check)
                            c.add("CX",[anc[0],f],check=check);c.add("CX",[anc[j],f],check=check)
                            rec=f"f{check}_verify{vr}_{j}";c.add("M",[f],record=rec,check=check);c.detectors.append([rec])
                for a,q in zip(anc,order):
                    p=str(code.generators[check])[q]
                    if p=="Y":c.add("SDG",[q],check=check)
                    c.add("CZ" if p=="Z" else "CX",[a,q],check=check)
                    if p=="Y":c.add("S",[q],check=check)
                records=[]
                for j,a in enumerate(anc):
                    c.add("H",[a],check=check);rec=f"s{check}_cat{j}";c.add("M",[a],record=rec,check=check);records.append(rec)
                c.detectors.append(records)
            # Unique records per round, preserving every referenced parity.
            names={op.record:f"r{rd}_{op.record}" for op in c.operations[start:] if op.record}
            from dataclasses import replace
            for i in range(start,len(c.operations)):
                op=c.operations[i];c.operations[i]=replace(op,record=names.get(op.record),round_index=rd)
            for detector in c.detectors:
                for j,name in enumerate(detector):
                    if name in names:detector[j]=names[name]
    c.validate()
    if g.compact_ancillas:
        from .allocation import compact
        c=compact(c)
    if g.schedule in ("colored","joint_colored"):
        if g.family!="bare" or slots!=m or any(set(str(p)) - {"I"} not in ({"X"},{"Z"}) for p in code.generators):raise ValueError("Colored schedule requires bare CSS dedicated ancillas")
        from .coloring import compile_layers
        return compile_layers(c,g.orders,g.interaction_layers,joint=g.schedule=="joint_colored")
    if g.schedule not in ("check_serial","axis_grouped"):
        from ..scheduling.dependencies import reorder
        c=reorder(c,g.schedule)
    return c
