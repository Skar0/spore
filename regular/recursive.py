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

from regular.attractor import attractor
from regular.buchiSolver import buchi_partial_solver


def recursive(arena):
    """
    Solve the parity game provided in arena using the recursive algorithm.
    :param arena: a game arena
    :type arena: Arena
    :return: the solution of the provided parity game, that is the set of vertices won by each player
    :rtype: list of int, list of int
    """

    winning_region_player0 = []  # winning region of player 0
    winning_region_player1 = []  # winning region of player 1

    # if the game is empty, return the empty regions
    if arena.nbr_vertices == 0:
        return winning_region_player0, winning_region_player1

    else:
        max_occurring_priority = max(arena.priorities[0].keys())  # get max priority occurring in g

        # determining which player we are considering, if max_occurring_priority is odd : player 1 and else player 0
        j = max_occurring_priority % 2

        opponent = 0 if j else 1  # getting the opponent of the player

        # vertices with priority max_occurring_priority
        U = arena.priorities[0][max_occurring_priority]

        # getting the attractor A
        A = attractor(arena, U, j)

        # The subgame G\A is composed of the vertices not in the attractor
        G_A = arena.subarena(A)

        # Recursively solving the subgame G\A
        winning_region_player0_G_A, winning_region_player1_G_A = recursive(G_A)

        # depending on which player we are considering, assign regions to the proper variables
        # if we consider player1
        if j:
            winning_region_player = winning_region_player1_G_A
            winning_region_opponent = winning_region_player0_G_A
        else:
            winning_region_player = winning_region_player0_G_A
            winning_region_opponent = winning_region_player1_G_A

        # if winning_region_opponent is empty we update the regions depending on the current player
        # the region for the whole game for one of the players is empty
        if not winning_region_opponent:

            # if we consider player1
            if j:
                winning_region_player1.extend(A)
                winning_region_player1.extend(winning_region_player)
            else:
                winning_region_player0.extend(A)
                winning_region_player0.extend(winning_region_player)

        else:
            # compute attractor B
            B = attractor(arena, winning_region_opponent, opponent)

            # The subgame G\B is composed of the vertices not in the attractor
            G_B = arena.subarena(B)

            # recursively solve subgame G\B
            winning_region_player0_G_B, winning_region_player1_G_B = recursive(G_B)

            # depending on which player we are considering, assign regions to the proper variables
            # if we consider player1
            if j:
                winning_region_player_bis = winning_region_player1_G_B
                winning_region_opponent_bis = winning_region_player0_G_B
            else:
                winning_region_player_bis = winning_region_player0_G_B
                winning_region_opponent_bis = winning_region_player1_G_B

            # the last step is to update the winning regions depending on which player we consider
            # if we consider player1
            if j:
                winning_region_player1 = winning_region_player_bis

                winning_region_player0.extend(winning_region_opponent_bis)
                winning_region_player0.extend(B)
            else:
                winning_region_player0 = winning_region_player_bis

                winning_region_player1.extend(winning_region_opponent_bis)
                winning_region_player1.extend(B)

    return winning_region_player0, winning_region_player1


def recursive_with_buchi(arena):
    """
    Solve the parity game provided in arena using a combinations of the recursive algorithm and the partial solver
    called buchi solver.
    :param arena: a game arena
    :type arena: Arena
    :return: the solution of the provided parity game, that is the set of vertices won by each player
    :rtype: list of int, list of int
    """

    winning_region_player0 = []  # winning region of player 0
    winning_region_player1 = []  # winning region of player 1

    # if the game is empty, return the empty regions
    if arena.nbr_vertices == 0:
        return winning_region_player0, winning_region_player1

    remaining_arena, partial_winning_region_player0, partial_winning_region_player1 = buchi_partial_solver(arena,
                                                                                                           [],
                                                                                                           [])

    # if the remaining game is empty, return the partial regions
    if remaining_arena.nbr_vertices == 0:
        return partial_winning_region_player0, partial_winning_region_player1

    else:
        max_occurring_priority = max(remaining_arena.priorities[0].keys())  # get max priority occurring in g

        # determining which player we are considering, if max_occurring_priority is odd : player 1 and else player 0
        j = max_occurring_priority % 2

        opponent = 0 if j else 1  # getting the opponent of the player

        # vertices with priority max_occurring_priority
        U = remaining_arena.priorities[0][max_occurring_priority]

        # getting the attractor A
        A = attractor(remaining_arena, U, j)

        # The subgame G\A is composed of the vertices not in the attractor
        G_A = remaining_arena.subarena(A)

        # Recursively solving the subgame G\A
        winning_region_player0_G_A, winning_region_player1_G_A = recursive_with_buchi(G_A)

        # depending on which player we are considering, assign regions to the proper variables
        # if we consider player1
        if j:
            winning_region_player = winning_region_player1_G_A
            winning_region_opponent = winning_region_player0_G_A
        else:
            winning_region_player = winning_region_player0_G_A
            winning_region_opponent = winning_region_player1_G_A

        # if winning_region_opponent is empty we update the regions depending on the current player
        # the region for the whole game for one of the players is empty
        if not winning_region_opponent:

            # if we consider player1
            if j:
                winning_region_player1.extend(A)
                winning_region_player1.extend(winning_region_player)
            else:
                winning_region_player0.extend(A)
                winning_region_player0.extend(winning_region_player)

        else:
            # compute attractor B
            B = attractor(remaining_arena, winning_region_opponent, opponent)

            # The subgame G\B is composed of the vertices not in the attractor
            G_B = remaining_arena.subarena(B)

            # recursively solve subgame G\B
            winning_region_player0_G_B, winning_region_player1_G_B = recursive_with_buchi(G_B)

            # depending on which player we are considering, assign regions to the proper variables
            # if we consider player1
            if j:
                winning_region_player_bis = winning_region_player1_G_B
                winning_region_opponent_bis = winning_region_player0_G_B
            else:
                winning_region_player_bis = winning_region_player0_G_B
                winning_region_opponent_bis = winning_region_player1_G_B

            # the last step is to update the winning regions depending on which player we consider
            # if we consider player1
            if j:
                winning_region_player1 = winning_region_player_bis

                winning_region_player0.extend(winning_region_opponent_bis)
                winning_region_player0.extend(B)
            else:
                winning_region_player0 = winning_region_player_bis

                winning_region_player1.extend(winning_region_opponent_bis)
                winning_region_player1.extend(B)

    # add the partial solutions to the winning regions
    winning_region_player0.extend(partial_winning_region_player0)
    winning_region_player1.extend(partial_winning_region_player1)

    return winning_region_player0, winning_region_player1
