"""
Check some adder implementations.
"""

import bdd

## test_adder(4, ripple_carry_add)

def test_adder(n, add):
    "Make an n-bit adder and test it exhaustively."
    c_in, = map(bdd.Variable, range(-1, 0))
    A = map(bdd.Variable, range(0, n))
    B = map(bdd.Variable, range(n, 2*n))
    c_out, Sum = add(A, B, c_in) # XXX confusable name
    for av in range(2**n):
        for bv in range(2**n):
            for civ in 0, 1:
                env = {}
                env[-1] = civ
                for p in range(n):
                    env[p]   = (av >> p) & 1
                    env[n+p] = (bv >> p) & 1
                cov = c_out.evaluate(env)
                sv = sum(sp.evaluate(env) << p for p, sp in enumerate(Sum))
                assert (cov << n) + sv == av + bv + civ
    # TODO: symbolically test equivalence with a fancier adder circuit
    #       nicer code above, making it easier to vary the variable ranking
    #       pick a better ranking of variables (interleaved)

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
