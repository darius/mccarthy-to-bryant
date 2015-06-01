"""
Check some adder implementations.
"""
# TODO: symbolically test equivalence with a fancier adder circuit
#       rename .rank to .var?

import bdd

## test_adder(4, ripple_carry_add)
#. 'passed'
## test_adder(4, ripple_carry_add, interleaved=False)
#. 'passed'

def test_adder(n, add, interleaved=True):
    "Make an n-bit adder and test it exhaustively."
    c_in = bdd.Variable(-1)
    inputs = map(bdd.Variable, range(2*n))
    if interleaved:
        A = inputs[0::2]
        B = inputs[1::2]
    else:
        A = inputs[:n]
        B = inputs[n:]
    S, c_out = add(A, B, c_in)
    for av in range(2**n):
        for bv in range(2**n):
            for civ in 0, 1:
                env = {c_in.rank: civ}
                env.update(env_from_uint(A, av))
                env.update(env_from_uint(B, bv))
                cov = c_out.evaluate(env)
                sv = uint_from_bdds(S, env)
                assert (cov << n) + sv == av + bv + civ
    return 'passed'

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
