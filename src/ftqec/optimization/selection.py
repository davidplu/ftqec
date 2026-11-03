def comparable_simulation(a,b):
    return all(a.get("simulation",{}).get(k)==b.get("simulation",{}).get(k) for k in ("decoder","noise","p"))

def dominates(a,b,keys):
    return all(a[k]<=b[k] for k in keys) and any(a[k]<b[k] for k in keys)

def pareto(rows,keys=("Q","D","QD","two_q_gates")):
    return [r for r in rows if not any(dominates(s["resources"],r["resources"],keys) for s in rows)]

def promising(rows):
    # Conservative confidence-interval dominance; uncertain families retain exploration.
    keep=[]
    for row in rows:
        lo=row["simulation"]["confidence"][0]
        if not any(comparable_simulation(s,row) and s["simulation"]["confidence"][1]<lo and dominates(s["resources"],row["resources"],("Q","D","two_q_gates")) for s in rows):keep.append(row)
    families={r["genome"]["family"] for r in rows}
    for family in sorted(families):
        if not any(r["genome"]["family"]==family for r in keep):keep.append(min((r for r in rows if r["genome"]["family"]==family),key=lambda r:r["simulation"]["confidence"][1]))
    return keep


def reliability_pareto(rows):
    candidates=[r for r in rows if "rate" in r.get("simulation",{})]
    keys=("Q","D","QD","two_q_gates","rate")
    def coordinates(row):return dict(row["resources"],rate=row["simulation"]["rate"])
    return [r for r in candidates if not any(comparable_simulation(s,r) and dominates(coordinates(s),coordinates(r),keys) for s in candidates)]
