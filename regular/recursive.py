from regular.attractor import attractor


def strong_parity_solver_no_strategies(arena):
    """
    Strong parity games solver. This is an implementation of the recursive algorithm used to solve parity games.
    This implementation does not compute the winning strategies (for comparison purpose with other algorithms
    which don't)
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """
    W1 = []  # Winning region of player 0
    W2 = []  # Winning region of player 1

    # if the game is empty, return the empty regions
    if arena.nbr_vertices == 0:
        return W1, W2

    else:
        i = max(arena.priorities[0].keys())  # get max priority occurring in g
        print(i)

        # determining which player we are considering, if i is even : player 0 and else player 1
        j = 1 if i % 2 else 0

        opponent = 0 if j else 1  # getting the opponent of the player

        U = arena.priorities[0][i]

        # getting the attractor A and discarding the region for the opponent
        A = attractor(arena, U, j)

        # The subgame G\A is composed of the nodes not in the attractor, thus the nodes of the opposite player's region
        G_A = arena.subarena(A)

        # Recursively solving the subgame G\A, solution comes as (W_0, W_1)
        sol_player1, sol_player2 = strong_parity_solver_no_strategies(G_A)

        # depending on which player we are considering, assign regions to the proper variables
        # W'_j is noted W_j, sigma'_j is noted sig_j; the same aplies for jbar
        if j == 0:
            W_j = sol_player1
            W_jbar = sol_player2
        else:
            W_j = sol_player2
            W_jbar = sol_player1

        # if W'_jbar is empty we update the regions depending on the current player
        # the region for the whole game for one of the players is empty
        if not W_jbar:
            if j == 0:
                W1.extend(A)
                W1.extend(W_j)
            else:
                W2.extend(A)
                W2.extend(W_j)
        else:
            # compute attractor B
            B = attractor(arena, W_jbar, opponent)
            # The subgame G\B is composed of the nodes not in the attractor, so of the opposite player's winning region
            G_B = arena.subarena(B)

            # recursively solve subgame G\B, solution comes as (W_0, W_1)
            sol_player1_, sol_player2_ = strong_parity_solver_no_strategies(G_B)

            # depending on which player we are considering, assign regions to the proper variables
            # W''_j is noted W__j, sigma''_j is noted sig__j; the same aplies for jbar
            if j == 0:
                W__j = sol_player1_
                W__jbar = sol_player2_
            else:
                W__j = sol_player2_
                W__jbar = sol_player1_

            # the last step is to update the winning regions depending on which player we consider
            if j == 0:
                W1 = W__j

                W2.extend(W__jbar)
                W2.extend(B)

            else:
                W2 = W__j

                W1.extend(W__jbar)
                W1.extend(B)

    return W1, W2
