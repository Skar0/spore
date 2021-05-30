from bdd.attractor import attractor_cudd
from collections import defaultdict

from bdd.generalizedBuchiSolver import buchi_solver_gen, buchi_solver_gen_inverted_players


def complement_priorities(arena, manager):
    """
    Complement the priorities in the provided arena. That is, add 1 to each priority. Also record the maximal priority
    occurring in the arena and make sure that it is odd (adding +1 to actual maximum if it is not the case).
    :param arena: a game arena
    :type arena: Arena
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the maximal priorities occurring in the complemented arena
    :rtype: list of int
    """

    max_priorities = [-1] * arena.nbr_functions

    # TODO should we maintain existing colors somewhere ? Check if this function is a bottleneck
    for function_index in range(arena.nbr_functions):

        # new dictionary to hold the new keys for the priorities
        new_dict = defaultdict(lambda: manager.false)

        for priority, bdd in arena.priorities[function_index].items():

            if (priority + 1) > max_priorities[function_index]:
                max_priorities[function_index] = (priority + 1)

            new_dict[priority + 1] = bdd

        arena.priorities[function_index] = new_dict

        # if maximum priority is even, add 1
        if not max_priorities[function_index] % 2:
            max_priorities[function_index] += 1

    return max_priorities


def generalized_recursive(arena, manager):
    """
    Solve the generalized parity game provided in arena using the recursive algorithm.
    :param arena: a game arena
    :type arena: Arena
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: (dd.cudd.Function, dd.cudd.Function)
    """

    max_priorities = complement_priorities(arena, manager)

    return disj_par_win(arena, max_priorities, manager)


def disj_par_win(arena, max_priorities, manager):
    """
    Procedure to solve the generalized parity game provided in arena using the recursive algorithm.
    :param arena: a game arena
    :type arena: Arena
    :param max_priorities: the maximal priorities occurring in the arena
    :type max_priorities: list of int
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: (dd.cudd.Function, dd.cudd.Function)
    """

    # TODO probably should record all vertices somewhere to avoid doing the | a lot between player0 and player1 vertices
    if all(value == 1 for value in max_priorities) or \
            (arena.player0_vertices | arena.player1_vertices) == manager.false:
        return arena.player0_vertices | arena.player1_vertices, manager.false

    for function_index in range(arena.nbr_functions):

        if max_priorities[function_index] != 1:

            a0 = attractor_cudd(arena,
                                arena.priorities[function_index][max_priorities[function_index]],
                                0,
                                manager)

            g_bar = arena.subarena(~a0, manager)

            a1 = attractor_cudd(g_bar,
                                g_bar.priorities[function_index][max_priorities[function_index] - 1],
                                1,
                                manager)

            h = g_bar.subarena(~a1, manager)

            while True:
                copy_max_priorities = max_priorities[:]  # faster copy
                copy_max_priorities[function_index] -= 2

                w0, w1 = disj_par_win(h, copy_max_priorities, manager)

                if g_bar.player0_vertices | g_bar.player1_vertices == manager.false \
                        or w1 == (h.player0_vertices | h.player1_vertices):
                    break

                a0 = attractor_cudd(g_bar, w0, 0, manager)
                g_bar = g_bar.subarena(~a0, manager)
                a1 = attractor_cudd(g_bar,
                                    g_bar.priorities[function_index][max_priorities[function_index] - 1],
                                    1,
                                    manager)

                h = g_bar.subarena(~a1, manager)

            q_bar = g_bar.player0_vertices | g_bar.player1_vertices

            if w1 == (h.player0_vertices | h.player1_vertices) and not q_bar == manager.false:
                a1 = attractor_cudd(arena,
                                    q_bar,
                                    1,
                                    manager)
                w0_bis, w1_bis = disj_par_win(arena.subarena(~a1, manager), max_priorities, manager)

                return w0_bis, a1 | w1_bis

    return arena.player0_vertices | arena.player1_vertices, manager.false


