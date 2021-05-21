from collections import defaultdict
from regular.attractor import attractor
from regular.generalizedBuchiSolver import generalized_buchi_partial_solver


def transform_game(arena):
    """
    Complement the priorities in the provided arena. That is, add 1 to each priority. Also record the maximal priority
    occurring in the arena and make sure that it is odd (adding +1 to actual maximum if it is not the case).
    :param arena: a game arena
    :type arena: Arena
    :return: the maximal priorities occurring in the complemented arena
    :rtype: list of int
    """

    max_priorities = [-1] * arena.nbr_functions

    # TODO should we maintain existing priorities somewhere ? Check if this function is a bottleneck
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
        # TODO maps could be faster list(map(lambda x: x + 1, arena.vertex_priorities[vertex]))

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
                # print(set(arena.vertices)) TODO fix
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

    # TODO fix add partial solver in recursive calls
    winning_region_player0, winning_region_player1 = disj_parity_win(arena, max_priorities)

    winning_region_player0.extend(partial_winning_region_player0)
    winning_region_player1.extend(partial_winning_region_player1)

    return winning_region_player0, winning_region_player1

"""
def disj_parity_win_with_partial(g, maxValues, k, u, partial):
    
    Recursive solver for generalized parity games. Implements the classical algorithm which solves generalized parity
    games.
    :param g: the game to solve
    :param maxValues: the maximum value according to each priority function
    :param k: the number of priority functions
    :param u: integer for testing purposes
    :param partial: partial solver.
    :return: W1, W2 the winning regions in the game for player 1 and player 2
             (for the original game, without complement)
    

    rest, W0, W1 = partial(g, [], [])  # call to the partial solver

    if len(rest.nodes) == 0:
        return W0, W1

    # For the correctness argument to work, and for the base case too,
    # we need the max value of each priority to be odd!
    assert(all(m % 2 == 1 for m in maxValues))

    # Base case : all maxValues are 1 or the game is empty
    if all(value == 1 for value in maxValues) or len(rest.get_nodes()) == 0:
        return rest.get_nodes(), []

    # FIXME: the code below is a hacked base case, remove it when the bug is
    # fixed. Clement added this condition, which states that if there is only
    # one node left with only odd priorities, it is winning for player 1
    # (since we work with complemented priorities in this algorithm)
    # if len(g.nodes) == 1 and all(value % 2 == 1 for value in g.nodes[g.get_nodes()[0]][1:]):
    #     return g.get_nodes(), []
    for i in range(k):

        # We only consider priority functions according to which every value is not 1
        if maxValues[i] != 1:

            # if u <= 4:
            #     print("-" * u + str(i))
            attMaxOdd, compl_attMaxOdd = attractor(rest, ops.i_priority_node_function_j(rest, maxValues[i], i + 1),
                                                                0)
            G1 = rest.subgame(compl_attMaxOdd)
            attMaxEven, compl_attMaxEven = attractor(G1, ops.i_priority_node_function_j(G1, maxValues[i] - 1,
                                                                                                     i + 1), 1)
            H1 = G1.subgame(compl_attMaxEven)
            while True:
                h1_old_len = len(H1.get_nodes())
                copy_maxValues = copy.copy(maxValues)
                copy_maxValues[i] -= 2
                # sanity check: on recursive calls we have less priorities
                # It should not be the case that negative max priorities occur as we only consider functions
                # in which the max odd value is > 1. Negative values happened when we considered the following
                # instruction when maxValue is 1.
                assert(copy_maxValues[i] >= 0)
                assert(copy_maxValues[i] == maxValues[i] - 2)
                # end of sanity check
                W1, W2 = disj_parity_win_with_partial(H1, copy_maxValues, k, u + 1, partial)
                # sanity check: if all priorities were odd, then W1 union G1.V should be g.V
                assert(set(G1.get_nodes()).union(set(W1)) != rest.get_nodes()
                       or any(rest.get_node_priority_function_i(n, i) % 2 == 0
                              for n in rest.get_nodes()))
                # end of sanity check

                if len(G1.get_nodes()) == 0 or set(W2) == set(H1.get_nodes()):
                    break

                T, compl_T = attractor(G1, W1, 0)
                G1 = G1.subgame(compl_T)
                E, compl_E = attractor(G1,
                                                    ops.i_priority_node_function_j(G1, maxValues[i] - 1, i + 1), 1)
                H1 = G1.subgame(compl_E)
                # assert(len(H1.get_nodes()) < h1_old_len)

            # checks after the end of the loop (base cases, essentially)
            if set(W2) == set(H1.get_nodes()) and len(G1.get_nodes()) > 0:
                assert(len(G1.get_nodes()) > 0)  # otherwise this makes no sense!
                B, compl_B = attractor(rest, G1.get_nodes(), 1)
                # sanity check: we always do a recursive call on a smaller game
                # and so necessarily B is non-empty
                assert(len(B) > 0)
                # end of sanity check
                W1, W2 = disj_parity_win_with_partial(rest.subgame(compl_B), maxValues, k, u + 1, partial)
                B.extend(W2)
                return W1, B

    return rest.get_nodes(), []
"""