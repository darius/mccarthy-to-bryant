"""
Use BDDs to solve SAT problems from DIMACS files.
TODO: try the tableau method too
"""

import bddsat
import dimacs
import sat

# Some problems from http://toughsat.appspot.com/
filenames = ['problems/trivial.dimacs',
             'problems/factoring6.dimacs',
             'problems/factoring2.dimacs',
             'problems/subsetsum_random.dimacs',
             ]

def main():
    for filename in filenames:
        print(filename)
        _, problem = dimacs.load(filename)
        solution = bddsat.solve(problem)
        print(solution)
        if solution is not None:
            assert sat.is_satisfied(problem, solution)
        print

## main()
#. problems/trivial.dimacs
#. {1: 1, 2: 1}
#. 
#. problems/factoring6.dimacs
#. {1: 0, 2: 1, 3: 1, 4: 1, 5: 0, 6: 1, 7: 0, 8: 1, 9: 0, 10: 1, 11: 1, 12: 0, 13: 1, 14: 0}
#. 
#. problems/factoring2.dimacs
#. {1: 0, 2: 1, 3: 0, 4: 1, 5: 1, 6: 0, 7: 0, 8: 1, 9: 0, 10: 1, 11: 0, 12: 0, 13: 1, 14: 0, 15: 0, 16: 0, 17: 0, 18: 1, 19: 0, 20: 1, 21: 0, 22: 0, 23: 0, 24: 1, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0}
#. 
#. problems/subsetsum_random.dimacs
#. {1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0, 7: 1, 8: 1, 9: 1, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 1, 16: 1, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 1, 26: 1, 27: 0, 28: 0, 29: 0, 30: 0}
#. 

if __name__ == '__main__':
    main()
