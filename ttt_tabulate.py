# Auto-extracted from the Code Words article
import logic as E; E.ChoiceNode = E.memoize(E.ChoiceNode)
import tictactoe as T

def exhaust(human_to_move):
    for AI_to_move in T.successors(human_to_move):
        if T.successors(AI_to_move):
            all_responses[AI_to_move] = response = T.max_play(AI_to_move)
            exhaust(response)
        else:
            all_responses[AI_to_move] = tuple(reversed(AI_to_move))

all_responses = {}
exhaust(T.empty_grid)
O_tables = [{grid: (Os2>>square)&1
             for grid,(_,Os2) in all_responses.items()}
            for square in range(9)]
squares = range(9)
def combine(xs, os): return tuple(xs) + tuple(os)

XO_variables = combine((E.Variable('x%d' % k) for k in squares),
                       (E.Variable('o%d' % k) for k in squares))

def XO_values((Os,Xs)):
    return combine(((Xs>>k)&1 for k in squares),
                   ((Os>>k)&1 for k in squares))

O_nodes = [E.express(XO_variables, {XO_values(grid): value
                                    for grid, value in table.items()})
           for table in O_tables]
squares = (4, 0,2,6,8,  7,1,3,5)
def combine(xs, os): return sum(zip(xs, os), ())
def express(variables, table):
    if not table:
        return const0      # (Can you be cleverer here?)
    elif len(table) == 1:
        return Constant(table.values()[0])
    else:
        first_var, rest_vars = variables[0], variables[1:]
        # The new logic: if first_var takes on only one value
        # in the table...
        domain = set(row[0] for row in table.keys())
        if len(domain) == 1:
            # ...then just assume it'll take that value in the input.
            value = next(iter(domain))
            return express(rest_vars, subst_for_first_var(table, value))
        # Otherwise as before.
        return first_var(express(rest_vars, subst_for_first_var(table, 0)),
                         express(rest_vars, subst_for_first_var(table, 1)))
