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
            pp = priority % 2
            # TODO my impl monotone attractor
            #monotone_att = monotone_attractor_cha(manager, arena, pp, target_set, priority)
            monotone_att = monotone_attractor(arena, target_set, priority, manager)

            # TODO test si la facon de def subset est correcte
            #assert ((monotone_att | target_set) == monotone_att) == ((~target_set | monotone_att) == manager.true)
            if (monotone_att | target_set) == monotone_att: #if (~target_set | monotone_att) == manager.true: #TODO check this is implication, check apply perf, check preimage perf  (monotone_att | target_set) == monotone_att:

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
