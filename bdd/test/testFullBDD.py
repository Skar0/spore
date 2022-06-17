import unittest
from functools import reduce

import dd.cudd as bdd

from bdd.bdd_util import decomp_data_file
from bdd.dpa2bdd import explicit2symbolic_path
from bdd.dpa2gpg import symb_dpa2gpg
from bdd.generalizedRecursive import generalized_recursive
from bdd.misc import bdd2int


def get_winning_regions(file):
    manager = bdd.BDD()
    input_signals, output_signals, automata_paths = decomp_data_file(file)

    manager.declare(*input_signals)
    manager.declare(*output_signals)

    automata = [explicit2symbolic_path(path, manager) for path in automata_paths]

    product = reduce(lambda a1, a2: a1.product(a2, manager), automata)

    arena, init = symb_dpa2gpg(product, input_signals, output_signals, manager)

    winning_region_player0, winning_region_player1 = generalized_recursive(arena, manager)

    computed_winning_0 = bdd2int(winning_region_player0, arena.vars, manager)
    computed_winning_1 = bdd2int(winning_region_player1, arena.vars, manager)

    return computed_winning_0, computed_winning_1


class TestFullBDD(unittest.TestCase):

    def setUp(self):
        self.arena_path = "./arenas/automata/"

    def test_recursive_generalized_solved_examples(self):
        """
        Checks the solution of the recursive algorithm on examples solved by hand.
        """

        computed_winning_0, computed_winning_1 = get_winning_regions(self.arena_path + "example_1/data.txt")

        self.assertEqual(len(computed_winning_0), 0)
        self.assertEqual(len(computed_winning_1), 12)

        computed_winning_0, computed_winning_1 = get_winning_regions(self.arena_path + "example_2/data.txt")

        self.assertTrue(0 in computed_winning_0)

        # The automaton asks to see b (controlled by system) while seeing a or the next step after a (env)
        computed_winning_0, computed_winning_1 = get_winning_regions(self.arena_path + "example_3/data.txt")

        self.assertEqual(len(computed_winning_0), 6)
        self.assertEqual(len(computed_winning_1), 3)
        self.assertTrue(0 in computed_winning_0)

        # Same as before but the system controls a and the environment controls b (solution : never launch a)
        computed_winning_0, computed_winning_1 = get_winning_regions(self.arena_path + "example_4/data.txt")

        self.assertEqual(len(computed_winning_0), 4)
        self.assertEqual(len(computed_winning_1), 5)
        self.assertTrue(0 in computed_winning_0)

        # The first automaton is the same as before, the second one asks to never see b (controlled by the system)
        # The environment wins : input a, if the system output b he loses, if he doesn't he loses.
        computed_winning_0, computed_winning_1 = get_winning_regions(self.arena_path + "example_5/data.txt")

        self.assertTrue(0 not in computed_winning_0)


if __name__ == '__main__':
    unittest.main()
