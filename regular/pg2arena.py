from collections import defaultdict
from regular.arena import Arena


def pg2arena(pg_path, is_gpg=True):
    """
    Loads a parity game from file and represent it as an Arena object.
    :param pg_path: path to the .pg file containing a parity game in PGSolver format
    :type pg_path: str
    :param is_gpg: whether the file is in generalized parity extended PGSolver format
    :type is_gpg: bool
    :return: an arena object for the arena provided in the file
    :rtype: Arena
    """

    # open file
    with open(pg_path, "r") as pg_file:

        info_line = pg_file.readline().rstrip().split(" ")

        if is_gpg:
            # first line has max index for vertices and number of priority functions; function and index start at 0
            max_index = int(info_line[1])
            nbr_functions = int(info_line[2][:-1])
        else:
            # first line has max index for vertices; index start at 0
            max_index = int(info_line[1][:-1])

        nbr_vertices = max_index + 1

        vertices = []
        player = defaultdict(lambda: -1)
        priorities = [defaultdict(lambda: [])]
        vertex_priorities = defaultdict(lambda: [])
        successors = defaultdict(lambda: [])
        predecessors = defaultdict(lambda: [])

        # iterate over vertices in the file
        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            prio = int(infos[1])
            vertex_player = int(infos[2])

            vertices.append(index)

            player[index] = vertex_player

            priorities[0][prio].append(index)

            vertex_priorities[index] = [prio]

            for succ in infos[3].split(","):
                successor = int(succ)
                successors[index].append(successor)
                predecessors[successor].append(index)

        arena = Arena()

        arena.nbr_vertices = nbr_vertices
        arena.nbr_functions = 1

        arena.vertices = vertices
        arena.player = player
        arena.priorities = priorities
        arena.vertex_priorities = vertex_priorities
        arena.successors = successors
        arena.predecessors = predecessors

        return arena
