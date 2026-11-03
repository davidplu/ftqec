"""Code-only hook ordering. Candidate guidance is never a circuit certificate."""
from itertools import permutations
import random
from ..codes.pauli import Pauli
from ..codes.logicals import logical_basis, logical_effect
from ..certification.structural import graph, produce


class Effects:
    def __init__(self, values): self.values = sorted(values)
    def rows(self):
        for i, (d, l) in enumerate(self.values): yield i, "X", d, l, 0


def channel_masks(code):
    pairs = logical_basis(code)
    masks = []
    for bit in range(2 * code.k):
        p = pairs[bit // 2][1 if bit % 2 == 0 else 0]
        axes = set(str(p)) - {"I"}
        if len(axes) != 1: return None
        masks.append([1 << i for i, g in enumerate(code.generators)
                      if set(str(g)) - {"I"} == axes])
    return masks


def hook_orders(inp, target, seed, option_limit=48, graph_work=2000000):
    """Greedily retain the requested data-effect graph bound as hooks are added.

    Uses only stabilizers and derived logicals, not coordinates, names, known
    schedules or reference circuits. Full physical faults are certified later.
    Bounded option sampling is reported, never called exhaustive optimization.
    """
    code = inp.code
    masks = channel_masks(code)
    if not masks or any(len(set(str(g)) - {"I"}) != 1 for g in code.generators):
        return None, dict(status="INAPPLICABLE", reason="non-CSS logical/check channel")
    pairs = logical_basis(code)
    def effect(p): return code.syndrome(p), logical_effect(p, pairs)
    base = {effect(Pauli(code.n, (1 << q) if a in "XY" else 0,
                        (1 << q) if a in "YZ" else 0))
            for q in range(code.n) for a in "XYZ"}
    score_cache = {}
    def score(items):
        key = frozenset(items)
        if key in score_cache:return score_cache[key]
        lower = target
        for bit, selected in enumerate(masks):
            g = graph(Effects(items), selected, bit)
            if g is None: return 0
            proof = produce(g, target, work_limit=graph_work)
            if not proof["complete"]: return 0
            lower = min(lower, proof["lower_bound"])
        score_cache[key] = lower
        return lower
    rng = random.Random(seed)
    checks = list(range(len(code.generators))); rng.shuffle(checks)
    orders = [None] * len(checks); history = []; tried = 0
    for check in checks:
        score_cache.clear()
        p = code.generators[check]
        support = [q for q in range(code.n) if (p.x | p.z) >> q & 1]
        if len(support) <= 4:
            options = list(permutations(support)); rng.shuffle(options)
        else:
            options = [tuple(support)]
            for _ in range(option_limit - 1):
                order = list(support); rng.shuffle(order); options.append(tuple(order))
            options = list(dict.fromkeys(options))
        best = None
        for order in options[:option_limit]:
            effects = set(); suffix = Pauli(code.n)
            for q in reversed(order):
                for axis in "IXYZ":
                    single = Pauli(code.n, (1 << q) if axis in "XY" else 0,
                                   (1 << q) if axis in "YZ" else 0)
                    effects.add(effect(suffix ^ single))
                suffix = suffix ^ Pauli(code.n, (1 << q) if p.x >> q & 1 else 0,
                                        (1 << q) if p.z >> q & 1 else 0)
            value = score(base | effects); tried += 1
            if best is None or value > best[0]: best = value, order, effects
            if value >= target: break
        orders[check] = best[1]; base |= best[2]
        history.append(dict(check=check, guiding_bound=best[0]))
    return tuple(orders), dict(status="GENERATED", method="code_only_greedy_hook_graph",
                               target=target, options_examined=tried, history=history,
                               qualification="guidance only; complete physical certification required")


def generate(inp, seed, target, guided=True, parallel=False, joint=False):
    from .population import sample, Genome
    g = sample(inp, seed, target)
    if guided and parallel and seed % 8 == 0:
        from .coloring import colored_orders
        choice, receipt = colored_orders(inp,target,seed,joint=True) if joint else (None,None)
        if choice is not None:
            orders,layers=choice
            return Genome("bare",orders,g.checks,1,False,schedule="joint_colored",interaction_layers=layers,native_css=True),receipt
        choice, receipt = colored_orders(inp,target,seed)
        if choice is not None:
            orders,layers=choice
            return Genome("bare",orders,g.checks,1,False,schedule="colored",interaction_layers=layers),receipt

    if guided and seed % 4 == 0:
        orders, receipt = hook_orders(inp, target, seed)
        if orders is not None:
            rng = random.Random(seed)
            g = Genome("bare", orders, g.checks, rng.choice((1, target)),
                       rng.choice((True, False)), False, (), "single", 1,
                       rng.choice(("check_serial", "axis_grouped")))
            return g, receipt
        return g, receipt
    return g, dict(status="GENERATED", method="random_population", target=target)
