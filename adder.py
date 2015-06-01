"""
Check some adder implementations.
"""

import bdd

## test_adder(4, ripple_carry_add)
#. 'passed'

def test_adder(n, add):
    "Make an n-bit adder and test it exhaustively."
    c_in = bdd.Variable(-1)
    A = map(bdd.Variable, range(0, n))
    B = map(bdd.Variable, range(n, 2*n))
    c_out, Sum = add(A, B, c_in) # XXX confusable name
    for av in range(2**n):
        for bv in range(2**n):
            for civ in 0, 1:
                env = {c_in.rank: civ}
                env.update(env_from_uint(A, av))
                env.update(env_from_uint(B, bv))
                cov = c_out.evaluate(env)
                sv = uint_from_bdds(Sum, env)
                assert (cov << n) + sv == av + bv + civ
    return 'passed'
    # TODO: symbolically test equivalence with a fancier adder circuit
    #       pick a better ranking of variables (interleaved)
    #       rename .rank to .var?

def env_from_uint(bit_nodes, value):
    return {node.rank: (value >> p) & 1 for p, node in enumerate(bit_nodes)}

def uint_from_bdds(bit_nodes, env):
    return sum(node.evaluate(env) << p for p, node in enumerate(bit_nodes))

def ripple_carry_add(A, B, carry):
    "The simplest adder in logic gates."
    assert len(A) == len(B)
    out = []
    for a, b in zip(A, B):
        carry, sum = add3(a, b, carry)
        out.append(sum)
    return carry, tuple(out)

def add3(a, b, c):
    "Compute the msb and lsb of a+b+c."
    c1, s1 = add2(a, b)
    c2, s2 = add2(s1, c)
    return c1 | c2, s2

def add2(a, b):
    "Compute the msb and lsb of a+b."
    return a & b, a ^ b
