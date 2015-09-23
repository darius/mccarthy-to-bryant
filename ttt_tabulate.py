"""
Creating the tic-tac-toe machine by tabulating max_play.
"""

import logic as E; E.ChoiceNode = E.memoize(E.ChoiceNode)
import tictactoe as T

def exhaust(grid):
    for grid2 in T.successors(grid):
        if grid2 in all_responses: continue
        if T.successors(grid2):
            all_responses[grid2] = response = T.max_play(grid2)
            exhaust(response)
        else:
            all_responses[grid2] = tuple(reversed(grid2))

all_responses = {}
exhaust(T.empty_grid)

## len(all_responses)
#. 427

O_tables = [{grid: (Os2>>square)&1
             for grid,(_,Os2) in all_responses.items()}
            for square in range(9)]

#squares = range(9)
squares = (4, 0,2,6,8,  7,1,3,5)

#def combine(xs, os): return tuple(xs) + tuple(os)
def combine(xs, os): return sum(zip(xs, os), ())

XO_variables = combine((E.Variable('x%d' % k) for k in squares),
                       (E.Variable('o%d' % k) for k in squares))

def XO_values((Os,Xs)):
    return combine(((Xs>>k)&1 for k in squares),
                   ((Os>>k)&1 for k in squares))

O_nodes = [E.boole_express(XO_variables, {XO_values(grid): value
                                          for grid, value in table.items()})
           for table in O_tables]
## sum(node.size() for node in O_nodes)
#. 1053
## len(E.ChoiceNode._memos)
#. 620
