from collections import defaultdict


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
        p0_vertices = manager.false  # BDD for vertices of Player 0
        p1_vertices = manager.false  # BDD for vertices of Player 1
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
                p1_vertices = p1_vertices | vertex_bdd
            else:
                p0_vertices = p0_vertices | vertex_bdd

        pg_file.seek(0)  # go back to first line
        pg_file.readline()  # first line has special info

        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])

            for succ in infos[3].split(","):
                successor = int(succ)
                edges = edges | (all_vertices[index] & manager.let(mapping_bis, all_vertices[successor]))

        return p0_vertices, p1_vertices, edges, colors
