from os import listdir, stat
import signal
from contextlib import contextmanager
import time
import dd.cudd as _bdd

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


# path to the directory which contains all tlsf files and all generated (empty or not) files
tlsf_and_games = "csv/tlsf-after-2min-added-gen-fater-20/"

# name for the .csv file containing the comparison between the running times
comparison_file_name = "friday.csv"

# timeout value for the algorithms
out = 5


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


# from https://www.jujens.eu/posts/en/2018/Jun/02/python-timeout-function/#:~:text=You%20can%20use%20signals%20and,alarm%20signal%20for%20the%20timeout.&text=Even%20if%20this%20solution%20works,which%20can%20be%20a%20problem.


@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except Exception:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise Exception


def solve_pg_regular(pg_path, timeout_value):
    """
    Load and solve the parity game whose path is provided in parameter using the regular implementation.
    """

    player0_won = "TIMEOUT"

    start_time = time.time()

    with timeout(timeout_value):

        arena = reg_pg_loader.pg2arena(pg_path)
        winning_0, winning_1 = reg_pg_recursive.recursive(arena)
        player0_won = 0 in winning_0

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time


def solve_pg_bdd(pg_path, timeout_value):
    """
    Load and solve the parity game whose path is provided in parameter using the bdd implementation.
    """

    player0_won = "TIMEOUT"

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

    return player0_won, end_time


def solve_gpg_regular(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation.
    """

    player0_won = "TIMEOUT"

    start_time = time.time()

    with timeout(timeout_value):
        arena = reg_gpg_loader.gpg2arena(gpg_path)
        winning_0, winning_1 = reg_gpg_recursive.generalized_recursive(arena)
        player0_won = 0 in winning_0

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time


def solve_gpg_regular_c(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation.
    """

    player0_won = "TIMEOUT"

    start_time = time.time()

    with timeout(timeout_value):
        arena = reg_c_gpg_loader.gpg2arena(gpg_path)
        winning_0, winning_1 = reg_c_gpg_recursive.generalized_recursive(arena)
        player0_won = 0 in winning_0

    end_time = "%.5f" % (time.time() - start_time)

    if player0_won == "TIMEOUT":
        end_time = "TIMEOUT"

    return player0_won, end_time


def solve_gpg_bdd(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation.
    """

    player0_won = "TIMEOUT"

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

    return player0_won, end_time


def solve_gpg_bdd_c(gpg_path, timeout_value):
    """
    Load and solve the generalized parity game whose path is provided in parameter using the regular implementation.
    """

    player0_won = "TIMEOUT"

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

    return player0_won, end_time


def get_game_size(path):

    with open(path, "r") as game_file:

        # first line has max index for vertices and number of priority functions; vertices and function index start at 0
        info_line = game_file.readline().rstrip().split(" ")

        max_index = int(info_line[1])

        nbr_functions = int(info_line[2][:-1])

        nbr_vertices = max_index + 1

    return nbr_vertices, nbr_functions


def compare_all_files(input_path, output_path, timeout):

    with open(output_path, "a") as f:

        f.write("FILE, "
                "PG SIZE, "
                "REG TIME, "
                "BDD TIME, "
                "GPG SIZE, "
                "GPG FUNC, "
                "REG TIME, "
                "REG C TIME, "
                "BDD TIME, "
                "BDD C TIME, "
                "REAL REG PG, "
                "REAL BDD PG, "
                "REAL REG GPG, "
                "REAL REG C GPG, "
                "REAL BDD GPG, "
                "REAL BDD C GPG, "
                "\n")

        at_least_one_non_empty = sorted(get_non_empty_tlsf(input_path))

        nbr_files = len(at_least_one_non_empty)

        current_done = 0

        for file_name in at_least_one_non_empty:

            print(" "* 10 + file_name + " "+str(int(100*(float(current_done) / float(nbr_files)))) + " % done")
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
                won_player_0_reg, time_reg = solve_pg_regular(pg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "

                print("    bdd")
                won_player_0_reg, time_reg = solve_pg_bdd(pg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "

            else:
                result_string += pg_size
                result_string += ", "

                result_string += pg_size
                result_string += ", "

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
                won_player_0_reg, time_reg = solve_gpg_regular(gpg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "

                print("    regular c")
                won_player_0_reg, time_reg = solve_gpg_regular_c(gpg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "

                print("    bdd")
                won_player_0_reg, time_reg = solve_gpg_bdd(gpg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "

                print("    bdd c")
                won_player_0_reg, time_reg = solve_gpg_bdd_c(gpg_file_path, timeout)
                realizability.append(won_player_0_reg)
                result_string += str(time_reg)
                result_string += ", "

            else:
                result_string += gpg_size
                result_string += ", "

                result_string += gpg_size
                result_string += ", "

                result_string += gpg_size
                result_string += ", "

                result_string += gpg_size
                result_string += ", "

            for realized in realizability:
                result_string += str(realized)
                result_string += ", "

            result_string += " \n"

            f.write(result_string)

        f.close()


compare_all_files(tlsf_and_games, comparison_file_name, out)