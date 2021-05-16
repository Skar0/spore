from collections import defaultdict
import arena as ar


def gpg2bdd(gpg_path, manager):
    """
    Encode a generalized parity game in extended PGsolver file format into a Binary Decision Diagram (BDD) using the
    dd library.
    :param gpg_path: path to the generalized parity game in extended PGsolver file
    :param manager: the BDD manager
    :return: a bdd representation of the generalized parity game in the file gpg_path
    """

    # open file
    with open(gpg_path, "r") as gpg_file:

        # first line has max index for vertices and number of coloring functions, vertices and function index start at 0
        info_line = gpg_file.readline().rstrip().split(" ")

        max_index = int(info_line[1])

        nbr_functions = int(info_line[2][:-1])

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
        edges = manager.false  # BDD for edge relation
        # dictionary with BDD as key created on call (to avoid creating a BDD for non-existing colors)
        colors = [defaultdict(lambda: manager.false) for _ in range(nbr_functions)]  # function indexing starts at 0
        all_vertices = [None for _ in range(max_index + 1)]

        # all possible variables assignments of var (not in order)
        all_possibilities = manager.pick_iter(manager.true, vars)

        # iterate over nodes
        for line in gpg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            priorities = [int(p) for p in infos[1].split(",")]
            player = int(infos[2])

            # current bdd for the node
            vertex_dict = next(all_possibilities)  # dictionary encoding the valuation corresponding to the vertex
            vertex_bdd = manager.cube(vertex_dict)  # create a BDD node for this valuation

            # TODO we might need to remember the correspondence to later decide whether vertex 0 is won by Player 0

            # add current node to all nodes
            all_vertices[index] = vertex_bdd

            # add vertex to the formula for correct color and correct function
            for func in range(nbr_functions):
                colors[func][priorities[func]] = colors[func][priorities[func]] | vertex_bdd

            # add vertex to correct player vertex BDD, 0 evaluates as false and 1 as true
            if player:
                player1_vertices = player1_vertices | vertex_bdd
            else:
                player0_vertices = player0_vertices | vertex_bdd

        gpg_file.seek(0)  # go back to first line
        gpg_file.readline()  # first line has special info

        for line in gpg_file:
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
        arena.nbr_functions = nbr_functions

        arena.player0_vertices = player0_vertices
        arena.player1_vertices = player1_vertices
        arena.edges = edges
        arena.colors = colors

        return arena
