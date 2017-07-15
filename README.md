Code for ["The language of choice"](https://codewords.recurse.com/issues/four/the-language-of-choice).

logic.py and utils.py go with the first half. Then
ttt_tabulate.py/ttt_tabulate_3way.py. bdd.py goes with the rest.

Generalized to n-way decisions, in nway_logic.py and dd.py.

lua/ has a LuaJIT port, to check for reasonable performance when not
stuck with CPython.

Other files are for testing and other demos, e.g. puzzler.py,
nqueens.py, problems.py.

play.{html,js} tried to animate the choice-tree transformations, but
it's unfinished.
