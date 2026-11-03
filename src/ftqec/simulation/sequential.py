"""Union-bound Hoeffding confidence sequence at deterministic batch looks."""
import math

def confidence(failures,shots,look,alpha=.05):
    if not shots:return [0.,1.]
    if look<1 or not 0<alpha<1:raise ValueError("look/alpha")
    # alpha_t=alpha/(t(t+1)); sum over all positive t is alpha.
    radius=math.sqrt(math.log(2*look*(look+1)/alpha)/(2*shots));p=failures/shots
    return [max(0.,p-radius),min(1.,p+radius)]

def combine(batches,alpha=.05):
    if not batches:raise ValueError("At least one simulation batch required")
    if len({b.get("decoder") for b in batches})>1:raise ValueError("Cannot combine different decoders")
    shots=sum(b["shots"] for b in batches);failures=sum(b["failures"] for b in batches)
    return dict(decoder=batches[0].get("decoder"),noise=batches[0].get("noise"),p=batches[0].get("p"),shots=shots,failures=failures,rate=failures/shots if shots else 0.,confidence=confidence(failures,shots,len(batches),alpha),
        look=len(batches),alpha=alpha,method="Hoeffding alpha spending alpha/(look*(look+1))",decoder_unknown=sum(b["decoder_unknown"] for b in batches),seeds=[b["seed"] for b in batches])
