"""
Check some adder implementations.
"""

import math
from utils import memoize
import dd

## test_adder(4, ripple_carry_add)
#. 'passed'
## test_adder(4, ripple_carry_add, interleaved=False)
#. 'passed'

## test_adder(1, carry_lookahead_add)
#. 'passed'
## test_adder(2, carry_lookahead_add)
#. 'passed'
## test_adder(3, carry_lookahead_add)
#. 'passed'
## test_adder(4, carry_lookahead_add)
#. 'passed'

## test_equivalent(1, ripple_carry_add, carry_lookahead_add)
#. 'passed'
## test_equivalent(4, ripple_carry_add, carry_lookahead_add)
#. 'passed'
# test_equivalent(12, ripple_carry_add, carry_lookahead_add, interleaved=False)
## test_equivalent(32, ripple_carry_add, carry_lookahead_add)
#. 'passed'

def test_equivalent(n, adder1, adder2, interleaved=True):
    c_in, A, B = make_alu_inputs(n, interleaved)
    S1, c_out1 = adder1(A, B, c_in)
    S2, c_out2 = adder2(A, B, c_in)
    assert len(S1) == len(S2) == len(A)
    assert dd.Equiv(c_out1, c_out2) == dd.lit1
    for s1, s2 in zip(S1, S2):
        assert dd.Equiv(s1, s2) == dd.lit1
    return 'passed'

def test_adder(n, add, interleaved=True):
    "Make an n-bit adder and test it exhaustively."
    c_in, A, B = make_alu_inputs(n, interleaved)
    S, c_out = add(A, B, c_in)
    for av in range(2**n):
        for bv in range(2**n):
            for civ in 0, 1:
                env = {c_in.rank: civ}
                env.update(env_from_uint(A, av))
                env.update(env_from_uint(B, bv))
                cov = c_out.evaluate(env)
                sv = uint_from_bdds(S, env)
                assert (cov << n) + sv == av + bv + civ, ("%d + %d + %d => (%d<<%d) + %d"
                                                          % (av, bv, civ, cov, n, sv))
    return 'passed'

def make_alu_inputs(n, interleaved):
    c_in = dd.Variable(-1)
    inputs = map(dd.Variable, range(2*n))
    if interleaved:
        A = inputs[0::2]
        B = inputs[1::2]
    else:
        A = inputs[:n]
        B = inputs[n:]
    return c_in, A, B

def env_from_uint(bit_nodes, value):
    return {node.rank: (value >> p) & 1 for p, node in enumerate(bit_nodes)}

def uint_from_bdds(bit_nodes, env):
    return sum(node.evaluate(env) << p for p, node in enumerate(bit_nodes))

def ripple_carry_add(A, B, carry):
    "The simplest adder in logic gates."
    assert len(A) == len(B)
    S = []
    for a, b in zip(A, B):
        sum, carry = add3(a, b, carry)
        S.append(sum)
    return tuple(S), carry

def add3(a, b, c):
    "Compute the lsb and msb of a+b+c."
    s1, c1 = add2(a, b)
    s2, c2 = add2(s1, c)
    return s2, c1 | c2

def add2(a, b):
    "Compute the lsb and msb of a+b."
    return a ^ b, a & b


def carry_lookahead_add(A, B, carry):
    assert len(A) == len(B)

    @memoize
    def lookahead(lo, nbits, assume_cin):
        if nbits == 0:
            return dd.Constant(assume_cin)
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
    return 2**int(math.log(n-1, 2))

def add2_constant(a, b, bit):
    if bit == 0: return add2(a, b)
    else:        return dd.Equiv(a, b), a|b
