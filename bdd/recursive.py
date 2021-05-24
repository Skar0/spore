from bdd.attractor import attractor
from bdd.buchiSolver import buchi_partial_solver


def recursive(arena, manager):
    """
    Solve the parity game provided in arena using the recursive algorithm implemented with bdds.
    :param arena: a game arena
    :type arena: Arena
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the solution of the provided parity game, that is the set of vertices won by each player
    :rtype: (dd.cudd.Function, dd.cudd.Function)
    """

    winning_region_player0 = manager.false  # winning region of player 0
    winning_region_player1 = manager.false  # winning region of player 1

    # if the game is empty, return the empty regions
    # TOD in the bdd impl the nbr of vertices in not maintained easily
    if (arena.player0_vertices | arena.player1_vertices) == manager.false:
        return winning_region_player0, winning_region_player1

    else:
        max_occurring_priority = max(arena.priorities[0].keys())  # get max priority occurring in g

        # determining which player we are considering, if max_occurring_priority is odd : player 1 and else player 0
        j = 1 if max_occurring_priority % 2 else 0

        opponent = 0 if j else 1  # getting the opponent of the player

        # vertices with priority max_occurring_priority
        U = arena.priorities[0][max_occurring_priority]

        # getting the attractor A
        A = attractor(arena, U, j, manager)

        # The subgame G\A is composed of the vertices not in the attractor
        G_A = arena.subarena(~A, manager) # TODO being consistent between bdd and non bdd for subarena

        # Recursively solving the subgame G\A
        winning_region_player0_G_A, winning_region_player1_G_A = recursive(G_A, manager)

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
        if winning_region_opponent == manager.false:

            # if we consider player1
            if j:
                winning_region_player1 = winning_region_player1 | A
                winning_region_player1 = winning_region_player1 | winning_region_player
            else:
                winning_region_player0 = winning_region_player0 | A
                winning_region_player0 = winning_region_player0 | winning_region_player

        else:
            # compute attractor B
            B = attractor(arena, winning_region_opponent, opponent, manager)

            # The subgame G\B is composed of the vertices not in the attractor
            G_B = arena.subarena(~B, manager)

            # recursively solve subgame G\B
            winning_region_player0_G_B, winning_region_player1_G_B = recursive(G_B, manager)

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

                winning_region_player0 = winning_region_player0 | winning_region_opponent_bis
                winning_region_player0 = winning_region_player0 | B
            else:
                winning_region_player0 = winning_region_player_bis

                winning_region_player1 = winning_region_player1 | winning_region_opponent_bis
                winning_region_player1 = winning_region_player1 | B

    return winning_region_player0, winning_region_player1


def recursive_with_buchi(arena, manager):
    """
    Solve the parity game provided in arena using a combinations of the recursive algorithm and the partial solver
    implemented using bdds.
    :param arena: a game arena
    :type arena: Arena
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the solution of the provided parity game, that is the set of vertices won by each player
    :rtype: (dd.cudd.Function, dd.cudd.Function)
    """

    if arena.player0_vertices == manager.false and arena.player1_vertices == manager.false:
        return manager.false, manager.false

    winning_region_player0 = manager.false  # winning region of player 0
    winning_region_player1 = manager.false  # winning region of player 1

    remaining_arena1, partial_winning_region_player0, partial_winning_region_player1 = buchi_partial_solver(arena,
                                                                                                           manager.false,
                                                                                                           manager.false,
                                                                                                           manager)


    remaining_arena = arena.subarena(~(partial_winning_region_player0 | partial_winning_region_player1), manager)
    # TODO this is a test, is the yielded subarena in the partial solver correct or do i need to complement here
    # ca a l'air correct
    #assert remaining_arena1.player0_vertices == remaining_arena.player0_vertices
    #assert remaining_arena1.player1_vertices == remaining_arena.player1_vertices

    # if the game is empty, return the empty regions
    # TODO in the bdd impl the nbr of vertices in not maintained easily
    if (remaining_arena.player0_vertices | remaining_arena.player1_vertices) == manager.false:
        return partial_winning_region_player0, partial_winning_region_player1

    else:
        max_occurring_priority = max(remaining_arena.priorities[0].keys())  # get max priority occurring in g

        # determining which player we are considering, if max_occurring_priority is odd : player 1 and else player 0
        j = 1 if max_occurring_priority % 2 else 0

        opponent = 0 if j else 1  # getting the opponent of the player

        # vertices with priority max_occurring_priority
        U = remaining_arena.priorities[0][max_occurring_priority]

        # getting the attractor A
        A = attractor(remaining_arena, U, j, manager)

        # The subgame G\A is composed of the vertices not in the attractor
        G_A = remaining_arena.subarena(~A, manager) # TODO being consistent between bdd and non bdd for subarena

        # Recursively solving the subgame G\A
        winning_region_player0_G_A, winning_region_player1_G_A = recursive_with_buchi(G_A, manager)

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
        if winning_region_opponent == manager.false:

            # if we consider player1
            if j:
                winning_region_player1 = winning_region_player1 | A
                winning_region_player1 = winning_region_player1 | winning_region_player
            else:
                winning_region_player0 = winning_region_player0 | A
                winning_region_player0 = winning_region_player0 | winning_region_player

        else:
            # compute attractor B
            B = attractor(remaining_arena, winning_region_opponent, opponent, manager)

            # The subgame G\B is composed of the vertices not in the attractor
            G_B = remaining_arena.subarena(~B, manager)

            # recursively solve subgame G\B
            winning_region_player0_G_B, winning_region_player1_G_B = recursive_with_buchi(G_B, manager)

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

                winning_region_player0 = winning_region_player0 | winning_region_opponent_bis
                winning_region_player0 = winning_region_player0 | B
            else:
                winning_region_player0 = winning_region_player_bis

                winning_region_player1 = winning_region_player1 | winning_region_opponent_bis
                winning_region_player1 = winning_region_player1 | B

    # add the partial solutions to the winning regions
    winning_region_player0 = winning_region_player0 | partial_winning_region_player0
    winning_region_player1 = winning_region_player1 | partial_winning_region_player1

    return winning_region_player0, winning_region_player1

