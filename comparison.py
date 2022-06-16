# -*- coding: utf-8 -*-
# SPORE: Symbolic Partial sOlvers for REalizability. 
# Copyright (C) 2021 - Charly Delfosse (University of Mons), Gaëtan Staquet (University of Mons), Clément Tamines (University of Mons)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from os import listdir, stat
import signal
from contextlib import contextmanager
import time
import dd.cudd as _bdd
import traceback
import os.path

import regular.pg2arena as reg_pg_loader
import regular.recursive as reg_pg_recursive

import regular.gpg2arena as reg_gpg_loader
import regular.generalizedRecursive as reg_gpg_recursive

import bdd.pg2bdd as bdd_pg_loader
import bdd.recursive as bdd_pg_recursive

import bdd.gpg2bdd as bdd_gpg_loader
import bdd.generalizedRecursive as bdd_gpg_recursive

from bdd.dpa2bdd import explicit2symbolic_path
from bdd.dpa2gpg import symb_dpa2gpg
from bdd.bdd_util import decomp_data_file
from functools import reduce


# from https://www.jujens.eu/posts/en/2018/Jun/02/python-timeout-function/#:~:text=You%20can%20use%20signals%20and,alarm%20signal%20for%20the%20timeout.&text=Even%20if%20this%20solution%20works,which%20can%20be%20a%20problem.

class TimeOutException(Exception):
    def __init__(self):
        pass


@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeOutException:
        print("    " * 10 + " timeout occurred")
        pass
    except Exception as err:
        print("    " * 10 + " exception occurred")
        exception_type = type(err).__name__
        print(exception_type)
        print(err)
        track = traceback.format_exc()
        print(track)
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeOutException()


