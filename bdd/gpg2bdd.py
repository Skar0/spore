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

from collections import defaultdict
import bdd.arena as ar


def gpg2bdd(gpg_path, manager):
    """
    Loads a generalized parity game from file and represent it as a Binary Decision Diagram (BDD).
    :param gpg_path: path to the .gpg file containing a generalized parity game in extended PGSolver format
    :type gpg_path: str
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: an arena object for the arena provided in the file and a list of its vertices represented by BDDs
    :rtype: Arena, list of dd.cudd.Function
    """

    # open file
    with open(gpg_path, "r") as gpg_file:

        # first line has max index for vertices and number of priority functions; vertices and function index start at 0
        info_line = gpg_file.readline().rstrip().split(" ")

        max_index = int(info_line[1])

        nbr_functions = int(info_line[2][:-1])

        nbr_digits_vertices = len(bin(max_index)) - 2  # binary representation is prefixed by '0b'

        # init BDD variables
        vars = ['x{i}'.format(i=j) for j in range(nbr_digits_vertices)]  # variables to encode the vertices
        vars_bis = ['xb{i}'.format(i=j) for j in range(nbr_digits_vertices)]
        all_vars = vars + vars_bis
        manager.declare(*all_vars)
        mapping_bis = dict(zip(vars, vars_bis))
        inv_mapping_bis = dict(zip(vars_bis, vars))

        # init the BDDs
        player0_vertices = manager.false  # BDD for vertices of Player 0
        player1_vertices = manager.false  # BDD for vertices of Player 1
        edges = manager.false  # BDD for edges
        # dictionary with BDD as key created on call (to avoid creating a BDD for non-existing priorities)
        priorities = [defaultdict(lambda: manager.false) for _ in range(nbr_functions)]  # function indexing starts at 0
        all_vertices = [None for _ in range(max_index + 1)]

        # all possible variables assignments of var (not yielded in order)
        all_possibilities = manager.pick_iter(manager.true, vars)

        # iterate over vertices in the file
        for line in gpg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            prios = [int(p) for p in infos[1].split(",")]
            player = int(infos[2])

            # current BDD for the vertex
            vertex_dict = next(all_possibilities)  # dictionary encoding the valuation corresponding to the vertex
            vertex_bdd = manager.cube(vertex_dict)  # create a BDD node for this valuation

            # add current node to all nodes at the correct index
            all_vertices[index] = vertex_bdd

            # add vertex to the formula for correct priority and correct function
            for func in range(nbr_functions):
                priorities[func][prios[func]] = priorities[func][prios[func]] | vertex_bdd

            # add vertex to correct player vertex BDD, 0 evaluates as false and 1 as true
            if player:
                player1_vertices = player1_vertices | vertex_bdd
            else:
                player0_vertices = player0_vertices | vertex_bdd

        gpg_file.seek(0)  # go back to first line of the file
        gpg_file.readline()  # first line has special info, pass it

        for line in gpg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])

            for succ in infos[3].split(","):
                successor = int(succ)
                edges = edges | (all_vertices[index] & manager.let(mapping_bis, all_vertices[successor]))

        # create an Arena object and fill it in
        arena = ar.Arena()
        arena.vars = vars
        arena.vars_bis = vars_bis
        arena.all_vars = all_vars
        arena.mapping_bis = mapping_bis
        arena.inv_mapping_bis = inv_mapping_bis

        arena.nbr_vertices = max_index + 1
        arena.nbr_digits_vertices = nbr_digits_vertices
        arena.nbr_functions = nbr_functions

        arena.player0_vertices = player0_vertices
        arena.player1_vertices = player1_vertices
        arena.edges = edges
        arena.priorities = priorities

        return arena, all_vertices
