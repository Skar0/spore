from collections import defaultdict
import bdd.arena as ar
import bdd.misc


def pg2bdd(pg_path, manager):
    """
    Loads a parity game from file and represent it as a Binary Decision Diagram (BDD).
    :param pg_path: path to the .pg file containing a parity game in PGSolver format
    :type pg_path: str
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: an arena object for the arena provided in the file and a list of its vertices represented by BDDs
    :rtype: Arena, list of dd.cudd.Function
    """

    # open file
    with open(pg_path, "r") as pg_file:

        # first line has max index for vertices; vertices index starts at 0
        info_line = pg_file.readline().rstrip().split(" ")

        max_index = int(info_line[1][:-1])

        nbr_digits_vertices = len(bin(max_index)) - 2  # binary representation is prefixed by '0b'

        # init BDD variables
        vars = ['x{i}'.format(i=j) for j in range(nbr_digits_vertices)]  # variables to encode the vertices
        vars_bis = ['xb{i}'.format(i=j) for j in range(nbr_digits_vertices)]
        all_vars = vars + vars_bis
        manager.declare(*all_vars)
        mapping_bis = dict(zip(vars, vars_bis))
        inv_mapping_bis = dict(zip(vars_bis, vars))

        # init the BDDs
        player0_vertices = manager.false  # BDD for vertices of Player 0
        player1_vertices = manager.false  # BDD for vertices of Player 1
        edges = manager.false  # BDD for edges
        # dictionary with BDD as key created on call (to avoid creating a BDD for non-existing priorities)
        priorities = defaultdict(lambda: manager.false)
        all_vertices = [None for _ in range(max_index + 1)]

        # all possible variables assignments of var (not yielded in order)
        all_possibilities = manager.pick_iter(manager.true, vars)

        # iterate over vertices in the file
        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            prio = int(infos[1])
            player = int(infos[2])

            # current BDD for the vertex
            vertex_dict = next(all_possibilities)  # dictionary encoding the valuation corresponding to the vertex
            vertex_bdd = manager.cube(vertex_dict)  # create a BDD node for this valuation
            # TODO we need to remember the correspondence between BDD node and vertex for later

            # add current node to all nodes at the correct index
            all_vertices[index] = vertex_bdd

            # add vertex to the formula for correct priority
            priorities[prio] = priorities[prio] | vertex_bdd

            # add vertex to correct player vertex BDD, 0 evaluates as false and 1 as true
            if player:
                player1_vertices = player1_vertices | vertex_bdd
            else:
                player0_vertices = player0_vertices | vertex_bdd

        pg_file.seek(0)  # go back to first line of the file
        pg_file.readline()  # first line has special info, pass it

        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])

            for succ in infos[3].split(","):
                successor = int(succ)
                edges = edges | (all_vertices[index] & manager.let(mapping_bis, all_vertices[successor]))

        # create an Arena object and fill it in
        arena = ar.Arena()
        arena.vars = vars
        arena.vars_bis = vars_bis
        arena.all_vars = all_vars
        arena.mapping_bis = mapping_bis
        arena.inv_mapping_bis = inv_mapping_bis

        arena.nbr_vertices = max_index + 1
        arena.nbr_digits_vertices = nbr_digits_vertices
        arena.nbr_functions = 1

        arena.player0_vertices = player0_vertices
        arena.player1_vertices = player1_vertices
        arena.edges = edges
        arena.priorities = priorities

        return arena, all_vertices


def pg2bdd_direct_encoding(pg_path, manager):
    """
    Loads a parity game from file and represent it as a Binary Decision Diagram (BDD). The encoding of vertices from the
    game arena is done using a direct encoding. That is, a vertex v is represented by its binary encoding expressed as
    an assignment of the variables in the BDD. Function pg2bdd does not apply this encoding and rather uses a random
    assignment of the variables to represent each vertex, which performs better. It is however possible to consider this
    random assignment as a binary encoding, we just need to consider a specific order of the variables which is not the
    intended one (that is, x1 might represent bit number 3 of the encoding and so on).
    :param pg_path: path to the .pg file containing a parity game in PGSolver format
    :type pg_path: str
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: an arena object for the arena provided in the file and a list of its vertices represented by BDDs
    :rtype: Arena, list of dd.cudd.Function
    """

    # open file
    with open(pg_path, "r") as pg_file:

        # first line has max index for vertices; vertices index starts at 0
        info_line = pg_file.readline().rstrip().split(" ")

        max_index = int(info_line[1][:-1])

        nbr_digits_vertices = len(bin(max_index)) - 2  # binary representation is prefixed by '0b'

        # init BDD variables
        vars = ['x{i}'.format(i=j) for j in range(nbr_digits_vertices)]  # variables to encode the vertices
        vars_bis = ['xb{i}'.format(i=j) for j in range(nbr_digits_vertices)]
        all_vars = vars + vars_bis
        manager.declare(*all_vars)
        mapping_bis = dict(zip(vars, vars_bis))
        inv_mapping_bis = dict(zip(vars_bis, vars))

        # init the BDDs
        player0_vertices = manager.false  # BDD for vertices of Player 0
        player1_vertices = manager.false  # BDD for vertices of Player 1
        edges = manager.false  # BDD for edges
        # dictionary with BDD as key created on call (to avoid creating a BDD for non-existing priorities)
        priorities = defaultdict(lambda: manager.false)
        all_vertices = [None for _ in range(max_index + 1)]

        # iterate over vertices in the file
        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            prio = int(infos[1])
            player = int(infos[2])

            # dictionary encoding the valuation corresponding to the vertex
            vertex_dict = bdd.misc.int2dict(index, vars)
            vertex_bdd = manager.cube(vertex_dict)  # create a BDD node for this valuation

            # add vertex to the formula for correct priority
            priorities[prio] = priorities[prio] | vertex_bdd

            # add vertex to correct player vertex BDD, 0 evaluates as false and 1 as true
            if player:
                player1_vertices = player1_vertices | vertex_bdd
            else:
                player0_vertices = player0_vertices | vertex_bdd

        pg_file.seek(0)  # go back to first line of the file
        pg_file.readline()  # first line has special info, pass it

        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])

            # TODO we use the encoding from int to test node in order to get a vertex and add it to the BDD
            # TODO remembering created BDD nodes in a list like previously could be more efficient
            # TODO does re-declaring the BDD node for a vertex using manager.cube work ? Or does it need to be the
            #  previously declared node ?

            for succ in infos[3].split(","):
                successor = int(succ)
                index_bdd = manager.cube(bdd.misc.int2dict(index, vars))
                succ_bdd = manager.let(mapping_bis, manager.cube(bdd.misc.int2dict(successor, vars)))

                edges = edges | (index_bdd & succ_bdd)

        # create an Arena object and fill it in
        arena = ar.Arena()
        arena.vars = vars
        arena.vars_bis = vars_bis
        arena.all_vars = all_vars
        arena.mapping_bis = mapping_bis
        arena.inv_mapping_bis = inv_mapping_bis

        arena.nbr_vertices = max_index + 1
        arena.nbr_digits_vertices = nbr_digits_vertices
        arena.nbr_functions = 1

        arena.player0_vertices = player0_vertices
        arena.player1_vertices = player1_vertices
        arena.edges = edges
        arena.priorities = priorities

        return arena, all_vertices
