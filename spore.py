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

import argparse

import dd.cudd as _bdd

import bdd.recursive
import bdd.pg2bdd

import regular.recursive
import regular.pg2arena

import bdd.generalizedRecursive
import bdd.gpg2bdd as bdd_gen_loader

import regular.generalizedRecursive
import regular.gpg2arena as reg_gen_loader

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='SPORE: Symbolic Partial sOlvers for REalizability.')

    type_group = parser.add_mutually_exclusive_group(required=True)

    type_group.add_argument('-pg',
                            action='store_true',
                            help='Load a parity game in PGSolver format.')

    type_group.add_argument('-gpg',
                            action='store_true',
                            help='Load a generalized parity game in extended PGSolver format.')

    solver_group = parser.add_mutually_exclusive_group(required=False)

    solver_group.add_argument('-par',
                            action='store_true',
                            help='Use the combination of the recursive algorithm with a partial solver (default).')

    solver_group.add_argument('-rec',
                            action='store_true',
                            help='Use the recursive algorithm.')

    bdd_group = parser.add_mutually_exclusive_group(required=False)

    bdd_group.add_argument('-bdd',
                            action='store_true',
                            help='Use the symbolic implementation of the algorithms, '
                                 'using Binary Decision Diagrams (default).')

    bdd_group.add_argument('-reg',
                            action='store_true',
                            help='Use the regular, explicit, implementation of the algorithms.')

    parser.add_argument('input_path', type=str, help='The path to the file containing the game in '
                                                     '(extended) PGSolver format')

    args = parser.parse_args()

    if args.pg:

        if args.reg:

            arena = regular.pg2arena.pg2arena(args.input_path, is_gpg=False)

            if args.rec:
                winning_region_player0, winning_region_player1 = \
                    regular.recursive.recursive(arena)

            else:
                winning_region_player0, winning_region_player1 = \
                    regular.recursive.recursive_with_buchi(arena)

            vertex_0_won_by_player0 = 0 in winning_region_player0

            if vertex_0_won_by_player0:
                print("REALIZABLE")
            else:
                print("UNREALIZABLE")

        else:

            manager = _bdd.BDD()
            arena, all_vertices = bdd.pg2bdd.pg2bdd(args.input_path, manager, is_gpg=False)

            if args.rec:
                winning_region_player0, winning_region_player1 = \
                    bdd.recursive.recursive(arena, manager)
            else:
                winning_region_player0, winning_region_player1 = \
                    bdd.recursive.recursive_with_buchi(arena, manager)

            vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
            vertex_0_won_by_player0 = manager.let(vertex_0_dict_rep, winning_region_player0) == manager.true

            if vertex_0_won_by_player0:
                print("REALIZABLE")
            else:
                print("UNREALIZABLE")

    if args.gpg:

        if args.reg:

            arena = reg_gen_loader.gpg2arena(args.input_path)

            if args.rec:
                winning_region_player0, winning_region_player1 = \
                    regular.generalizedRecursive.generalized_recursive(arena)

            else:
                winning_region_player0, winning_region_player1 = \
                    regular.generalizedRecursive.generalized_recursive_with_buchi(arena)

            vertex_0_won_by_player0 = 0 in winning_region_player0

            if vertex_0_won_by_player0:
                print("REALIZABLE")
            else:
                print("UNREALIZABLE")

        else:

            manager = _bdd.BDD()
            arena, all_vertices = bdd_gen_loader.gpg2bdd(args.input_path, manager)

            if args.rec:
                winning_region_player0, winning_region_player1 = \
                    bdd.generalizedRecursive.generalized_recursive(arena, manager)
            else:
                winning_region_player0, winning_region_player1 = \
                    bdd.generalizedRecursive.generalized_recursive_with_psolver(arena, manager)

            vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
            vertex_0_won_by_player0 = manager.let(vertex_0_dict_rep, winning_region_player0) == manager.true

            if vertex_0_won_by_player0:
                print("REALIZABLE")
            else:
                print("UNREALIZABLE")
