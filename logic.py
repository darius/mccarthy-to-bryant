"""
Propositional logic in terms of decision trees: IF-THEN-ELSE or CASE expressions.
For simplicity we assume variables all have the same, finite domain: currently
(0, 1). But I think I'll want to make it 3-way for more-efficient tic-tac-toe.
"""

from utils import memoize

class Node(object):
    "A decision-tree node."
    def evaluate(self, env):
        "My value when variables are set according to env, a dictionary."
        abstract
    def size(self):
        "How many choice nodes make up my subtree."
        return 0
    def find(self, goal, env):
        """Generate (partial) environments that extend `env`, in which
        I evaluate to `goal`."""
        abstract
    def __call__(self, *branches):
        return Choice(self, *branches)

Node.__invert__ = lambda self:        Choice(self, lit1, lit0)
Node.__and__    = lambda self, other: Choice(self, lit0, other)
Node.__or__     = lambda self, other: Choice(self, other, lit1)
Node.__xor__    = lambda self, other: Choice(self, other, ~other)

def Implies(p, q): return Choice(p, lit1, q)
def Equiv(p, q):   return Choice(p, ~q, q)

## ~lit0 ^ Variable('x')
#. (x `(1 `0` 0)` (1 `x` 0))

class LiteralNode(Node):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return repr(self.value)
    def evaluate(self, env):
        return self.value
    def find(self, goal, env):
        if self.value == goal:
            yield env

class VariableNode(Node):
    def __init__(self, name):
        assert isinstance(name, str)
        self.name = name
    def __repr__(self):
        return self.name
    def evaluate(self, env):
        return env[self]
    def find(self, goal, env):
        if self not in env:
            yield extend(env, self, goal)
        elif env[self] == goal:
            yield env

class ChoiceNode(Node):
    def __init__(self, index, *branches):
        self.index, self.branches = index, branches
    def __repr__(self):
        if len(self.branches) == 2:
            return '(%r `%r` %r)' % (self.branches[0], self.index, self.branches[1])
        else:
            return '(%r: %s)' % (self.index, ', '.join(map(repr, self.branches)))
    def evaluate(self, env):
        return self.branches[self.index.evaluate(env)].evaluate(env)
    def size(self):
        return sum((node.size() for node in self.branches), 1)
    def find(self, goal, env):
        for i, branch in enumerate(self.branches):
            for env1 in self.index.find(i, env):
                for env2 in branch.find(goal, env1):
                    yield env2

def extend(env, var, value):
    result = dict(env)
    result[var] = value
    return result

Literal = memoize(LiteralNode)
lit0, lit1 = Literal(0), Literal(1)

Variable = VariableNode

def Choice(index, *branches):
    if len(set(branches)) == 1:
        return branches[0]
    elif all(branch is Literal(i) for i, branch in enumerate(branches)):
        return index
    else:
        return ChoiceNode(index, *branches)

#Choice = ChoiceNode

def naively_express(variables, table):
    tree = lit0 # A value for any omitted rows; it could just as well be `lit1`.
    for key, value in table.items():
        tree = Choice(match(variables, key), tree, Literal(value))
    return tree

def match(variables, values):
    """Return an expression that evaluates to 1 just when every variable
    has the corresponding value."""
    tree = lit1
    for var, value in zip(variables, values):
        tree = (Choice(var, lit0, tree) if value else
                Choice(var, tree, lit0))
    return tree

def check(express, names, table):
    variables = map(Variable, names)
    tree = express(variables, table)
    for keys, value in table.items():
        assert value == tree.evaluate(dict(zip(variables, keys))), \
           "Mismatch at %r: %r" % (keys, tree)
    return tree

def boole_express(variables, table, cleaver=lambda variables, table: 0):
    if not table:
        return lit0      # Or 1, doesn't matter.
    elif len(table) == 1:
        return Literal(next(iter(table.values())))
    else:
        v = cleaver(variables, table)
        return Choice(variables[v], *[boole_express(remove(variables, v),
                                                    project(table, v, value),
                                                    cleaver)
                                      for value in var_range(table, v)])

def var_range(table, v):
    return range(max(keys[v] for keys in table.keys()) + 1)

def remove(xs, v):
    return xs[:v]+xs[v+1:]

def project(table, v, v_value):
    return {remove(keys, v): output
            for keys, output in table.items() if keys[v] == v_value}

def discerningly_express(variables, table):
    return boole_express(variables, table, cleaver=most_informative)

def most_informative(variables, table):
    "Pick the most-informative variable to split on."
    def discernment(v):
        """Return a score that's higher, the better that branching on
        variables[v] sifts the table's values into 0's in one branch
        and 1's in the other."""
        # (This is a good measure only for exhaustive tables:)
        return abs(  imbalance(project(table, v, 0))
                   - imbalance(project(table, v, 1)))
    return max(range(len(variables)), key=discernment)

from collections import Counter

def imbalance(table):
    tallies = Counter(table.values())
    return tallies.get(1, 0) - tallies.get(0, 0)

and_ = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1}

## check(naively_express, 'AB', and_)
#. (0 `B` A)
## check(boole_express, 'AB', and_)
#. (0 `A` B)
## check(discerningly_express, 'AB', and_)
#. (0 `A` B)

from itertools import product
majority = {row: max(row, key=row.count)
            for row in product((0,1), (0,1), (0,1))}
## check(naively_express, 'ABC', majority)
#. ((((((((0 `C` (0 `B` (1 `A` 0))) `((0 `B` A) `C` 0)` 1) `((A `B` 0) `C` 0)` 0) `(0 `C` ((1 `A` 0) `B` 0))` 0) `(0 `C` (A `B` 0))` 1) `(((1 `A` 0) `B` 0) `C` 0)` 0) `((0 `B` (1 `A` 0)) `C` 0)` 0) `(0 `C` (0 `B` A))` 1)
## check(boole_express, 'ABC', majority)
#. ((0 `B` C) `A` (C `B` 1))
## check(discerningly_express, 'ABC', majority)
#. ((0 `B` C) `A` (C `B` 1))

parity = {row: reduce(lambda x, y: x^y, row)
          for row in product(*((0,1),) * 5)}
## check(boole_express, 'ABCDE', parity)
#. ((((E `D` (1 `E` 0)) `C` ((1 `E` 0) `D` E)) `B` (((1 `E` 0) `D` E) `C` (E `D` (1 `E` 0)))) `A` ((((1 `E` 0) `D` E) `C` (E `D` (1 `E` 0))) `B` ((E `D` (1 `E` 0)) `C` ((1 `E` 0) `D` E))))

## ChoiceNode = memoize(ChoiceNode)

## len(ChoiceNode._memos)
#. 0
## check(boole_express, 'ABCDE', parity)
#. ((((E `D` (1 `E` 0)) `C` ((1 `E` 0) `D` E)) `B` (((1 `E` 0) `D` E) `C` (E `D` (1 `E` 0)))) `A` ((((1 `E` 0) `D` E) `C` (E `D` (1 `E` 0))) `B` ((E `D` (1 `E` 0)) `C` ((1 `E` 0) `D` E))))
## len(ChoiceNode._memos)
#. 8
