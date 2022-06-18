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
import sys
from functools import reduce

import dd.cudd as _bdd

import bdd.recursive
import bdd.pg2bdd

import regular.recursive
import regular.pg2arena

import bdd.generalizedRecursive
import bdd.gpg2bdd as bdd_gen_loader

import regular.generalizedRecursive
import regular.gpg2arena as reg_gen_loader

from bdd.bdd_util import decomp_data_file, x, xb
from bdd.dpa2bdd import explicit2symbolic_path
from bdd.dpa2gpg import symb_dpa2gpg

# Increase the recursion limit to avoid error when we read a long label with explicit2symbolic_path
sys.setrecursionlimit(50000)

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

    solver_group.add_argument('-snl',
                              action='store_true',
                              help='Perform a single call to the partial solver '
                                   'and solve the remaining arena using the recursive algorithm.')

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

    bdd_group.add_argument('-fbdd',
                           action='store_true',
                           help='Use the symbolic implementation of the algorithms, '
                                'using Binary Decision Diagrams, and in addition, '
                                'use a symbolic implementation of automata.')

    reordering_group = parser.add_mutually_exclusive_group(required=False)

    reordering_group.add_argument('-dynord', '--dynamic_ordering',
                        action='store_true',
                        help='With -fbdd only, use the dynamic ordering available in dd with CUDD as backend.')

    reordering_group.add_argument('-arbord', '--arbitrary_ordering',
                        action='store_true',
                        help='With -fbdd only, enable an arbitrary ordering of the BDD just'
                             'before the computation of the product autamaton :'
                             '(1) state variables, (2) Atomic porpositions, (3) state variable bis.')

    parser.add_argument('-rstredge', '--restrict_reach_edges',
                        action='store_true',
                        help='With -fbdd only, enable the restriction of edges to reachable'
                             'vertices, incoming and outgoing, when the symbolic arena is built.')

    parser.add_argument('input_path', type=str, help='The path to the file containing the game in '
                                                     '(extended) PGSolver format or the path to the file containing'
                                                     'the path to the automatas for -fbdd.')

    args = parser.parse_args()

    # Checking if some options of -fbdd are used without -fbdd

    if (args.dynord or args.arbord or args.rstredge) and not args.fbdd:
        parser.error("-dynord, -arbord and -rstredge require -fbdd.")

    if args.pg:

        if args.reg:

            arena = regular.pg2arena.pg2arena(args.input_path, is_gpg=False)

            if args.rec:
                winning_region_player0, winning_region_player1 = \
                    regular.recursive.recursive(arena)

            elif args.snl:
                winning_region_player0, winning_region_player1 = \
                    regular.recursive.recursive_single_call(arena)

            else:
                winning_region_player0, winning_region_player1 = \
                    regular.recursive.recursive_with_buchi(arena)

            vertex_0_won_by_player0 = 0 in winning_region_player0

            if vertex_0_won_by_player0:
                print("REALIZABLE")
            else:
                print("UNREALIZABLE")

        else:  # if args.bdd or default

            manager = _bdd.BDD()
            arena, all_vertices = bdd.pg2bdd.pg2bdd(args.input_path, manager, is_gpg=False)

            if args.rec:
                winning_region_player0, winning_region_player1 = \
                    bdd.recursive.recursive(arena, manager)

            elif args.snl:
                winning_region_player0, winning_region_player1 = \
                    bdd.recursive.recursive_single_call(arena, manager)

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

            elif args.snl:
                winning_region_player0, winning_region_player1 = \
                    regular.generalizedRecursive.generalized_recursive_with_buchi(arena)

            else:
                winning_region_player0, winning_region_player1 = \
                    regular.generalizedRecursive.generalized_recursive_with_buchi_multiple_calls(arena)

            vertex_0_won_by_player0 = 0 in winning_region_player0

            if vertex_0_won_by_player0:
                print("REALIZABLE")
            else:
                print("UNREALIZABLE")

        elif args.fbdd:

            manager = _bdd.BDD()
            manager.configure(reordering=args.dynamic_ordering)

            input_signals, output_signals, automata_paths = decomp_data_file(args.input_path)

            manager.declare(*input_signals)
            manager.declare(*output_signals)

            automata = [explicit2symbolic_path(path, manager) for path in automata_paths]

            if args.arbitrary_ordering:
                nb_total_var = sum(map(lambda a: len(a.vars), automata))
                new_order = dict()
                i = 0
                for var in input_signals + output_signals:
                    new_order[var] = i
                    i += 1
                for var in range(nb_total_var):
                    manager.declare(x(var))
                    new_order[x(var)] = i
                    i += 1
                for var in range(nb_total_var):
                    manager.declare(xb(var))
                    new_order[xb(var)] = i
                    i += 1
                _bdd.reorder(manager, new_order)

            product = reduce(lambda a1, a2: a1.product(a2, manager), automata)

            arena, init = symb_dpa2gpg(product, input_signals, output_signals,
                                       manager, restrict_reach_edges=args.restrict_reach_edges)

            if args.rec:
                winning_region_player0, winning_region_player1 = \
                    bdd.generalizedRecursive.generalized_recursive(arena, manager)

            elif args.snl:
                winning_region_player0, winning_region_player1 = \
                    bdd.generalizedRecursive.generalized_recursive_with_psolver(arena, manager)

            else:
                winning_region_player0, winning_region_player1 = \
                    bdd.generalizedRecursive.generalized_recursive_with_psolver_multiple_calls(arena, manager)

            vertex_0_dict_rep = next(manager.pick_iter(init))
            vertex_0_won_by_player0 = manager.let(vertex_0_dict_rep, winning_region_player0) == manager.true

            if vertex_0_won_by_player0:
                print("REALIZABLE")
            else:
                print("UNREALIZABLE")

        else:  # if args.bdd or default

            manager = _bdd.BDD()
            arena, all_vertices = bdd_gen_loader.gpg2bdd(args.input_path, manager)

            if args.rec:
                winning_region_player0, winning_region_player1 = \
                    bdd.generalizedRecursive.generalized_recursive(arena, manager)

            elif args.snl:
                winning_region_player0, winning_region_player1 = \
                    bdd.generalizedRecursive.generalized_recursive_with_psolver(arena, manager)

            else:
                winning_region_player0, winning_region_player1 = \
                    bdd.generalizedRecursive.generalized_recursive_with_psolver_multiple_calls(arena, manager)

            vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
            vertex_0_won_by_player0 = manager.let(vertex_0_dict_rep, winning_region_player0) == manager.true

            if vertex_0_won_by_player0:
                print("REALIZABLE")
            else:
                print("UNREALIZABLE")
