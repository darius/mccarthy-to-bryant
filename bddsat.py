"""
Use BDDs to solve SAT problems, given as a list of lists of literals,
where a literal is a nonzero int whose absolute value denotes a variable.
"""

import dd

def solve(clauses):
    node = conjoin(map(disjoin, clauses))
    return dd.satisfy(node, 1)

def conjoin(nodes):
    return reduce(lambda x, y: x & y, nodes)

def disjoin(literals):
    result = dd.lit0
    for lit in literals:
        v = dd.Variable(abs(lit))
        result |= v if 0 < lit else ~v
    return result
