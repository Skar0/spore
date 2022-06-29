import sys

import dd.cudd as _bdd

import regular.gpg2arena as reg_gpg_loader
import regular.generalizedRecursive as reg_gpg_recursive

import bdd.gpg2bdd as bdd_gpg_loader
import bdd.generalizedRecursive as bdd_gpg_recursive

from bdd.dpa2bdd import get_product_automaton
from bdd.dpa2gpg import symb_dpa2gpg
from bdd.bdd_util import decomp_data_file


# Increase the recursion limit to avoid error when we read a long label with explicit2symbolic_path
sys.setrecursionlimit(50000)


def get_gpg_sizes_and_number_of_functions(gpg_path):
    manager = _bdd.BDD()
    arena, _ = bdd_gpg_loader.gpg2bdd(gpg_path, manager)
    return len(manager), arena.nbr_vertices, arena.nbr_functions

def solve_gpg_regular(gpg_path):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation of
    the recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    arena = reg_gpg_loader.gpg2arena(gpg_path)
    winning_0, winning_1 = reg_gpg_recursive.generalized_recursive(arena)
    player0_won = 0 in winning_0

    return player0_won, winning_0, winning_1


def solve_gpg_regular_partial(gpg_path):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation of
    the combination of the recursive algorithm and a partial solver. This implementation performs a single call to the
    partial solver before running the recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    arena = reg_gpg_loader.gpg2arena(gpg_path)
    winning_0, winning_1 = reg_gpg_recursive.generalized_recursive_with_buchi(arena)
    player0_won = 0 in winning_0

    return player0_won, winning_0, winning_1


def solve_gpg_regular_partial_multiple_calls(gpg_path):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation of
    the combination of the recursive algorithm and a partial solver. This implementation performs a call to the partial
    solver in each recursive call.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    arena = reg_gpg_loader.gpg2arena(gpg_path)
    winning_0, winning_1 = reg_gpg_recursive.generalized_recursive_with_buchi_multiple_calls(arena)
    player0_won = 0 in winning_0

    return player0_won, winning_0, winning_1


def solve_gpg_bdd(gpg_path):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the bdd implementation of the
    recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    manager = _bdd.BDD()
    arena, all_vertices = bdd_gpg_loader.gpg2bdd(gpg_path, manager)
    winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive(arena, manager)
    vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
    player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    return player0_won, winning_0, winning_1


def solve_gpg_bdd_partial(gpg_path):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the bdd implementation of the
    combination of the recursive algorithm and a partial solver. This implementation performs a single call to the
    partial solver before running the recursive algorithm.
    """
    manager = _bdd.BDD()
    arena, all_vertices = bdd_gpg_loader.gpg2bdd(gpg_path, manager)
    winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive_with_psolver(arena, manager)
    vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
    player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    return player0_won, winning_0, winning_1


def solve_gpg_bdd_partial_multiple_calls(gpg_path):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the bdd implementation of the
    combination of the recursive algorithm and a partial solver. This implementation performs a call to the partial
    sover in each recursive call.
    """
    manager = _bdd.BDD()
    arena, all_vertices = bdd_gpg_loader.gpg2bdd(gpg_path, manager)
    winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive_with_psolver_multiple_calls(arena, manager)
    vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
    player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    return player0_won, winning_0, winning_1


def construct_full_bdd_arena(data_path, dynamic_reordering=True, arbitrary_reordering=True):
    input_signals, output_signals, automata_paths = decomp_data_file(data_path)

    manager = _bdd.BDD()
    manager.declare(*input_signals, *output_signals)
    manager.configure(reordering=dynamic_reordering)

    product = get_product_automaton(automata_paths, manager, arbitrary_reordering=arbitrary_reordering,
                                    aps=input_signals + output_signals)

    arena, init = symb_dpa2gpg(product, input_signals, output_signals, manager)

    return manager, arena, init


def get_gpg_full_bdd_sizes(data_path, dynamic_reordering=True, arbitrary_reordering=True):
    manager, arena, _ = construct_full_bdd_arena(data_path, dynamic_reordering, arbitrary_reordering)

    return len(manager), len(list(manager.pick_iter(arena.player0_vertices | arena.player1_vertices))), arena.nbr_functions


def solve_gpg_full_bdd(data_path, dynamic_reordering=True, arbitrary_reordering=True):
    manager, arena, init = construct_full_bdd_arena(data_path, dynamic_reordering, arbitrary_reordering)
    winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive(arena, manager)
    vertex_0_dict_rep = next(manager.pick_iter(init))
    player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    return player0_won, winning_0, winning_1


def solve_gpg_full_bdd_partial(data_path, dynamic_reordering=True, arbitrary_reordering=True):
    manager, arena, init = construct_full_bdd_arena(data_path, dynamic_reordering, arbitrary_reordering)
    winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive_with_psolver(arena, manager)
    vertex_0_dict_rep = next(manager.pick_iter(init))
    player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    return player0_won, winning_0, winning_1


def solve_gpg_full_bdd_partial_multiple_calls(data_path, dynamic_reordering=True, arbitrary_reordering=True):
    manager, arena, init = construct_full_bdd_arena(data_path, dynamic_reordering, arbitrary_reordering)
    winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive_with_psolver_multiple_calls(arena, manager)
    vertex_0_dict_rep = next(manager.pick_iter(init))
    player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    return player0_won, winning_0, winning_1


if __name__ == "__main__":
    mode = sys.argv[1]
    path = sys.argv[2]
    fbdd_dynamic_reordering = len(sys.argv) > 3 and sys.argv[3] == "True"
    fbdd_arbitrary_reordering = len(sys.argv) > 4 and sys.argv[4] == "True"

    if mode == "gpgSizeFunc":
        bdd_size, game_size, n_func = get_gpg_sizes_and_number_of_functions(path)
        with open("/tmp/out", "w") as f:
            f.write(str(bdd_size) + "\n" + str(game_size) + "\n" + str(n_func) + "\n")
    elif mode == "fbddSizes":
        bdd_size, game_size, n_func = get_gpg_full_bdd_sizes(path, fbdd_dynamic_reordering, fbdd_arbitrary_reordering)
        with open("/tmp/out", "w") as f:
            f.write(str(bdd_size) + "\n" + str(game_size) + "\n" + str(n_func) + "\n")
    elif mode == "reg":
        solve_gpg_regular(path)
    elif mode == "regPa":
        solve_gpg_regular_partial(path)
    elif mode == "regPaMu":
        solve_gpg_regular_partial_multiple_calls(path)
    elif mode == "bdd":
        solve_gpg_bdd(path)
    elif mode == "bddPa":
        solve_gpg_bdd_partial(path)
    elif mode == "bddPaMu":
        solve_gpg_bdd_partial_multiple_calls(path)
    elif mode == "fbdd":
        solve_gpg_full_bdd(path, fbdd_dynamic_reordering, fbdd_arbitrary_reordering)
    elif mode == "fbddPa":
        solve_gpg_full_bdd_partial(path, fbdd_dynamic_reordering, fbdd_arbitrary_reordering)
    elif mode == "fbddPaMu":
        solve_gpg_full_bdd_partial_multiple_calls(path, fbdd_dynamic_reordering, fbdd_arbitrary_reordering)
    else:
        raise Exception("Invalid mode " + mode)
