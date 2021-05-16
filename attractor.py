import dd.cudd as bdd_func


def attractor(arena, s, player, manager):
    """
    Computes the attractor for player for the set s in the provided game arena
    :param arena: the arena in which we compute the attractor
    :param s: the set for which we compute the attractor
    :param player: the player for which we compute the attractor
    :param manager: the BDD manager object
    :return: the computed attractor
    """

    old_attractor = manager.false  # start with empty set
    new_attractor = s  # at first attractor only contains s
    # while a fixpoint is not reached
    while old_attractor != new_attractor:

        old_attractor = new_attractor

        # BDD representing the old attractor set, using prime variables
        old_attractor_prime = manager.let(arena.mapping_bis, old_attractor)

        # BDD representing vertices with at least one successor in the old attractor
        bdd_vertices_one_succ = arena.edges & old_attractor_prime

        vertices_one_succ = manager.exist(arena.vars_bis, bdd_vertices_one_succ)

        # bdd representing vertices with at least one successor outside the previous attractor
        # TODO I assume that vertices in the negation that don't exist are ignored since they dont belong to arena.edges
        bdd_vertices_all_succ = arena.edges & ~old_attractor_prime

        # vertices for which there does not exist a successor outside the previous attractor
        vertices_all_succ = ~manager.exist(arena.vars_bis, bdd_vertices_all_succ)

        # if we compute the attractor for player 0
        if not player:
            player0_vertices_attractor = arena.player0_vertices & vertices_one_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_all_succ
        else:
            player0_vertices_attractor = arena.player0_vertices & vertices_all_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_one_succ

        new_attractor = old_attractor | player0_vertices_attractor | player1_vertices_attractor

    return new_attractor


def attractor_optimized(arena, s, player, manager):
    """
    Computes the attractor for player for the set s in the provided game arena. This is an optimized version using built
    in functions from CUDD.
    :param arena: the arena in which we compute the attractor
    :param s: the set for which we compute the attractor
    :param player: the player for which we compute the attractor
    :param manager: the BDD manager object
    :return: the computed attractor
    """

    old_attractor = manager.false  # start with empty set
    new_attractor = s  # at first attractor only contains s
    # while a fixpoint is not reached
    while old_attractor != new_attractor:
        old_attractor = new_attractor

        # BDD representing the old attractor set, using prime variables
        old_attractor_prime = manager.let(arena.mapping_bis, old_attractor)

        # BDD representing vertices with at least one successor in the old attractor
        vertices_one_succ = bdd_func.and_exists(arena.edges, old_attractor_prime, arena.vars_bis)

        # bdd representing vertices with at least one successor outside the previous attractor
        # TODO I assume that vertices in the negation that don't exist are ignored since they dont belong to arena.edges
        # TODO is complementing the replaced attractor with prime vars same as replacing variables in complement of att
        vertices_all_succ = ~bdd_func.and_exists(arena.edges, ~old_attractor_prime, arena.vars_bis)

        # if we compute the attractor for player 0
        if not player:
            player0_vertices_attractor = arena.player0_vertices & vertices_one_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_all_succ
        else:
            player0_vertices_attractor = arena.player0_vertices & vertices_all_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_one_succ

        new_attractor = old_attractor | player0_vertices_attractor | player1_vertices_attractor

    return new_attractor