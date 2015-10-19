# Auto-extracted from the Code Words article
from utils import memoize

class Node(object):
    "A binary-decision-diagram node."
    __invert__ = lambda self:        self(const1, const0)
    __and__    = lambda self, other: self(const0, other)
    __or__     = lambda self, other: self(other, const1)
    __xor__    = lambda self, other: self(other, ~other)

def Equiv(p, q):   return p(~q, q)
def Implies(p, q): return p(const1, q)
class ConstantNode(Node):
    rank = float('Inf')   # (Greater than any variable's rank.)
    def __init__(self, value):     self.value = value
    def evaluate(self, env):       return self.value
    def __call__(self, *branches): return branches[self.value]

Constant = memoize(ConstantNode)
const0, const1 = Constant(0), Constant(1)

def Variable(rank):
    return build_node(rank, const0, const1)

class ChoiceNode(Node):
    value = None    # (Explained below.)
    def __init__(self, rank, if0, if1):
        assert rank < if0.rank and rank < if1.rank
        self.rank = rank
        self.if0 = if0
        self.if1 = if1
    def evaluate(self, env):
        branch = (self.if0, self.if1)[env[self.rank]]
        return branch.evaluate(env)
    def __call__(self, if0, if1):
        if if0 is if1: return if0
        if (if0, if1) == (const0, const1):
            return self
        # The above cases usually save work, but aren't needed for correctness.
        return build_choice(self, if0, if1)

build_node = memoize(ChoiceNode)
@memoize
def build_choice(node, if0, if1):
    """Like Choice(node, if0, if1) in logic.py, but McCarthy-standardized,
    presupposing the arguments are all McCarthy-standardized."""
    top = min(node.rank, if0.rank, if1.rank)
    cases = [subst(node, top, value)(subst(if0, top, value),
                                     subst(if1, top, value))
             for value in (0, 1)]
    return make_node(top, *cases)

def make_node(rank, if0, if1):
    if if0 is if1: return if0
    return build_node(rank, if0, if1)

def subst(node, rank, value):
    """Specialize node to the case where variable #rank takes the given value.
    Again, node must be standardized."""
    if   rank <  node.rank: return node
    elif rank == node.rank: return (node.if0, node.if1)[value]
    else:                   return make_node(node.rank,
                                             subst(node.if0, rank, value),
                                             subst(node.if1, rank, value))
def is_valid(claim):
    return satisfy(claim, 0) is None

def satisfy(node, goal):
    """Return the lexicographically first env such that
    node.evaluate(env) == goal, if there's any; else None."""
    env = {}
    while isinstance(node, ChoiceNode):
        if   node.if0.value in (None, goal): node, env[node.rank] = node.if0, 0
        elif node.if1.value in (None, goal): node, env[node.rank] = node.if1, 1
        else:                                return None
    return env if node.value == goal else None
def ripple_carry_add(A, B, carry):
    "The simplest adder in logic gates."
    assert len(A) == len(B)
    S = []
    for a, b in zip(A, B):
        sum, carry = add3(a, b, carry)
        S.append(sum)
    return tuple(S), carry

def add3(a, b, c):
    "Compute the least- and most-significant bits of a+b+c."
    s1, c1 = add2(a, b)
    s2, c2 = add2(s1, c)
    return s2, c1 | c2

def add2(a, b):
    "Compute the least- and most-significant bits of a+b."
    return a ^ b, a & b
def carry_lookahead_add(A, B, carry):
    assert len(A) == len(B)

    @memoize # (to keep the circuit from blowing up in size)
    def lookahead(lo, nbits, assume_cin):
        if nbits == 0:
            return Constant(assume_cin)
        elif nbits == 1:
            s, c = add2_constant(A[lo], B[lo], assume_cin)
            return c
        else:
            m = preceding_power_of_2(nbits)
            return lookahead(lo, m, assume_cin)(lookahead(lo+m, nbits-m, 0),
                                                lookahead(lo+m, nbits-m, 1))

    # The carry at each place.
    C = [carry(lookahead(0, hi, 0),
               lookahead(0, hi, 1))
         for hi in range(len(A)+1)]

    return tuple(a^b^c for a,b,c in zip(A, B, C)), C[-1]

def preceding_power_of_2(n):
    import math
    return 2**int(math.log(n-1, 2))

def add2_constant(a, b, bit):
    if bit == 0: return add2(a, b)
    else:        return Equiv(a, b), a|b
def test_equivalent(n, adder1, adder2, interleaved=True):
    c_in, A, B = make_alu_inputs(n, interleaved)
    S1, c_out1 = adder1(A, B, c_in)
    S2, c_out2 = adder2(A, B, c_in)
    assert len(S1) == len(S2) == len(A)
    assert Equiv(c_out1, c_out2) == const1
    for s1, s2 in zip(S1, S2):
        assert Equiv(s1, s2) == const1
    return 'passed'

def make_alu_inputs(n, interleaved):
    c_in = Variable(-1)
    inputs = map(Variable, range(2*n))
    if interleaved:
        A = inputs[0::2]
        B = inputs[1::2]
    else:
        A = inputs[:n]
        B = inputs[n:]
    return c_in, A, B
