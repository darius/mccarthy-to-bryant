"""
Adapted from https://github.com/darius/sturm/blob/master/tictactoe.py
"""

# Utilities

def average(ns):
    ns = list(ns)
    return float(sum(ns)) / len(ns)

def memoize(f):
    "Return a function like f that remembers and reuses results of past calls."
    def memo_f(*args):
        try:
            return memo_f._memos[args]
        except KeyError:
            memo_f._memos[args] = value = f(*args)
            return value
    memo_f._memos = {}
    return memo_f


# Strategies. They all presume the game's not over.

def drunk_play(grid):
    "Beatable, but not so stupid it seems mindless."
    return min(successors(grid), key=drunk_value)

def spock_play(grid):
    "Play supposing both players are rational."
    return min(successors(grid), key=evaluate)

def max_play(grid):
    "Play like Spock, except breaking ties by drunk_value."
    return min(successors(grid),
               key=lambda succ: (evaluate(succ), drunk_value(succ)))

@memoize
def drunk_value(grid):
    "Return the expected value to the player if both players play at random."
    if is_won(grid): return -1
    succs = list(successors(grid))
    return -average(map(drunk_value, succs)) if succs else 0

@memoize
def evaluate(grid):
    "Return the value for the player to move, assuming perfect play."
    if is_won(grid): return -1
    succs = list(successors(grid))
    return -min(map(evaluate, succs)) if succs else 0
    
# (Some scaffolding to view examples inline, below:)
def multiview(grids): print '\n'.join(reduce(beside, [view(g).split('\n') for g in grids])),
def beside(block1, block2): return map('  '.join, zip(block1, block2))

# Example: starting from this board:
## print view((0610, 0061)),
#.  X X .
#.  O O X
#.  . . O
# Spock examines these choices:
## multiview(successors((0610, 0061)))
#.  X X .   X X .   X X X
#.  O O X   O O X   O O X
#.  . X O   X . O   . . O
# and picks the win:
## print view(spock_play((0610, 0061))),
#.  X X X
#.  O O X
#.  . . O


# We represent a tic-tac-toe grid as a pair of bit-vectors (p,q), p
# for the player to move, q for their opponent. So p has 9
# bit-positions, one for each square in the grid, with a 1 in the
# positions where the player has already moved; and likewise for the
# other player's moves in q. The least significant bit is the
# lower-right square; the most significant is upper-left.

empty_grid = 0, 0

def is_won(grid):
    "Did the latest move win the game?"
    p, q = grid
    return any(way == (way & q) for way in ways_to_win)

# Numbers like 0o... are in octal: 3 bits/digit, thus one grid-row per digit.
ways_to_win = (0o700, 0o070, 0o007, 0o444, 0o222, 0o111, 0o421, 0o124)

## multiview((0, way) for way in ways_to_win)
#.  X X X   . . .   . . .   X . .   . X .   . . X   X . .   . . X
#.  . . .   X X X   . . .   X . .   . X .   . . X   . X .   . X .
#.  . . .   . . .   X X X   X . .   . X .   . . X   . . X   X . .

def successors(grid):
    "Return the possible grids resulting from p's moves."
    return filter(None, (apply_move(grid, move) for move in range(9)))

## multiview(successors(empty_grid))
#.  . . .   . . .   . . .   . . .   . . .   . . .   . . X   . X .   X . .
#.  . . .   . . .   . . .   . . X   . X .   X . .   . . .   . . .   . . .
#.  . . X   . X .   X . .   . . .   . . .   . . .   . . .   . . .   . . .

def apply_move(grid, move):
    "Try to move: return a new grid, or None if illegal."
    p, q = grid
    bit = 1 << move
    return (q, p | bit) if 0 == (bit & (p | q)) else None

## example = ((0112, 0221))
## multiview([example, apply_move(example, 2)])
#.  . O X   . O X
#.  . O X   . O X
#.  . X O   X X O


# Symmetries

def representative(grid):
    "Return a canonical symmetric equivalent of grid."
    return min(equivalents(grid))

## multiview(equivalents((0610, 0061)))
#.  X X .   . X O   O . .   . O X   . . O   O X .   . X X   X O .
#.  O O X   X O .   X O O   . O X   O O X   . O X   X O O   X O .
#.  . . O   X O .   . X X   O X .   X X .   . O X   O . .   . X O

def equivalents(grid):
    return rotations(grid) + rotations(permute(flip, grid))

def rotations(grid):
    grids = [grid]
    for _ in range(3):
        grids.append(permute(rotate, grids[-1]))
    return grids

def permute(permutation, grid):
    return tuple(map(permutation, grid))

def flip(bits):
    return ((0o007&bits) << 6) | (0o070&bits) | (bits >> 6)

def rotate(bits):
    (b2,b5,b8,
     b1,b4,b7,
     b0,b3,b6) = tuple(player_bits(bits))
    return (((((((b8*2+b7)*2+b6)*2+b5)*2+b4)*2+b3)*2+b2)*2+b1)*2+b0


# The presentation layer

def view(grid):
    "Show a grid human-readably."
    p_mark, q_mark = player_marks(grid)
    return grid_format % tuple(p_mark if by_p else q_mark if by_q else '.'
                               for by_p, by_q in zip(*map(player_bits, grid)))

grid_format = '\n'.join([' %s %s %s'] * 3)

def player_marks(grid):
    "Return two results: the player's mark and their opponent's."
    p, q = grid
    return 'XO' if sum(player_bits(p)) == sum(player_bits(q)) else 'OX'

def player_bits(bits):
    return ((bits >> i) & 1 for i in reversed(range(9)))

def whose_move(grid):
    "Return the mark of the player to move."
    return player_marks(grid)[0]
