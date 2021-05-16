from collections import defaultdict
import arena as ar


def pg2bdd(pg_path, manager):
    """
    Encode a parity game in PGsolver file format into a Binary Decision Diagram (BDD) using the dd library.
    :param pg_path: path to the parity game in PGsolver file
    :param manager: the BDD manager
    :return: a bdd representation of the parity game in the file pg_path
    """

    # open file
    with open(pg_path, "r") as pg_file:

        info_line = pg_file.readline()  # first line has max index for vertices, vertices index start at 0

        max_index = int(info_line.rstrip().split(" ")[1][:-1])

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
        colors = defaultdict(lambda: manager.false)
        all_vertices = [None for _ in range(max_index + 1)]

        # all possible variables assignments of var (not in order)
        all_possibilities = manager.pick_iter(manager.true, vars)

        # iterate over nodes
        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            priority = int(infos[1])
            player = int(infos[2])

            # current bdd for the node
            vertex_dict = next(all_possibilities)  # dictionary encoding the valuation corresponding to the vertex
            vertex_bdd = manager.cube(vertex_dict)  # create a BDD node for this valuation

            # TODO we might need to remember the correspondence to later decide whether vertex 0 is won by Player 0

            # add current node to all nodes
            all_vertices[index] = vertex_bdd

            # add vertex to the formula for correct color
            colors[priority] = colors[priority] | vertex_bdd

            # add vertex to correct player vertex BDD, 0 evaluates as false and 1 as true
            if player:
                player1_vertices = player1_vertices | vertex_bdd
            else:
                player0_vertices = player0_vertices | vertex_bdd

        pg_file.seek(0)  # go back to first line
        pg_file.readline()  # first line has special info

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
        arena.colors = colors

        return arena


def int2bdd(index, vars, nbr_vars):
    """
    Transforms an index in base 10 into a dictionary of Booleans. Variable x0 is the most significant bit.
    :param index: the index in base 10
    :param vars: the variables declared in the bdd
    :param nbr_vars: number of variables declared
    :return: a dictionary of Booleans representing the binary encoding of index.
    """

    # TODO avoid conversion from str to in to bool, find a better way to create the dictionnary of booleans

    binary_representation = format(index,
                                   '0' + str(nbr_vars) + 'b')  # string containing the binary representation of index
    return {vars[i]: bool(int(binary_representation[i])) for i in range(nbr_vars)}


def bdd2int(dict_encoding, vars, nbr_vars):
    """
    Transforms a dictionary of Booleans into a base 10 number. Variable x0 is the most significant bit for the binary
    representation of the number in the dictionary.
    :param dict_encoding: dictionary encoding of the binary repreentation of the number
    :param vars: the variables declared in the bdd
    :param nbr_vars: number of variables declared
    :return: a base 10 number corresponding to the binary representation contained in the dictionary.
    """

    binary_representation = ""
    for i in range(nbr_vars):
        binary_representation = binary_representation + str(int(dict_encoding[vars[i]]))

    return int(binary_representation, 2)


def pg2bdd_direct_encoding(pg_path, manager):
    """
    Encode a parity game in PGsolver file format into a Binary Decision Diagram (BDD) using the dd library.
    The encoding of vertices from the graph is done using a direct encoding. That is, a vertex v is represented by its
    binary encoding expressed as an assignment of the variables in the BDD. Function pg2bdd does not apply this encoding
    and rather uses a random assignment of the variables to represent each vertex, which performs better. It is however
    possible to consider this random assignment as a binary encoding, we just need to consider a specific order of the
    variables which is not the intended one (that is, x1 might represent bit number 3 of the encoding and so on).
    :param pg_path: path to the parity game in PGsolver file
    :param manager: the BDD manager
    :return: a bdd representation of the parity game in the file pg_path
    """

    # open file
    with open(pg_path, "r") as pg_file:

        info_line = pg_file.readline()  # first line has max index for vertices, vertices index start at 0

        max_index = int(info_line.rstrip().split(" ")[1][:-1])

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
        colors = defaultdict(lambda: manager.false)
        all_vertices = [None for _ in range(max_index + 1)]

        # all possible variables assignments of var (not in order)
        all_possibilities = manager.pick_iter(manager.true, vars)

        # iterate over nodes
        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            priority = int(infos[1])
            player = int(infos[2])

            # current bdd for the node
            # dictionary encoding the valuation corresponding to the vertex
            vertex_dict = int2bdd(index, vars, nbr_digits_vertices)
            vertex_bdd = manager.cube(vertex_dict)  # create a BDD node for this valuation

            # add current node to all nodes
            all_vertices[index] = vertex_bdd

            # add vertex to the formula for correct color
            colors[priority] = colors[priority] | vertex_bdd

            # add vertex to correct player vertex BDD, 0 evaluates as false and 1 as true
            if player:
                player1_vertices = player1_vertices | vertex_bdd
            else:
                player0_vertices = player0_vertices | vertex_bdd

            # TODO we use the encoding from int to bdd node in order to get a vertex and add it to the BDD
            # TODO remembering created BDD nodes in a list like previously could be more efficient
            # TODO does re-declaring the BDD node for a vertex using manager.cube work ? Or does it need to be the
            #  previously declared node ?

            for succ in infos[3].split(","):
                successor = int(succ)
                edges = edges | (manager.cube(int2bdd(index, vars, nbr_digits_vertices)) &
                                 manager.let(mapping_bis, manager.cube(int2bdd(successor, vars, nbr_digits_vertices))))

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
        arena.colors = colors

        return arena