def generalized_recursive_with_psolver(arena, manager):
    """
    Solve the generalized parity game provided in arena using a combination of a provided partial solver and the
    recursive algorithm.
    :param arena: a game arena
    :type arena: Arena
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: (dd.cudd.Function, dd.cudd.Function)
    """

    partial_winning_region_player0, partial_winning_region_player1 = buchi_solver_gen(arena, manager)

    remaining_unsolved = arena.subarena(~(partial_winning_region_player0 | partial_winning_region_player1), manager)

    if (remaining_unsolved.player0_vertices | remaining_unsolved.player1_vertices) == manager.false:
        return partial_winning_region_player0, partial_winning_region_player1

    max_priorities = complement_priorities(remaining_unsolved, manager)

    winning_region_player0, winning_region_player1 = disj_par_win(remaining_unsolved, max_priorities, manager)

    return winning_region_player0 | partial_winning_region_player0, winning_region_player1 | partial_winning_region_player1


def generalized_recursive_with_psolver_multiple_calls(arena, manager):
    """
    Solve the generalized parity game provided in arena using a combination of a provided partial solver and the
    recursive algorithm.
    :param arena: a game arena
    :type arena: Arena
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: (dd.cudd.Function, dd.cudd.Function)
    """

    """
    partial_winning_region_player0, partial_winning_region_player1 = buchi_solver_gen(arena, manager)

    remaining_unsolved = arena.subarena(~(partial_winning_region_player0 | partial_winning_region_player1), manager)

    if (remaining_unsolved.player0_vertices | remaining_unsolved.player1_vertices) == manager.false:
        return partial_winning_region_player0, partial_winning_region_player1
    """

    max_priorities = complement_priorities(arena, manager)

    winning_region_player0, winning_region_player1 = disj_par_win_multiple_calls(arena, max_priorities, manager)

    return winning_region_player0, winning_region_player1


def disj_par_win_multiple_calls(arena, max_priorities, manager):
    """
    Procedure to solve the generalized parity game provided in arena using the recursive algorithm.
    :param arena: a game arena
    :type arena: Arena
    :param max_priorities: the maximal priorities occurring in the arena
    :type max_priorities: list of int
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: (dd.cudd.Function, dd.cudd.Function)
    """

    # TODO probably should record all vertices somewhere to avoid doing the | a lot between player0 and player1 vertices
    if all(value == 1 for value in max_priorities) or \
            (arena.player0_vertices | arena.player1_vertices) == manager.false:
        return arena.player0_vertices | arena.player1_vertices, manager.false

    partial_winning_region_player0, partial_winning_region_player1 = buchi_solver_gen_inverted_players(arena, manager)

    remaining_unsolved = arena.subarena(~(partial_winning_region_player0 | partial_winning_region_player1), manager)

    if (remaining_unsolved.player0_vertices | remaining_unsolved.player1_vertices) == manager.false:
        return partial_winning_region_player0, partial_winning_region_player1


    for function_index in range(remaining_unsolved.nbr_functions):

        if max_priorities[function_index] != 1:

            a0 = attractor_cudd(remaining_unsolved,
                                remaining_unsolved.priorities[function_index][max_priorities[function_index]],
                                0,
                                manager)

            g_bar = remaining_unsolved.subarena(~a0, manager)

            a1 = attractor_cudd(g_bar,
                                g_bar.priorities[function_index][max_priorities[function_index] - 1],
                                1,
                                manager)

            h = g_bar.subarena(~a1, manager)

            while True:
                copy_max_priorities = max_priorities[:]  # faster copy
                copy_max_priorities[function_index] -= 2

                w0, w1 = disj_par_win_multiple_calls(h, copy_max_priorities, manager)

                if g_bar.player0_vertices | g_bar.player1_vertices == manager.false \
                        or w1 == (h.player0_vertices | h.player1_vertices):
                    break

                a0 = attractor_cudd(g_bar, w0, 0, manager)
                g_bar = g_bar.subarena(~a0, manager)
                a1 = attractor_cudd(g_bar,
                                    g_bar.priorities[function_index][max_priorities[function_index] - 1],
                                    1,
                                    manager)

                h = g_bar.subarena(~a1, manager)

            q_bar = g_bar.player0_vertices | g_bar.player1_vertices

            if w1 == (h.player0_vertices | h.player1_vertices) and not q_bar == manager.false:
                a1 = attractor_cudd(remaining_unsolved,
                                    q_bar,
                                    1,
                                    manager)
                w0_bis, w1_bis = disj_par_win_multiple_calls(remaining_unsolved.subarena(~a1, manager), max_priorities, manager)

                return w0_bis | partial_winning_region_player0, a1 | w1_bis | partial_winning_region_player1

    return remaining_unsolved.player0_vertices | remaining_unsolved.player1_vertices | partial_winning_region_player0, partial_winning_region_player1
