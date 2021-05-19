from collections import defaultdict

class Arena:
    """
    Class used to represent a game arena. Internally, the arena is represented using lists and dictionaries.
    """

    def __init__(self):

        # classical arena information
        self.nbr_vertices = 0           # type: int
        self.nbr_functions = 1          # type: int
 
        # list of all vertices 
        self.vertices = None            # type: list[int]
        # defaultdict of int (vertex): int (player for that vertex)
        self.player = None              # type: defaultdict[int, int]
        # list of defaultdict of int (priority): list of int (vertices of that priority)
        self.priorities = None          # type: defaultdict[int, list[int]]
        # defaultdict of int (vertex): list of int (priorities for that vertex)
        self.vertex_priorities = None   # type: defaultdict[int, list[int]]
        # defaultdict of int (vertex): list of int (successors)
        self.successors = None          # type: defaultdict[int, list[int]]
        # defaultdict of int (vertex): list of int (predecessors)
        self.predecessors = None        # type: defaultdict[int, list[int]]

    def subarena(self, removed):
        """
        Creates a sub-arena of the current arena by only keeping vertices not present in the provided set.
        :param removed: vertices to be removed from the current arena
        :type removed: list of int
        :return: a new arena corresponding to the sub-arena
        :rtype: Arena
        """
        cdef int nbr_vertices, nbr_functions
        cdef list vertices
        cdef dict player

        nbr_vertices = 0
        nbr_functions = self.nbr_functions

        vertices = []
        player = <dict>defaultdict(lambda: -1)
        priorities = [defaultdict(lambda: []) for _ in range(nbr_functions)]
        vertex_priorities = <dict>defaultdict(lambda: [])
        successors = <dict>defaultdict(lambda: [])
        predecessors = <dict>defaultdict(lambda: [])

        for vertex in self.vertices:
            # for each remaining vertex
            if vertex not in removed:

                nbr_vertices += 1
                vertices.append(vertex)
                player[vertex] = self.player[vertex]

                # for each function, add this vertex to the correct set of vertices for the corresponding priority
                for func in range(nbr_functions):
                    priorities[func][self.vertex_priorities[vertex][func]].append(vertex)

                vertex_priorities[vertex] = self.vertex_priorities[vertex]

                for succ in self.successors[vertex]:
                    if succ not in removed:
                        successors[vertex].append(succ)
                        predecessors[succ].append(vertex)

        subarena = Arena()

        subarena.nbr_vertices = nbr_vertices
        subarena.nbr_functions = nbr_functions

        subarena.vertices = vertices
        subarena.player = player
        subarena.priorities = priorities
        subarena.vertex_priorities = vertex_priorities
        subarena.successors = successors
        subarena.predecessors = predecessors

        return subarena
