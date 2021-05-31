# -*- coding: utf-8 -*-
# SPORE: Symbolic Partial sOlvers for REalizability. 
# Copyright (C) 2021 - Charly Delfosse (University of Mons), Gaëtan Staquet (University of Mons), Clément Tamines (University of Mons)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
import dd.cudd as bdd

from bdd.generalizedRecursive import generalized_recursive
from bdd.gpg2bdd import gpg2bdd
from bdd.misc import bdd2int


class testGeneralizedRecursive(unittest.TestCase):
    """
    Test cases for the recursive algorithm used to solve generalized parity games.
    """

    def setUp(self):
        self.arena_path = "./"

    def test_recursive_generalized_solved_examples(self):
        """
        Checks the solution of the recursive algorithm on examples solved by hand.
        """

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_1_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 3, 5})
        self.assertEqual(set(computed_winning_1), {2, 4})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_2_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2})
        self.assertEqual(set(computed_winning_1), set())

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_3_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2, 3})
        self.assertEqual(set(computed_winning_1), set())

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_4_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2, 3})
        self.assertEqual(set(computed_winning_1), {4, 5, 6})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_5_pg.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 4})
        self.assertEqual(set(computed_winning_1), {2, 3, 5})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_1.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), set())
        self.assertEqual(set(computed_winning_1), {0, 1, 2})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_2.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2})
        self.assertEqual(set(computed_winning_1), set())

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_3.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1})
        self.assertEqual(set(computed_winning_1), {2, 3, 4})

        manager = bdd.BDD()
        arena, vertices_bdd = gpg2bdd(self.arena_path + "arenas/gpg/example_4.gpg", manager)
        computed_winning_0, computed_winning_1 = generalized_recursive(arena, manager)

        computed_winning_0 = bdd2int(computed_winning_0, arena.vars, manager, mapping=vertices_bdd)
        computed_winning_1 = bdd2int(computed_winning_1, arena.vars, manager, mapping=vertices_bdd)
        self.assertEqual(set(computed_winning_0), {0, 1, 2, 4, 5})
        self.assertEqual(set(computed_winning_1), {3})


if __name__ == '__main__':
    unittest.main()
