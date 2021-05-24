from bdd.attractor import attractor
from itertools import product
import dd.cudd as bdd_func

def attractor_pos(bdd, g, i, f):
    k = 1

    # Code non-optimized
    # f_1 = (g.tau & bdd.let(g.mapping_bis, f))
    # f_1 = bdd.exist(g.bis_vars, f_1)
    f_1 = bdd_func.and_exists(g.edges, bdd.let(g.mapping_bis, f), g.vars_bis)

    # Code non-optimized
    # f_2 = g.tau & bdd.let(g.mapping_bis, ~f)
    # f_2 = ~(bdd.exist(g.bis_vars, f_2))
    f_2 = ~ bdd_func.and_exists(g.edges, bdd.let(g.mapping_bis, ~f), g.vars_bis)
    if i == 0:
        f_1 = g.player0_vertices & f_1
        f_2 = g.player1_vertices & f_2
    else:
        f_1 = g.player1_vertices & f_1
        f_2 = g.player0_vertices & f_2

    attr_old = f_1 | f_2
    while True:
        # Code non-optimized
        # f_1 = (g.tau & bdd.let(g.mapping_bis, attr_old))
        # f_1 = (bdd.exist(g.bis_vars, f_1))
        f_1 = bdd_func.and_exists(g.edges, bdd.let(g.mapping_bis, attr_old), g.vars_bis)

        # Code non-optimized
        # f_2 = g.tau & bdd.let(g.mapping_bis, ~(attr_old | f))
        # f_2 = ~(bdd.exist(g.bis_vars, f_2))
        f_2 = ~ bdd_func.and_exists(g.edges, bdd.let(g.mapping_bis, ~(attr_old | f)), g.vars_bis)

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
        k = k + 1
    return attr_old

def recur(bdd, g, i, f):
    k = 0
    recur_old = f
    while True:
        f_1 = attractor_pos(bdd, g, i, recur_old)
        recur_new = f & f_1
        if recur_new == recur_old:
            break
        recur_old = recur_new
        k = k + 1
    return recur_old

def buchi(bdd, g, i, f):
    return attractor(g, recur(bdd, g, i, f), i , bdd)


def buchi_inter_safety(bdd, g, i, f, s):
    if i == 0:
        oppo = 1
    else:
        oppo = 0 # TODO here changed because for him -1 is 1 and for me -1 evaluates to False (which is 0)
    attr_adv_f = attractor(g, s,oppo, bdd)
    g_bar = g.subarena(~attr_adv_f, bdd)
    return buchi(bdd, g_bar, i, f)

# Return vertices with even priorities greater or equal than min_prio on dimension f_index
def sup_prio_expr_even(arena, bdd, min_prio, f_index, max_values):
    expr_res = bdd.false
    if min_prio % 2 == 0:
        init_prio = min_prio
    else:
        init_prio = min_prio + 1
    for curr_prio in range(init_prio, max_values[f_index] + 1, 2):
        expr_res = expr_res | arena.priorities[f_index][curr_prio]
    return expr_res


# Return vertices with a odd priority greater or equal than min_prios[l] in at least one dimension l
def sup_one_prio_odd(arena, bdd, min_prios, max_values):
    expr_res = bdd.false
    for prio_f_index in range(arena.nbr_functions):
        if min_prios[prio_f_index] % 2 == 0:
            init_prio = min_prios[prio_f_index] + 1
        else:
            init_prio = min_prios[prio_f_index]
        for curr_prio in range(init_prio, max_values[prio_f_index] + 1, 2):
            expr_res = expr_res | arena.priorities[prio_f_index][curr_prio]
    return expr_res


# Return winning regions in a game with a generalized Buchi objective for player 0
def buchi_gen(bdd, g, f):
    g_copy = g.subarena(g.player0_vertices | g.player1_vertices, bdd)
    while True:
        for curr_f in range(g.nbr_functions):
            b0 = attractor(g_copy, f[curr_f], 0, bdd)
            not_b0 = (g_copy.player0_vertices | g_copy.player1_vertices) & ~b0
            if not not_b0 == bdd.false:
                break
        b1 = attractor( g_copy, not_b0, 1, bdd)
        if b1 == bdd.false:
            break
        not_b1 = ~b1
        g_copy = g_copy.subarena(not_b1, bdd)

    return g_copy.player0_vertices | g_copy.player1_vertices


# Return winning regions in a game with a conjunction of a generalized Buchi objective
# and a safety objective for player 0
def buchi_inter_safety_gen(bdd, g, f, s):
    attr_adv_f = attractor( g, s, 1, bdd)
    g_bar = g.subarena(~attr_adv_f, bdd)
    return buchi_gen(bdd, g_bar, f)


def buchi_solver_gen(arena, manager):
    """
    k = nbr func TODO
    TODO why is d never updated
    @param arena:
    @type arena:
    @param manager:
    @type manager:
    @return:
    @rtype:
    """

    max_priorities = [-1] * arena.nbr_functions

    # TODO should we maintain existing colors somewhere ? Check if this function is a bottleneck
    for function_index in range(arena.nbr_functions):

        for priority, bdd in arena.priorities[function_index].items():

            if (priority) > max_priorities[function_index]:
                max_priorities[function_index] = (priority)

    # Iterate over all 1-priority
    for prio_f_index in range(arena.nbr_functions):
        # arena.d[prio_f_index] max prio selon cette dimension ? TODO
        for curr_prio in range(max_priorities[prio_f_index] + 1):
            if curr_prio % 2 == 1 and not arena.priorities[prio_f_index][curr_prio] == manager.false:
                u = arena.priorities[prio_f_index][curr_prio]
                u_bis = sup_prio_expr_even(arena, manager, curr_prio, prio_f_index, max_priorities)

                w = attractor(arena, buchi_inter_safety(manager, arena, 1, u, u_bis), 1, manager)

                if not w == manager.false:
                    ind_game = arena.subarena(~w, manager)
                    (z0, z1) = buchi_solver_gen(ind_game, manager)
                    return z0, z1 | w

    even_priorities = [[] for _ in range(arena.nbr_functions)]
    for prio_f_index in range(arena.nbr_functions):
        for curr_prio in range(0, max_priorities[prio_f_index] + 1, 2):
            if not arena.priorities[prio_f_index][curr_prio] == manager.false:
                even_priorities[prio_f_index].append(curr_prio)

    all_combinations = product(*even_priorities)
    # Iterate over all 0-priority vectors
    for curr_comb in all_combinations:
        u = [arena.priorities[l][curr_comb[l]] for l in range(arena.nbr_functions)]
        u_bis = sup_one_prio_odd(arena, manager, curr_comb, max_priorities)
        w = attractor(arena, buchi_inter_safety_gen(manager, arena, u, u_bis), 0, manager)
        if not w == manager.false:
            ind_game = arena.subarena(~w, manager)
            (z0, z1) = buchi_solver_gen(ind_game, manager)
            return z0 | w, z1

    return manager.false, manager.false
