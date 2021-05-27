from collections import defaultdict
from regular.attractor import attractor
from regular.generalizedBuchiSolver import generalized_buchi_partial_solver, \
    generalized_buchi_partial_solver_inverted_players


def transform_game(arena):
    """
    Complement the priorities in the provided arena. That is, add 1 to each priority. Also record the maximal priority
    occurring in the arena and make sure that it is odd (adding +1 to actual maximum if it is not the case). The arena
    provided in parameter is modified.
    :param arena: a game arena
    :type arena: Arena
    :return: the maximal priorities occurring in the complemented arena
    :rtype: list of int
    """

    max_priorities = [-1] * arena.nbr_functions

    for function_index in range(arena.nbr_functions):

        # new dictionary to hold the new keys for the priorities
        new_dict = defaultdict(lambda: [])

        for priority, vertices in arena.priorities[function_index].items():

            if (priority + 1) > max_priorities[function_index]:
                max_priorities[function_index] = (priority + 1)

            new_dict[priority + 1] = vertices

        arena.priorities[function_index] = new_dict

        # if maximum priority is even, add 1
        if not max_priorities[function_index] % 2:
            max_priorities[function_index] += 1

    # also update the vertex priorities
    for vertex in arena.vertices:
        arena.vertex_priorities[vertex] = [x + 1 for x in arena.vertex_priorities[vertex]]

    return max_priorities


def generalized_recursive(arena):
    """
    Solve the generalized parity game provided in arena using the recursive algorithm.
    :param arena: a game arena
    :type arena: Arena
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: list of int, list of int
    """

    max_priorities = transform_game(arena)

    return disj_parity_win(arena, max_priorities)


def disj_parity_win(arena, max_priorities):
    """
    Procedure to solve the generalized parity game provided in arena using the recursive algorithm.
    :param arena: a game arena
    :type arena: Arena
    :param max_priorities: the maximal priorities occurring in the arena
    :type max_priorities: list of int
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: list of int, list of int
    """

    # For the correctness argument to work, and for the base case too,
    # we need the max value of each priority to be odd!
    # assert(all(m % 2 == 1 for m in max_priorities))

    # Base case : all maxValues are 1 or the game is empty
    if all(value == 1 for value in max_priorities) or arena.nbr_vertices == 0:
        return arena.vertices, []

    for func_index in range(arena.nbr_functions):

        # We only consider priority functions according to which every value is not 1
        if max_priorities[func_index] != 1:

            attMaxOdd = attractor(arena, arena.priorities[func_index][max_priorities[func_index]], 0)
            G1 = arena.subarena(attMaxOdd)

            attMaxEven = attractor(G1, G1.priorities[func_index][max_priorities[func_index] - 1], 1)
            H1 = G1.subarena(attMaxEven)

            while True:
                copy_max_priorities = max_priorities[:]
                copy_max_priorities[func_index] -= 2
                # sanity check: on recursive calls we have less priorities
                # It should not be the case that negative max priorities occur as we only consider functions
                # in which the max odd value is > 1. Negative values happened when we considered the following
                # instruction when maxValue is 1.
                # assert(copy_max_priorities[func_index] >= 0)
                # assert(copy_max_priorities[func_index] == max_priorities[func_index] - 2)
                # end of sanity check
                W1, W2 = disj_parity_win(H1, copy_max_priorities)
                # sanity check: if all priorities were odd, then W1 union G1.V should be g.V
                # print(set(G1.vertices).union(set(W1)))
                # print(set(arena.vertices))
                # print(any(arena.vertices_priorities[n][func_index] % 2 == 0
                #              for n in arena.vertices))
                # assert(set(G1.vertices).union(set(W1)) != set(arena.vertices)
                #       or any(arena.vertices_priorities[n][func_index] % 2 == 0
                #              for n in arena.vertices))

                if G1.nbr_vertices == 0 or set(W2) == set(H1.vertices):
                    break

                T = attractor(G1, W1, 0)
                G1 = G1.subarena(T)
                E = attractor(G1, G1.priorities[func_index][max_priorities[func_index] - 1], 1)
                H1 = G1.subarena(E)
                # assert(len(H1.get_nodes()) < h1_old_len)

            # checks after the end of the loop (base cases, essentially)
            if set(W2) == set(H1.vertices) and G1.nbr_vertices > 0:
                assert (G1.nbr_vertices > 0)  # otherwise this makes no sense!
                B = attractor(arena, G1.vertices, 1)
                # sanity check: we always do a recursive call on a smaller game
                # and so necessarily B is non-empty
                assert (len(B) > 0)
                # end of sanity check
                W1, W2 = disj_parity_win(arena.subarena(B), max_priorities)
                B.extend(W2)
                return W1, B

    return arena.vertices, []


def generalized_recursive_with_buchi(arena):
    """
    Solve the generalized parity game provided in arena using a combination of the recursive algorithm and the partial
    solver called buchi solver.
    :param arena: a game arena
    :type arena: Arena
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: list of int, list of int
    """

    remaining_arena, partial_winning_region_player0, partial_winning_region_player1 = \
        generalized_buchi_partial_solver(arena, [], [])  # call to the partial solver

    if remaining_arena.nbr_vertices == 0:
        return partial_winning_region_player0, partial_winning_region_player1

    max_priorities = transform_game(remaining_arena)

    winning_region_player0, winning_region_player1 = disj_parity_win(remaining_arena, max_priorities)

    winning_region_player0.extend(partial_winning_region_player0)
    winning_region_player1.extend(partial_winning_region_player1)

    return winning_region_player0, winning_region_player1


