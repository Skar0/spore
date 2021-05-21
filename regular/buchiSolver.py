from regular.attractor import monotone_attractor, attractor


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


def buchi_partial_solver(arena, partial_winning_region_player0, partial_winning_region_player1):
    """
    Partial solver for parity games using fatal attractors. Implementation using sets.
    :param arena: the arena we consider
    :type arena: Arena
    :param partial_winning_region_player0: should be empty list when called
    :type partial_winning_region_player0: []
    :param partial_winning_region_player1: should be empty list when called
    :type partial_winning_region_player1: []
    :return: a partial solution sub-arena, partial_player0, partial_player1 in which sub-arena remains unsolved and
    partial_player0 (resp. partial_player1) is included in the winning region of player 0 (resp. player 1) in arena.
    :rtype: Arena, list of int, list of int
    """

    empty_set = set() # TODO is this needed to check emptyness ?

    for priority in sort_priorities_ascending(arena):

        target_set = set(arena.priorities[0][priority])  # set of vertices of priority

        cache = set()

        while cache != target_set and target_set != empty_set:

            cache = target_set

            monotone_att = monotone_attractor(arena, target_set, priority, 0)

            if target_set.issubset(monotone_att):

                regular_att = attractor(arena, monotone_att, priority % 2)

                # if priority is odd
                if priority % 2:
                    partial_winning_region_player1.extend(regular_att)
                else:
                    partial_winning_region_player0.extend(regular_att)

                return buchi_partial_solver(arena.subgame(regular_att),
                                            partial_winning_region_player0,
                                            partial_winning_region_player1)

            else:
                target_set = target_set.intersection(monotone_att)

    return arena, partial_winning_region_player0, partial_winning_region_player1
