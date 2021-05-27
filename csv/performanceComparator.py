from os import listdir, stat
import signal
from contextlib import contextmanager
import time
import dd.cudd as _bdd
import traceback

import regular.pg2arena as reg_pg_loader
import regular.recursive as reg_pg_recursive

import regular.gpg2arena as reg_gpg_loader
import regular.generalizedRecursive as reg_gpg_recursive

import bdd.pg2bdd as bdd_pg_loader
import bdd.recursive as bdd_pg_recursive

import bdd.gpg2bdd as bdd_gpg_loader
import bdd.generalizedRecursive as bdd_gpg_recursive

import bddcython.gpg2bdd as bdd_c_gpg_loader
import bddcython.generalizedRecursive as bdd_c_gpg_recursive

import regularcython.gpg2arena as reg_c_gpg_loader
import regularcython.generalizedRecursive as reg_c_gpg_recursive


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


def solve_gpg_regular_c(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the cythonized regular
    implementation of the recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        arena = reg_c_gpg_loader.gpg2arena(gpg_path)
        winning_0, winning_1 = reg_c_gpg_recursive.generalized_recursive(arena)
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


def solve_gpg_bdd_c(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the cythonized bdd
    implementation of the recursive algorithm.
    """

    player0_won = "TIMEOUT"

    winning_0, winning_1 = None, None

    start_time = time.time()

    with timeout(timeout_value):
        manager = _bdd.BDD()
        arena, all_vertices = bdd_c_gpg_loader.gpg2bdd(gpg_path, manager)
        winning_0, winning_1 = bdd_c_gpg_recursive.generalized_recursive(arena, manager)
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


def get_non_empty_tlsf(path):
    """
    Get all names of tlsf files yielding at least one non-empty .pg or .gpg file
    """

    file_names = []
    empty_for_both = []

    for file_name in listdir(path):

        if file_name[-5:] == ".tlsf":

            # current file is a .tlsf

            # check whether at least one of the games is not empty
            empty_pg = stat(path + file_name + ".pg").st_size != 0
            empty_gpg = stat(path + file_name + ".gpg").st_size != 0

            if empty_pg or empty_gpg:
                file_names.append(file_name)
            else:
                empty_for_both.append(file_name)

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
    print(computed_regions)
    nbr_computed_regions = len(computed_regions)
    print(nbr_computed_regions)

    # same goes for the realizability
    computed_realizability = [real for real in realizability if real != "TIMEOUT"]
    print(computed_realizability)

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
tlsf_and_games = "csv/tlsf-after-2min-added-gen-fater-20/"

# name for the .csv file containing the comparison between the running times
comparison_file_name = "thursday-15h-5min.csv"

# timeout value for the algorithms
out = 5 * 60

# whether to check the solutions (that is, check that the solution computed by each algorithm is the same and that the
# intersection of the winning regions is empty and their union is the whole arena)
check_solution = True

# check whether there were errors in the code
error_count = 0


def compare_all_files(input_path, output_path, timeout):
    with open(output_path, "a") as f:

        f.write("FILE, "
                "PG SIZE, "
                "REG TIME, "
                "REG PA TIME, "
                "BDD TIME, "
                "BDD PA CHA TIME, "
                "BDD PA CLEM TIME, "
                "GPG SIZE, "
                "GPG FUNC, "
                "REG TIME, "
                "REG PA TIME, "
                "REG PA MU TIME, "
                "BDD TIME, "
                "BDD PA TIME, "
                "BDD PA MU TIME, "
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

        at_least_one_non_empty = sorted(get_non_empty_tlsf(input_path))

        nbr_files = len(at_least_one_non_empty)

        current_done = 0

        for file_name in at_least_one_non_empty:

            print("    " * 10 + file_name + " " + str(int(100 * (float(current_done) / float(nbr_files)))) + " % done")
            current_done += 1

            file_path = input_path + file_name

            result_string = ""
            result_string += file_name
            result_string += ", "

            # parity game analysis
            print("parity")
            pg_file_path = file_path + ".pg"

            if stat(pg_file_path).st_size != 0:
                pg_size, _ = get_game_size(pg_file_path)
            else:
                pg_size = "NOT GEN"

            result_string += str(pg_size)
            result_string += ", "

            realizability = []

            if pg_size != "NOT GEN":
                print("    regular")
                won_player_0_reg, time_reg, parity_winning_0_reg, parity_winning_1_reg = solve_pg_regular(pg_file_path,
                                                                                                          timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "

                print("    regular partial")
                won_player_0_reg_par, time_reg_par, parity_winning_0_reg_par, parity_winning_1_reg_par = solve_pg_regular_partial(
                    pg_file_path, timeout)
                realizability.append(won_player_0_reg_par)
                result_string += str(time_reg_par)
                result_string += ", "

                print("    bdd")
                won_player_0_bdd, time_bdd, parity_winning_0_bdd, parity_winning_1_bdd = solve_pg_bdd(pg_file_path,
                                                                                                      timeout)
                realizability.append(won_player_0_bdd)
                result_string += str(time_bdd)
                result_string += ", "

                print("    bdd partial charly")
                won_player_0_bdd_par_cha, time_bdd_par_cha, parity_winning_0_bdd_par_cha, parity_winning_1_bdd_par_cha = solve_pg_bdd_partial(pg_file_path, timeout)
                realizability.append(won_player_0_bdd_par_cha)
                result_string += str(time_bdd_par_cha)
                result_string += ", "

                print("    bdd partial clem")
                won_player_0_bdd_par_clem, time_bdd_par_clem, parity_winning_0_bdd_par_clem, parity_winning_1_bdd_par_clem = solve_pg_bdd_partial_debug(
                    pg_file_path, timeout)
                realizability.append(won_player_0_bdd_par_clem)
                result_string += str(time_bdd_par_clem)
                result_string += ", "

                if check_solution:
                    # checking all results between them

                    pg_regions_reg = [(parity_winning_0_reg, parity_winning_1_reg),
                                  (parity_winning_0_reg_par, parity_winning_1_reg_par)]

                    pg_real_reg = [won_player_0_reg, won_player_0_reg_par]

                    check_consistency_regular(pg_regions_reg, pg_real_reg, True, pg_file_path)

                    pg_regions_bdd = [(parity_winning_0_bdd, parity_winning_1_bdd),
                                  (parity_winning_0_bdd_par_cha, parity_winning_1_bdd_par_cha),
                                      (parity_winning_0_bdd_par_clem, parity_winning_1_bdd_par_clem)]

                    pg_real_bdd = [won_player_0_bdd, won_player_0_bdd_par_cha, won_player_0_bdd_par_clem]

                    check_consistency_bdd(pg_regions_bdd, pg_real_bdd, True, pg_file_path)

            else:
                result_string += pg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += pg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += pg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += pg_size
                result_string += ", "
                realizability.append("NOT GEN")

                result_string += pg_size
                result_string += ", "
                realizability.append("NOT GEN")

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

                """
                print("    regular c")
                won_player_0_reg, time_reg = solve_gpg_regular_c(gpg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "
                """

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

                """
                print("    bdd c")
                won_player_0_reg, time_reg = solve_gpg_bdd_c(gpg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "
                """

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

                """
                result_string += gpg_size
                result_string += ", "

                result_string += gpg_size
                result_string += ", "
                """
            for realized in realizability:
                result_string += str(realized)
                result_string += ", "

            result_string += " \n"

            f.write(result_string)

        f.close()


compare_all_files(tlsf_and_games, comparison_file_name, out)