# Return the expression which is evaluate to True for vertices with priority less or equal than max_color
def inf_prio_expr(bdd, max_prio, g):
    expr_res = bdd.false
    for curr_prio in range(0, max_prio + 1):
        expr_res = expr_res | g.priorities[0][curr_prio]
    return expr_res

def monotone_attractor_cha(bdd, g, i, f, d):
    inf_col_expr = inf_prio_expr(bdd, d, g)

    f_1 = g.edges & bdd.let(g.mapping_bis, f)
    f_1 = bdd.exist(g.vars_bis, f_1) & inf_col_expr

    f_2 = g.edges & bdd.let(g.mapping_bis, ~f)
    f_2 = ~ bdd.exist(g.vars_bis, f_2) & inf_col_expr

    if i == 0:
        f_1 = g.player0_vertices & f_1
        f_2 = g.player1_vertices & f_2
    else:
        f_1 = g.player1_vertices & f_1
        f_2 = g.player0_vertices & f_2

    attr_old = f_1 | f_2
    while True:
        f_1 = g.edges & bdd.let(g.mapping_bis, attr_old)
        f_1 = bdd.exist(g.vars_bis, f_1) & inf_col_expr

        f_2 = g.edges & bdd.let(g.mapping_bis, ~ (attr_old | f))
        f_2 = ~ bdd.exist(g.vars_bis, f_2) & inf_col_expr

        if i == 0:
            f_1 = g.player0_vertices & f_1
            f_2 = g.player1_vertices & f_2
        else:
            f_1 = g.player1_vertices & f_1
            f_2 = g.player0_vertices & f_2

        attr_new = attr_old | f_1 | f_2
        if attr_new == attr_old:
            break
        attr_old = attr_new
    return attr_old

def psolB(bdd, g):

    if g.player0_vertices == bdd.false and g.player1_vertices == bdd.false:
        return bdd.false, bdd.false
    d = max(g.priorities[0].keys())
    for curr_p in range(0, d + 1):
        player = curr_p % 2
        x = g.priorities[0][curr_p] & (g.player0_vertices | g.player1_vertices)
        f_old = bdd.false
        while not (x == bdd.false or x == f_old):
            f_old = x
            m_attr_x = monotone_attractor_cha(bdd, g, player, x, curr_p)
            if (m_attr_x | x) == m_attr_x:
                attr_ma = attractor(g, m_attr_x, player, bdd)
                ind_game = g.subarena( ~attr_ma, bdd)
                (w_0, w_1) = psolB(bdd, ind_game)
                if player == 0:
                    w_0 = w_0 | attr_ma
                else:
                    w_1 = w_1 | attr_ma
                return w_0, w_1
            else:
                x = x & m_attr_x

    return bdd.false, bdd.false


def ziel_with_psolver(g, bdd):

    if g.player0_vertices == bdd.false and g.player1_vertices == bdd.false:
        return bdd.false, bdd.false

    z_0, z_1 = psolB(bdd, g)

    g_bar = g.subarena(~(z_0 | z_1), bdd)

    if (g_bar.player0_vertices | g_bar.player1_vertices) == bdd.false:
        return z_0, z_1

    p_max = max(g_bar.priorities[0].keys())  # get max priority occurring in g

    # determining which player we are considering, if max_occurring_priority is odd : player 1 and else player 0
    i = 1 if p_max % 2 else 0

    i = p_max % 2
    x = attractor(g_bar, g_bar.priorities[0][p_max], i, bdd)
    g_ind = g_bar.subarena(~x, bdd)
    (win_0, win_1) = ziel_with_psolver(g_ind, bdd)
    if i == 0:
        win_i = win_0
        win_i_bis = win_1
    else:
        win_i = win_1
        win_i_bis = win_0
    if win_i_bis == bdd.false:
        if i == 0:
            return z_0 | win_i | x, z_1
        else:
            return z_0, z_1 | win_i | x
    else:
        x = attractor(g_bar, win_i_bis, 1 - i, bdd)
        g_ind = g_bar.subarena(~x, bdd)
        (win_0, win_1) = ziel_with_psolver( g_ind, bdd)
        if i == 0:
            return z_0 | win_0, z_1 | win_1 | x
        else:
            return z_0 | win_0 | x, z_1 | win_1