from bdd.bdd_util import *
import math
from bdd.arena import Arena


def symb_dpa2gpg(aut, ap_inpt, ap_oupt, manager, restrict_reach_edges=False):
    """
    Construct a new symbolic generalized parity game (gpg) from a symbolic generalized parity automaton (dpa).
    :param aut: the source automaton
    :type aut: SymbolicGenDPA
    :param ap_inpt: the input atomic propositions, controlled by the environment (player 1).
    :type ap_inpt: list[str]
    :param ap_oupt: the output atomic propositions, controlled by the system (player 0).
    :type ap_oupt: list[str]
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :param restrict_reach_edges: true to restrict edges in addition to vertices, it may not be needed
    :type restrict_reach_edges: bool
    :return: a symbolic gpg object that represents the symbolic dpa
    :rtype: Arena
    """

    # First, we define the variables to represent the symbolic arena through the BDD,
    # we need bis variables to define the outgoing vertex of each edge.

    ap_inpt_bis = list(map(lambda s: s + 'b"', ap_inpt))

    vars = aut.vars + ap_inpt + ['i']
    vars_bis = aut.vars_bis + ap_inpt_bis + ['ib']
    all_vars = vars + vars_bis

    mapping_bis = dict(zip(vars, vars_bis))
    inv_mapping_bis = dict(zip(vars_bis, vars))

    manager.declare(*all_vars)

    nbr_vertices = aut.nbr_vertices * (1 + int(math.pow(2, len(ap_inpt))))
    nbr_digits_vertices = len(bin(nbr_vertices - 1)) - 2
    dimension = aut.dimension

    vari = manager.var("i")
    varib = manager.var("ib")

    # player0 : system, has vertices defined with i, player1 : env, possesses the complementaty
    sys_vertices = vari
    env_vertices = ~vari

    init = aut.init & ~vari & reduce(and_iter, [~manager.var(a) for a in ap_inpt])

    # Transitions controlled by the environment and not system is a conjunction :
    # - from non-intermediate states to intermediate state (!i & i")
    # - states variables of automaton are unchanged, it's the system that changes that (q1 <=> q1" & q2 <=> q2" & ...)
    # - always starts with variable of environment to false (!a1 & !a2 ...)
    edges_env = ~vari & varib & reduce(and_iter, [~manager.var(a) for a in ap_inpt]) \
                & reduce(and_iter, [manager.var(q).equiv(manager.var(qb)) for q, qb in zip(aut.vars, aut.vars_bis)])

    # Transitions controlled by the system is a conjunction :
    # - from intermediate states to a non-intermediate state (i & !i")
    # - cannot goes to a state with variable of environment AP to true (!a1" & !a2" & ...)
    # - when system takes an edge, we finish a "loop" (we took a single transition in dpa while it's 2 in the
    #   corresponding gpg), we want to start from a state that has an AP input label to true iff label of the previous
    #   transition (used by system, or the label of the corresponding transition in DPA) contains this input label.
    #   Rename in dpa transition a -> a' as these state variables hold the environment's assignment of its atomic
    #   propositions. We also remove labels of ap_output to ignore them, with "exist".
    edges_sys = vari & ~varib & manager.exist(ap_oupt, aut.transitions) \
                & reduce(and_iter, [~manager.var(ax) for ax in ap_inpt_bis])

    # Edges of arena is edges of system and edges of environment
    edges = edges_sys | edges_env

    # Actually we can simply use same priorities since intermediate states can have the same priorities then their
    # (unique) predecessor. It will transfer priority automatically because additional states variables (i, ap_inpt...)
    # are implicitly considered (use care_vars= to see every states on priorities). Otherwise we can use " & !i " for
    # every existing priorities in DPA (environment states) then link a priority -1 to states represented by i if we
    # want to set the same priorities for every intermediate states.
    priorities = aut.priorities

    arena = Arena()

    arena.vars = vars
    arena.vars_bis = vars_bis
    arena.all_vars = all_vars
    arena.mapping_bis = mapping_bis
    arena.inv_mapping_bis = inv_mapping_bis

    arena.nbr_vertices = nbr_vertices
    arena.nbr_digits_vertices = nbr_digits_vertices
    arena.nbr_functions = dimension

    arena.player0_vertices = sys_vertices
    arena.player1_vertices = env_vertices
    arena.edges = edges
    arena.priorities = priorities

    # If there are some reachable states, arena.nbr_vertices becomes incorrect, we should
    # count with a SAT count to correct this, which is a heavy operation we cannot afford.
    # Solver algorithms do not use the variable arena.nbr_vertices, so it doesn't matter.
    arena.restrict_to_reachable_states(init, manager,
                                       restrict_reach_edges=restrict_reach_edges,
                                       mapping_bis=mapping_bis)

    return arena, init
