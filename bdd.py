"BDDs; actually multiway DDs, and multiterminal if you change `num_terminals`."

from utils import memoize

num_terminals = 2
optimize = True

class Node(object):
    "A BDD node."
    __invert__ = lambda self:        self(lit1, lit0)
    __and__    = lambda self, other: self(lit0, other)
    __or__     = lambda self, other: self(other, lit1)
    __xor__    = lambda self, other: self(other, ~other)

def Equiv(p, q):   return p(~q, q)
def Implies(p, q): return p(lit1, q)

class ConstantNode(Node):
    rank = float('Inf')  # Greater than every variable.
    def __init__(self, value):     self.value = value
    def evaluate(self, env):       return self.value
    def __call__(self, *branches): return branches[self.value]

the_constants = tuple(map(ConstantNode, range(num_terminals)))
Constant = the_constants.__getitem__
lit0, lit1 = the_constants[:2]

def Variable(rank):
    return build_node(rank, the_constants)

class ChoiceNode(Node):
    def __init__(self, rank, branches):
        self.rank = rank
        self.branches = branches
        for b in branches: assert rank < b.rank
    def evaluate(self, env):
        return self.branches[env[self.rank]].evaluate(env)
    def __call__(self, *branches):
        if optimize: # (optional optimization)
            if len(set(branches)) == 1: return branches[0]
            if branches == the_constants: return self
        return build_choice(self, branches)

build_node = memoize(ChoiceNode)

@memoize
def build_choice(node, branches):
    top = min(node.rank, *[b.rank for b in branches])
    sbranches = tuple(subst(top, c, node)(*map_subst(top, c, branches))
                      for c in the_constants)
    return make_node(top, sbranches)

def make_node(rank, branches):
    if len(set(branches)) == 1: return branches[0]
    return build_node(rank, branches)

def map_subst(rank, replacement, nodes):
    return [subst(rank, replacement, e) for e in nodes]

def subst(rank, replacement, node):
    if   rank <  node.rank: return node   # N.B. we get here if node is a ConstantNode
    elif rank == node.rank: return replacement(*node.branches)
    else:                   return make_node(node.rank,
                                             map_subst(rank, replacement, node.branches))

def is_valid(node):
    return satisfy(node, 0) is None

def satisfy(node, goal):
    """Return the lexicographically first env such that
    node.evaluate(env) == goal, if there's any; else None.
    (The env may leave out variables that don't matter.)"""
    env = {}
    while isinstance(node, ChoiceNode):
        for value, branch in enumerate(node.branches):
            if isinstance(branch, ChoiceNode) or branch.value == goal:
                env[node.rank] = value
                node = branch
                break
        else:
            return None
    return env if node.value == goal else None


## x, y = map(Variable, (8, 9))
## is_valid(lit0), is_valid(lit1), is_valid(x)
#. (False, True, False)

## satisfy(~lit0, 0)
## satisfy(~lit0, 1)
#. {}

## satisfy(lit0, 0)
#. {}
## satisfy(lit0, 1)

## satisfy(x, 1)
#. {8: 1}
## satisfy(~x, 1)
#. {8: 0}
## satisfy(x&x, 1)
#. {8: 1}
## satisfy(x&~x, 1)
## satisfy(~x&~x, 1)
#. {8: 0}

## is_valid(Implies(Implies(Implies(x, y), x), x))
#. True
## is_valid(Implies(Implies(Implies(x, y), x), y))
#. False


a, b, c, d, p, q, r = map(Variable, range(7))

## is_valid(Equiv(a, lit0(a, b)))
#. True
## is_valid(Equiv(b, lit1(a, b)))
#. True
## is_valid(Equiv(p, p(lit0, lit1)))
#. True
## is_valid(Equiv(a, p(a, a)))
#. True
## is_valid(Equiv(p(a, c), p(a, p(b, c))))
#. True
## is_valid(Equiv(p(a, c), p(p(a, b), c)))
#. True
## is_valid(Equiv(q(p, r)(a, b), q(p(a, b), r(a, b))))
#. True
## is_valid(Equiv(q(p(a, b), p(c, d)), p(q(a, c), q(b, d))))
#. True
## is_valid(~(q(p(a, b), p(c, d)) ^ p(q(a, c), q(b, d))))
#. True
