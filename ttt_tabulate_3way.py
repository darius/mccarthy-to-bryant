"""
Creating the tic-tac-toe machine by tabulating max_play.
(Using 3-way mux gates this time.)
"""

from collections import Counter

import nway_logic as E; E.ChoiceNode = E.memoize(E.ChoiceNode)
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

def boole_express(variables, table, cleaver=lambda variables, table: 0):
    def recur(variables, table, parent):
        if not table:
            return E.Literal(most_popular(parent.values()))
        elif len(table) == 1:
            return E.Literal(next(iter(table.values())))
        else:
            v = cleaver(variables, table)
            return variables[v](*[recur(E.remove(variables, v),
                                        E.project(table, v, value),
                                        table)
                                  for value in (0, 1, 2)])
    return recur(variables, table, table)

def most_popular(values):
    (value, count), = Counter(values).most_common(1)
    return value

O_tables = [{grid: (Os2>>square)&1
             for grid,(_,Os2) in all_responses.items()}
            for square in range(9)]

#squares = range(9)
squares = (4, 0,2,6,8,  7,1,3,5)

XO_variables = tuple(E.Variable('xo%d' % k) for k in squares)

def XO_values((Os,Xs)):
    return tuple(1 if (Xs>>k)&1 else 2 if (Os>>k)&1 else 0
                 for k in squares)

O_nodes = [boole_express(XO_variables, {XO_values(grid): value
                                        for grid, value in table.items()})
           for table in O_tables]
# O_nodes
## sum(node.size() for node in O_nodes)
#. 811
## len(E.ChoiceNode._memos)
#. 379
