from collections import defaultdict
import arena as ar


def gpg2arena(gpg_path):
    """
    Loads a generalized parity game from file and represent it as an Arena object.
    :param gpg_path: path to the .gpg file containing a generalized parity game in extended PGSolver format
    :type gpg_path: str
    :return: an arena object for the arena provided in the file
    :rtype: Arena
    """

    # open file
    with open(gpg_path, "r") as gpg_file:

        # first line has max index for vertices and number of priority functions; vertices and function index start at 0
        info_line = gpg_file.readline().rstrip().split(" ")

        max_index = int(info_line[1])

        nbr_functions = int(info_line[2][:-1])

        nbr_vertices = max_index + 1

        vertices = []
        player = defaultdict(lambda: -1)
        priorities = [defaultdict(lambda: []) for _ in range(nbr_functions)]
        vertex_priorities = defaultdict(lambda: [])
        successors = defaultdict(lambda: [])
        predecessors = defaultdict(lambda: [])

        # iterate over vertices in the file
        for line in gpg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            prios = [int(p) for p in infos[1].split(",")]
            vertex_player = int(infos[2])

            vertices.append(index)
            player[index] = vertex_player

            for func in range(nbr_functions):
                priorities[func][prios[func]].append(index)

            vertex_priorities[index] = prios

            for succ in infos[3].split(","):
                successor = int(succ)
                successors[index].append(successor)
                predecessors[successor].append(index)

        arena = ar.Arena()

        arena.nbr_vertices = nbr_vertices
        arena.nbr_functions = nbr_functions

        arena.vertices = vertices
        arena.player = player
        arena.priorities = priorities
        arena.vertex_priorities = vertex_priorities
        arena.successors = successors
        arena.predecessors = predecessors

        return arena