def solve_pg_regular(pg_path, timeout_value):
    """
    Load and solve the parity game whose path is provided in parameter using the regular implementation of the recursive
    algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        arena = reg_pg_loader.pg2arena(pg_path)
        winning_0, winning_1 = reg_pg_recursive.recursive(arena)
        player0_won = 0 in winning_0

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_pg_regular_partial(pg_path, timeout_value):
    """
    Load and solve the parity game whose path is provided in parameter using the regular implementation of the
    combination of a partial solver and the recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        arena = reg_pg_loader.pg2arena(pg_path)
        winning_0, winning_1 = reg_pg_recursive.recursive_with_buchi(arena)
        player0_won = 0 in winning_0

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_pg_bdd(pg_path, timeout_value):
    """
    Load and solve the parity game whose path is provided in parameter using the bdd implementation of the recursive
    algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        manager = _bdd.BDD()

        arena, all_vertices = bdd_pg_loader.pg2bdd(pg_path, manager)
        winning_0, winning_1 = bdd_pg_recursive.recursive(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_pg_bdd_partial(pg_path, timeout_value):
    """
    Load and solve the parity game whose path is provided in parameter using the bdd implementation of the combination
    of the recursive algorithm and a partial solver. This is Charly's implementation.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        manager = _bdd.BDD()

        arena, all_vertices = bdd_pg_loader.pg2bdd(pg_path, manager)
        winning_0, winning_1 = bdd_pg_recursive.ziel_with_psolver(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_pg_bdd_partial_debug(pg_path, timeout_value):
    """
    Load and solve the parity game whose path is provided in parameter using the bdd implementation of the combination
    of the recursive algorithm and a partial solver. This is Clement's implementation.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        manager = _bdd.BDD()

        arena, all_vertices = bdd_pg_loader.pg2bdd(pg_path, manager)
        winning_0, winning_1 = bdd_pg_recursive.recursive_with_buchi(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_gpg_regular(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation of
    the recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        arena = reg_gpg_loader.gpg2arena(gpg_path)
        winning_0, winning_1 = reg_gpg_recursive.generalized_recursive(arena)
        player0_won = 0 in winning_0

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_gpg_regular_partial(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation of
    the combination of the recursive algorithm and a partial solver. This implementation performs a single call to the
    partial solver before running the recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        arena = reg_gpg_loader.gpg2arena(gpg_path)
        winning_0, winning_1 = reg_gpg_recursive.generalized_recursive_with_buchi(arena)
        player0_won = 0 in winning_0

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_gpg_regular_partial_multiple_calls(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation of
    the combination of the recursive algorithm and a partial solver. This implementation performs a call to the partial
    solver in each recursive call.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        arena = reg_gpg_loader.gpg2arena(gpg_path)
        winning_0, winning_1 = reg_gpg_recursive.generalized_recursive_with_buchi_multiple_calls(arena)
        player0_won = 0 in winning_0

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_gpg_bdd(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the bdd implementation of the
    recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        manager = _bdd.BDD()
        arena, all_vertices = bdd_gpg_loader.gpg2bdd(gpg_path, manager)
        winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_gpg_bdd_partial(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the bdd implementation of the
    combination of the recursive algorithm and a partial solver. This implementation performs a single call to the
    partial solver before running the recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        manager = _bdd.BDD()
        arena, all_vertices = bdd_gpg_loader.gpg2bdd(gpg_path, manager)
        winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive_with_psolver(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_gpg_bdd_partial_multiple_calls(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the bdd implementation of the
    combination of the recursive algorithm and a partial solver. This implementation performs a call to the partial
    sover in each recursive call.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        manager = _bdd.BDD()
        arena, all_vertices = bdd_gpg_loader.gpg2bdd(gpg_path, manager)
        winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive_with_psolver_multiple_calls(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1


def solve_gpg_full_bdd(data_path, timeout_value):
    player0_won = "TIMEOUT"
    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        input_signals, output_signals, automata_paths = decomp_data_file(data_path)

        manager = _bdd.BDD()
        manager.declare(*input_signals, *output_signals)
        manager.configure(reordering=True)

        automata = [explicit2symbolic_path(path, manager) for path in automata_paths]

        product = reduce(lambda a1, a2: a1.product(a2, manager), automata)

        arena, init = symb_dpa2gpg(product, input_signals, output_signals, manager)
        n_nodes_in_bdd = len(manager)

        winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(init))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1, n_nodes_in_bdd, arena.nbr_vertices


def solve_gpg_full_bdd_partial(data_path, timeout_value):
    player0_won = "TIMEOUT"
    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        input_signals, output_signals, automata_paths = decomp_data_file(data_path)

        manager = _bdd.BDD()
        manager.declare(*input_signals, *output_signals)
        manager.configure(reordering=True)

        automata = [explicit2symbolic_path(path, manager) for path in automata_paths]

        product = reduce(lambda a1, a2: a1.product(a2, manager), automata)

        arena, init = symb_dpa2gpg(product, input_signals, output_signals, manager)
        n_nodes_in_bdd = len(manager)

        winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive_with_psolver(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(init))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1, n_nodes_in_bdd, arena.nbr_vertices


def solve_gpg_full_bdd_partial_multiple_calls(data_path, timeout_value):
    player0_won = "TIMEOUT"
    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        input_signals, output_signals, automata_paths = decomp_data_file(data_path)

        manager = _bdd.BDD()
        manager.declare(*input_signals, *output_signals)
        manager.configure(reordering=True)

        automata = [explicit2symbolic_path(path, manager) for path in automata_paths]

        product = reduce(lambda a1, a2: a1.product(a2, manager), automata)

        arena, init = symb_dpa2gpg(product, input_signals, output_signals, manager)
        n_nodes_in_bdd = len(manager)

        winning_0, winning_1 = bdd_gpg_recursive.generalized_recursive_with_psolver_multiple_calls(arena, manager)
        vertex_0_dict_rep = next(manager.pick_iter(init))
        player0_won = manager.let(vertex_0_dict_rep, winning_0) == manager.true

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time, winning_0, winning_1, n_nodes_in_bdd, arena.nbr_vertices

def time_construction_game_full_bdd(data_path, timeout_value):
    start_time = time.time()

    with timeout(timeout_value):
        input_signals, output_signals, automata_paths = decomp_data_file(data_path)

        manager = _bdd.BDD()
        manager.declare(*input_signals, *output_signals)
        manager.configure(reordering=True)

        automata = [explicit2symbolic_path(path, manager) for path in automata_paths]

        product = reduce(lambda a1, a2: a1.product(a2, manager), automata)

        symb_dpa2gpg(product, input_signals, output_signals, manager)
    end_time = "%.5f" % (time.time() - start_time)
    return end_time

def get_non_empty_tlsf(path):
    """
    Get all names of tlsf files yielding at least one non-empty .pg or .gpg file
    """

    file_names = []
    empty_for_both = []

    for file_name in listdir(path):

        if file_name[-5:] == ".tlsf":

            # current file is a .tlsf

            empty_pg = False
            empty_gpg = False

            # check whether at least one of the games is not empty
            if os.path.isfile(path + file_name + ".pg"):
                empty_pg = stat(path + file_name + ".pg").st_size != 0
            if os.path.isfile(path + file_name + ".gpg"):
                empty_gpg = stat(path + file_name + ".gpg").st_size != 0

            if empty_pg or empty_gpg:
                file_names.append(file_name)
            else:
                empty_for_both.append(file_name)

    return file_names


def get_tlsf_files(path):
    file_names = []

    for file_name in listdir(path):

        if file_name[-5:] == ".tlsf":
            file_names.append(file_name)

    return file_names


def get_game_size(path):
    """
    Returns the size of the game arena and number of functions.
    """
    with open(path, "r") as game_file:
        # first line has max index for vertices and number of priority functions; vertices and function index start at 0
        info_line = game_file.readline().rstrip().split(" ")

        max_index = int(info_line[1])

        nbr_functions = int(info_line[2][:-1])

        nbr_vertices = max_index + 1

    return nbr_vertices, nbr_functions


def check_consistency_regular(regions, realizability, is_pg, file_path):
    """
    Checks the consistency of the winning regions computed by the regular algorithms.
    """

    # only keep the regions that were actually computed, meaning we exclude timeouts
    computed_regions = [region for region in regions if region[0] is not None]
    nbr_computed_regions = len(computed_regions)

    # same goes for the realizability
    computed_realizability = [real for real in realizability if real != "TIMEOUT"]

    if is_pg:
        arena_check_pg = reg_pg_loader.pg2arena(file_path)
        nbr_vertices_check = arena_check_pg.nbr_vertices
    else:
        arena_check_gpg = reg_gpg_loader.gpg2arena(file_path)
        nbr_vertices_check = arena_check_gpg.nbr_vertices

    # check that for each computed solution, intersection is empty and union is the set of vertices
    for region in computed_regions:
        assert (set(region[0]).intersection(region[1]) == set())
        assert (set(region[0]).union(region[1]) == set(range(nbr_vertices_check)))

    # there has to be at least 2 to compare
    if nbr_computed_regions >= 2:
        for i in range(nbr_computed_regions-1):
            compare_a = computed_regions[i]
            compare_b = computed_regions[i+1]

            assert set(compare_a[0]) == set(compare_b[0])
            assert set(compare_a[1]) == set(compare_b[1])

            assert computed_realizability[i] == computed_realizability[i + 1]


def check_consistency_bdd(regions, realizability, is_pg, file_path):
    """
    Checks the consistency of the winning regions computed by the bdd algorithms.
    """

    # only keep the regions that were actually computed, meaning we exclude timeouts
    computed_regions = [region for region in regions if region[0] is not None]
    nbr_computed_regions = len(computed_regions)

    # same goes for the realizability
    computed_realizability = [real for real in realizability if real != "TIMEOUT"]

    manager = _bdd.BDD()

    if is_pg:
        arena_check, all_vertices = bdd_pg_loader.pg2bdd(file_path, manager)
    else:
        arena_check, all_vertices = bdd_gpg_loader.gpg2bdd(file_path, manager)

    all_vertices_in_arena = arena_check.player0_vertices | arena_check.player1_vertices

    # check that for each computed solution, intersection is empty and union is the set of vertices
    for region in computed_regions:
        pass
        #assert(((region[0] & region[1]) & all_vertices_in_arena) == manager.false)
        #assert(((region[0] | region[1]) & all_vertices_in_arena) == all_vertices_in_arena)


    # there has to be at least 2 to compare
    if nbr_computed_regions >= 2:
        for i in range(nbr_computed_regions-1):
            compare_a = computed_regions[i]
            compare_b = computed_regions[i+1]

            #assert set(compare_a[0]) == set(compare_b[0])
            #assert set(compare_a[1]) == set(compare_b[1])

            assert computed_realizability[i] == computed_realizability[i + 1]


# path to the directory which contains all tlsf files and all generated (empty or not) files
tlsf_and_games = "/home/clement/CLionProjects/tlsf2gpg/examples-afterfix/"

# name for the .csv file containing the comparison between the running times
comparison_file_name = "saturday-night-runall-regen-10m.csv"

# timeout value for the algorithms
out = 60 * 10

# whether to check the solutions (that is, check that the solution computed by each algorithm is the same and that the
# intersection of the winning regions is empty and their union is the whole arena)
check_solution = True

# check whether there were errors in the code
error_count = 0

def compare_all_files(input_path, output_path, timeout):
    with open(output_path, "a") as f:

        f.write("FILE, "
                "GPG SIZE, "
                "GPG FUNC, "
                "REG TIME, "
                "REG PA TIME, "
                "REG PA MU TIME, "
                "BDD TIME, "
                "BDD PA TIME, "
                "BDD PA MU TIME, "
                "FULL BDD GENERATION TIME, "
                "FULL BDD BDD SIZE, "
                "FULL BDD GAME SIZE, "
                "FULL BDD TIME, "
                "FULL BDD PA TIME, "
                "FULL BDD PA MU TIME, "
                "REAL REG PG, "
                "REAL REG PA PG, "
                "REAL BDD PG, "
                "REAL BDD PA CHA PG, "
                "REAL BDD PA CLEM PG, "
                "REAL REG GPG, "
                "REAL REG PA GPG, "
                "REAL REG PA MU GPG, "
                "REAL BDD GPG, "
                "REAL BDD PA GPG, "
                "REAL BDD PA MU GPG, "
                "\n")

        # at_least_one_non_empty = sorted(get_non_empty_tlsf(input_path))
        all_files = sorted(get_tlsf_files(input_path))

        # nbr_files = len(at_least_one_non_empty)
        nbr_files = len(all_files)

        current_done = 0

        # for file_name in at_least_one_non_empty:
        for file_name in all_files:
            print(file_name)

            print("    " * 10 + file_name + " " + str(int(100 * (float(current_done) / float(nbr_files)))) + " % done")
            current_done += 1

            file_path = input_path + file_name

            result_string = ""
            result_string += file_name
            result_string += ", "

            realizability = []

            # generalized parity game analysis
            print("generalized")
            gpg_file_path = file_path + ".gpg"

            if stat(gpg_file_path).st_size != 0:
                gpg_size, gpg_func = get_game_size(gpg_file_path)
            else:
                gpg_size = "NOT GEN"
                gpg_func = "NOT GEN"

            result_string += str(gpg_size)
            result_string += ", "

            result_string += str(gpg_func)
            result_string += ", "

            if gpg_size != "NOT GEN":
                print("    regular")
                won_player_0_reg, time_reg, gen_parity_winning_0_reg, gen_parity_winning_1_reg = solve_gpg_regular(
                    gpg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "

                print("    regular partial")
                won_player_0_reg_par, time_reg_par, gen_parity_winning_0_reg_par, gen_parity_winning_1_reg_par = solve_gpg_regular_partial(
                    gpg_file_path, timeout)
                realizability.append(won_player_0_reg_par)
                result_string += str(time_reg_par)
                result_string += ", "

                print("    regular partial multiple calls")
                won_player_0_reg_par_multiple, time_reg_par_multiple, gen_parity_winning_0_reg_par_multiple, gen_parity_winning_1_reg_par_multiple = solve_gpg_regular_partial_multiple_calls(
                    gpg_file_path, timeout)
                realizability.append(won_player_0_reg_par_multiple)
                result_string += str(time_reg_par_multiple)
                result_string += ", "

                print("    bdd")
                won_player_0_bdd, time_bdd, gen_parity_winning_0_bdd, gen_parity_winning_1_bdd = solve_gpg_bdd(
                    gpg_file_path, timeout)
                realizability.append(won_player_0_bdd)
                result_string += str(time_bdd)
                result_string += ", "

                print("    bdd partial ")
                won_player_0_bdd_par, time_bdd_par, gen_parity_winning_0_bdd_par, gen_parity_winning_1_bdd_par = solve_gpg_bdd_partial(
                    gpg_file_path, timeout)
                realizability.append(won_player_0_bdd_par)
                result_string += str(time_bdd_par)
                result_string += ", "

                print("    bdd partial multiple calls")
                won_player_0_bdd_par_multiple, time_bdd_par_multiple, gen_parity_winning_0_bdd_par_multiple, gen_parity_winning_1_bdd_par_multiple = solve_gpg_bdd_partial_multiple_calls(
                    gpg_file_path, timeout)
                realizability.append(won_player_0_bdd_par_multiple)
                result_string += str(time_bdd_par_multiple)
                result_string += ", "

                if check_solution:
                    # checking all results between them

                    gpg_regions_reg = [(gen_parity_winning_0_reg, gen_parity_winning_1_reg),
                                  (gen_parity_winning_0_reg_par, gen_parity_winning_1_reg_par),
                                (gen_parity_winning_0_reg_par_multiple, gen_parity_winning_1_reg_par_multiple)]

                    gpg_real_reg = [won_player_0_reg, won_player_0_reg_par, won_player_0_reg_par_multiple]

                    check_consistency_regular(gpg_regions_reg, gpg_real_reg, False, gpg_file_path)

                    gpg_regions_bdd = [(gen_parity_winning_0_bdd, gen_parity_winning_1_bdd),
                                  (gen_parity_winning_0_bdd_par, gen_parity_winning_1_bdd_par),
                                      (gen_parity_winning_0_bdd_par_multiple, gen_parity_winning_1_bdd_par_multiple)]

                    gpg_real_bdd = [won_player_0_bdd, won_player_0_bdd_par, won_player_0_bdd_par_multiple]

                    check_consistency_bdd(gpg_regions_bdd, gpg_real_bdd, False, gpg_file_path)


            else:
                result_string += gpg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += gpg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += gpg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += gpg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += gpg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += gpg_size
                result_string += ", "
                realizability.append("NOT GEN")

            full_bdd_data_path = "automata/" + file_name + "/data.txt"
            print("    generating game")
            time_generation = time_construction_game_full_bdd(full_bdd_data_path, timeout)
            result_string += str(time_generation)
            result_string += ", "

            print("    full bdd")
            won_player_0_full_bdd, time_full_bdd, gen_parity_winning_0_full_bdd, gen_parity_winning_1_full_bdd, n_nodes_in_bdd, nbr_vertices_in_game = solve_gpg_full_bdd(
                full_bdd_data_path, timeout)
            realizability.append(won_player_0_full_bdd)
            result_string += str(n_nodes_in_bdd)
            result_string += ", "
            result_string += str(nbr_vertices_in_game)
            result_string += ", "
            result_string += str(time_full_bdd)
            result_string += ", "

            print("    full bdd partial")
            won_player_0_full_bdd_par, time_full_bdd_par, gen_parity_winning_0_full_bdd_par, gen_parity_winning_1_full_bdd_par, _, _ = solve_gpg_full_bdd_partial(
                full_bdd_data_path, timeout)
            realizability.append(won_player_0_full_bdd_par)
            result_string += str(time_full_bdd_par)
            result_string += ", "

            print("    full bdd partial multiple calls")
            won_player_0_full_bdd_par_multiple, time_full_bdd_par_multiple, gen_parity_winning_0_full_bdd_par_multiple, gen_parity_winning_1_full_bdd_par_multiple, _, _ = solve_gpg_full_bdd_partial_multiple_calls(
                full_bdd_data_path, timeout)
            realizability.append(won_player_0_full_bdd_par_multiple)
            result_string += str(time_full_bdd_par_multiple)
            result_string += ", "

            for realized in realizability:
                result_string += str(realized)
                result_string += ", "

            result_string += " \n"

            f.write(result_string)

        f.close()


compare_all_files(tlsf_and_games, comparison_file_name, out)