def generalized_recursive_with_buchi_multiple_calls(arena):
    """
    Solve the generalized parity game provided in arena using a combination of the recursive algorithm and the partial
    solver called buchi solver. This version uses a call to the partial solver in each recursive call to the algorithm.
    :param arena: a game arena
    :type arena: Arena
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: list of int, list of int
    """

    max_priorities = transform_game(arena)

    winning_region_player0, winning_region_player1 = disj_parity_win_multiple_calls(arena, max_priorities)

    return winning_region_player0, winning_region_player1


def disj_parity_win_multiple_calls(arena, max_priorities):
    """
    Procedure to solve the generalized parity game provided in arena using the recursive algorithm. This version
    performs a call to the partial solver in each recursive call. The input is a complemented arena and the partial
    solver is adapted to this
    :param arena: a game arena
    :type arena: Arena
    :param max_priorities: the maximal priorities occurring in the arena
    :type max_priorities: list of int
    :return: the solution of the provided generalized parity game, that is the set of vertices won by each player
    :rtype: list of int, list of int
    """

    # For the correctness argument to work, and for the base case too,
    # we need the max value of each priority to be odd!
    # assert(all(m % 2 == 1 for m in max_priorities))

    # Base case : all maxValues are 1 or the game is empty
    if all(value == 1 for value in max_priorities) or arena.nbr_vertices == 0:
        return arena.vertices, []

    remaining_arena, partial_winning_region_player0, partial_winning_region_player1 = \
        generalized_buchi_partial_solver_inverted_players(arena, [], [])  # call to the partial solver

    if remaining_arena.nbr_vertices == 0:
        return partial_winning_region_player0, partial_winning_region_player1

    # update the max priorities in the remaining following the removal of vertices TODO check correctness
    max_priorities_remaining = [max(remaining_arena.priorities[func].keys()) for func in range(remaining_arena.nbr_functions)]

    for func in range(remaining_arena.nbr_functions):
        if not max_priorities_remaining[func] % 2:
            max_priorities_remaining[func] += 1

    for func_index in range(remaining_arena.nbr_functions):

        # We only consider priority functions according to which every value is not 1
        if max_priorities_remaining[func_index] != 1:

            attMaxOdd = attractor(remaining_arena, remaining_arena.priorities[func_index][max_priorities_remaining[func_index]], 0)
            G1 = remaining_arena.subarena(attMaxOdd)

            attMaxEven = attractor(G1, G1.priorities[func_index][max_priorities_remaining[func_index] - 1], 1)
            H1 = G1.subarena(attMaxEven)

            while True:
                copy_max_priorities = max_priorities_remaining[:]
                copy_max_priorities[func_index] -= 2
                # sanity check: on recursive calls we have less priorities
                # It should not be the case that negative max priorities occur as we only consider functions
                # in which the max odd value is > 1. Negative values happened when we considered the following
                # instruction when maxValue is 1.
                # assert(copy_max_priorities[func_index] >= 0)
                # assert(copy_max_priorities[func_index] == max_priorities[func_index] - 2)
                # end of sanity check
                W1, W2 = disj_parity_win_multiple_calls(H1, copy_max_priorities)
                # sanity check: if all priorities were odd, then W1 union G1.V should be g.V
                # print(set(G1.vertices).union(set(W1)))
                # print(set(arena.vertices))
                # print(any(arena.vertices_priorities[n][func_index] % 2 == 0
                #              for n in arena.vertices))
                # assert(set(G1.vertices).union(set(W1)) != set(arena.vertices)
                #       or any(arena.vertices_priorities[n][func_index] % 2 == 0
                #              for n in arena.vertices))

                if G1.nbr_vertices == 0 or set(W2) == set(H1.vertices):
                    break

                T = attractor(G1, W1, 0)
                G1 = G1.subarena(T)
                E = attractor(G1, G1.priorities[func_index][max_priorities_remaining[func_index] - 1], 1)
                H1 = G1.subarena(E)
                # assert(len(H1.get_nodes()) < h1_old_len)

            # checks after the end of the loop (base cases, essentially)
            if set(W2) == set(H1.vertices) and G1.nbr_vertices > 0:
                assert (G1.nbr_vertices > 0)  # otherwise this makes no sense!
                B = attractor(remaining_arena, G1.vertices, 1)
                # sanity check: we always do a recursive call on a smaller game
                # and so necessarily B is non-empty
                assert (len(B) > 0)
                # end of sanity check
                W1, W2 = disj_parity_win_multiple_calls(remaining_arena.subarena(B), max_priorities_remaining)
                B.extend(W2)

                W1.extend(partial_winning_region_player0)
                B.extend((partial_winning_region_player1))
                return W1, B

    partial_winning_region_player0.extend(remaining_arena.vertices)

    return partial_winning_region_player0, partial_winning_region_player1
