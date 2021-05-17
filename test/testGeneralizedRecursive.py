import unittest
import generalizedRecursive
import gpg2bdd
import tools
import dd.cudd as bdd


class testGeneralizedRecursive(unittest.TestCase):
    """
    Test cases for the recursive algorithm used to solve generalized parity games.
    """

    def test_recursive_generalized_solved_examples(self):
        """
        Checks the solution of the recursive algorithm on examples solved by hand.
        """

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_1_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 3, 5})
        self.assertEqual(set(computed_winning_1), {2, 4})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_2_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2})
        self.assertEqual(set(computed_winning_1), set())

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_3_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2, 3})
        self.assertEqual(set(computed_winning_1), set())

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_4_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2, 3})
        self.assertEqual(set(computed_winning_1), {4, 5, 6})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_5_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 4})
        self.assertEqual(set(computed_winning_1), {2, 3, 5})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_1.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), set())
        self.assertEqual(set(computed_winning_1), {0, 1, 2})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_2.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2})
        self.assertEqual(set(computed_winning_1), set())

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_3.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1})
        self.assertEqual(set(computed_winning_1), {2, 3, 4})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd.gpg2bdd("arenas/gpg/example_4.gpg", manager)
        computed_winning_0, computed_winning_1 = generalizedRecursive.generalized_recursive(arena, manager)

        computed_winning_0 = tools.bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = tools.bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2, 4, 5})
        self.assertEqual(set(computed_winning_1), {3})


if __name__ == '__main__':
    unittest.main()
