"""
Solve logic puzzles.
TODO: compare to http://www.eecs.berkeley.edu/~bh/v3ch2/math.html
"""

import operator
from peglet import Parser
import dd

def mk_var(name):
    return dd.Variable(enter(name))

var_names = []
def enter(name):
    for v, vname in enumerate(var_names):
        if vname == name:
            return v
    v = len(var_names)
    var_names.append(name)
    return v

# XXX whitespace *with* a newline shouldn't be an AND -- too error-prone.
# Only with lhs and rhs on the same line should whitespace be AND.
# 
# XXX what's a good precedence/associativity for impl?
grammar = r"""
formula  = _ expr !.

expr     = sentence , _ expr  mk_and
         | sentence
sentence = sum /=/ _ sum      mk_eqv
         | sum
sum      = term \| _ sum      mk_or
         | term => _ term     mk_impl
         | term
term     = factor term        mk_and
         | factor
factor   = ~ _ primary        mk_not
         | primary
primary  = \( _ expr \) _
         | id _               mk_var

id       = ([A-Za-z_]\w*) _
_        = (?:\s|#[^\n]*)*
"""
parse = Parser(grammar,
               mk_eqv  = dd.Equiv,
               mk_impl = dd.Implies,
               mk_and  = operator.and_,
               mk_or   = operator.or_,
               mk_not  = operator.inv,
               mk_var  = mk_var)

def solve(puzzle_text):
    condition, = parse(puzzle_text)
    if dd.is_valid(condition):
        print("Valid.")
    else:
        show(dd.satisfy(condition, 1))

def show(opt_env):
    if opt_env is None:
        print("Unsatisfiable.")
    else:
        for k, v in sorted(opt_env.items()):
            if k is not None:
                print("%s%s" % ("" if v else "~", var_names[k]))

## solve(' hey (there | ~there), ~hey | ~there')
#. hey
#. ~there
## solve(' hey (there, ~there)')
#. Unsatisfiable.
## solve('a=>b = ~b=>~a')
#. Valid.


if __name__ == '__main__':
    import sys
    solve(sys.stdin.read())  # (try it on carroll)
