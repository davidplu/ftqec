"""Transparent empirical costs; censored observations supply lower bounds only."""
import math,statistics
from dataclasses import dataclass

@dataclass(frozen=True)
class Estimate:
    cpu: float
    samples: int
    censored: int
    method: str
    lower_bound: float

class CostModel:
    def __init__(self,observations=()):self.observations=list(observations)
    def estimate(self,tier,operations,target):
        records=[r for r in self.observations if r.get("supported",True) and r["tier"]==tier and (tier!="certify" or r["target"]==target)]
        complete=[r for r in records if not r["censored"]]
        exponent=2 if tier=="certify" and target>=3 else 1
        scale=max(1,operations)**exponent
        rates=[r["cpu"]/max(1,r["operations"])**exponent for r in complete]
        lower=max([r["cpu"]*scale/max(1,r["operations"])**exponent for r in records if r["censored"]]+[0.])
        # Priors are explicit uncalibrated costs, never measurements.
        prior={"screen":.04,"simulation":.08,"certify":.05 if target==2 else .5}[tier]*max(1,operations)/100
        value=max(lower,statistics.median(rates)*scale if rates else prior,.000001)
        return Estimate(value,len(complete),len(records)-len(complete),"median_size_scaled" if rates else "uncalibrated_prior",lower)
    def rejection_probability(self):
        rows=[r for r in self.observations if r["tier"]=="screen" and not r["censored"]]
        return (1+sum(r["status"]=="FAULT_INVALID" for r in rows))/(2+len(rows))
    def learned_prediction(self,tier,operations,target):
        # Interpretable log(cost) = intercept + slope log(operation count), completed labels only.
        rows=[r for r in self.observations if r.get("supported",True) and r["tier"]==tier and r["target"]==target and not r["censored"] and r["cpu"]>0]
        if len(rows)<4:return None
        xs=[math.log(max(1,r["operations"])) for r in rows];ys=[math.log(r["cpu"]) for r in rows]
        mx=statistics.mean(xs);my=statistics.mean(ys);den=sum((x-mx)**2 for x in xs)
        slope=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den if den else 0.
        return math.exp(my+slope*(math.log(max(1,operations))-mx))
