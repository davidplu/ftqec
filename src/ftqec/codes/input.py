from dataclasses import dataclass
from .stabilizer import StabilizerCode
from .pauli import Pauli
from .logicals import logical_basis
from ..results.artifacts import digest

@dataclass(frozen=True)
class CodeInput:
    code: StabilizerCode
    signs: tuple
    metadata: dict
    @property
    def identity(self):return digest(self.to_dict())
    def to_dict(self):return dict(self.code.to_dict(),signs=list(self.signs),metadata=self.metadata)

def load(data):
    raw=data.get("generators",data.get("stabilizers",[]))
    if not raw:raise ValueError("At least one independent stabilizer required")
    signs=tuple(data.get("signs",[int(s.startswith("-")) for s in raw]))
    if len(signs)!=len(raw) or any(type(s) is not int or s not in (0,1) for s in signs):raise ValueError("Binary generator signs required")
    code=StabilizerCode.from_dict(dict(data,generators=[s.lstrip("+-") for s in raw]))
    if code.rank!=len(code.generators):raise ValueError("Dependent stabilizers: supply an independent generating basis")
    pairs=logical_basis(code)
    if "logicals" in data:
        supplied=[tuple(Pauli.parse(s) for s in pair) for pair in data["logicals"]]
        if len(supplied)!=code.k or any(len(p)!=2 for p in supplied):raise ValueError("Logical pair count")
        flat=[p for pair in supplied for p in pair]
        if any(p.n!=code.n or code.syndrome(p) or code.is_stabilizer(p) for p in flat):raise ValueError("Logical/stabilizer inconsistency")
        for i,a in enumerate(flat):
            for j,b in enumerate(flat):
                if a.symplectic(b)!=int(i//2==j//2 and i!=j):raise ValueError("Logical commutation")
    return CodeInput(code,signs,dict(data.get("metadata",{}),known_distance_claim=data.get("distance"),derived_logicals=[[str(x),str(z)] for x,z in pairs]))
