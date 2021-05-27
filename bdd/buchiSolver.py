from bdd.attractor import monotone_attractor, attractor


def sort_priorities_ascending(arena):
    """
    Sort priorities occurring in the arena in ascending order.
    :param arena: the arena we consider
    :type arena: Arena
    :return: the colors in g sorted in ascending order.
    :rtype: list of int
    """

    priorities_occurring = arena.priorities[0]
    return sorted(priorities_occurring.keys())


def buchi_partial_solver(arena, partial_winning_region_player0, partial_winning_region_player1, manager):
    """
    Partial solver for parity games using fatal attractors. Implementation using sets.
    :param arena: the arena we consider
    :type arena: Arena
    :param partial_winning_region_player0: should be empty list when called
    :type partial_winning_region_player0: []
    :param partial_winning_region_player1: should be empty list when called
    :type partial_winning_region_player1: []
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: a partial solution sub-arena, partial_player0, partial_player1 in which sub-arena remains unsolved and
    partial_player0 (resp. partial_player1) is included in the winning region of player 0 (resp. player 1) in arena.
    :rtype: (Arena, dd.cudd.Function, dd.cudd.Function)
    """

    empty_set = manager.false

    for priority in sort_priorities_ascending(arena):

        target_set = arena.priorities[0][priority] & (arena.player0_vertices | arena.player1_vertices)# set of vertices of priority

        cache = manager.false

        while cache != target_set and target_set != empty_set:

            cache = target_set

            monotone_att = monotone_attractor(arena, target_set, priority, manager)

            # if target set is a subset of the monotone attractor
            if (monotone_att | target_set) == monotone_att:

                regular_att = attractor(arena, monotone_att, priority % 2, manager)

                # if priority is odd
                if priority % 2:
                    partial_winning_region_player1 = partial_winning_region_player1 | regular_att
                else:
                    partial_winning_region_player0 = partial_winning_region_player0 | regular_att

                return buchi_partial_solver(arena.subarena(~regular_att, manager),
                                            partial_winning_region_player0,
                                            partial_winning_region_player1, manager)

            else:
                target_set = target_set & monotone_att

    return arena, partial_winning_region_player0, partial_winning_region_player1
