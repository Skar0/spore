from collections import defaultdict
from typing import List, Any


class Arena:
    """
    Class used to represent a game arena. Internally, the arena is represented using lists and dictionaries.
    """
    nbr_vertices: int
    nbr_functions: int
    vertices: list[int]
    player: defaultdict[int, int]
    priorities: defaultdict[int, list[int]]
    vertex_priorities: defaultdict[int, list[int]]
    successors: defaultdict[int, list[int]]
    predecessors: defaultdict[int, list[int]]

    def __init__(self):

        # classical arena information
        self.nbr_vertices = 0
        self.nbr_functions = 1

        self.vertices = None  # list of all vertices
        self.player = None  # defaultdict of int (vertex): int (player for that vertex)
        self.priorities = None  # list of defaultdict of int (priority): list of int (vertices of that priority)
        self.vertex_priorities = None  # defaultdict of int (vertex): list of int (priorities for that vertex)
        self.successors = None  # defaultdict of int (vertex): list of int (successors)
        self.predecessors = None  # defaultdict of int (vertex): list of int (predecessors)

    def subarena(self, removed):
        """
        Creates a sub-arena of the current arena by only keeping vertices not present in the provided set.
        :param removed: vertices to be removed from the current arena
        :type removed: list of int
        :return: a new arena corresponding to the sub-arena
        :rtype: Arena
        """

        nbr_vertices = 0
        nbr_functions = self.nbr_functions

        vertices = []
        player = defaultdict(lambda: -1)
        priorities = [defaultdict(lambda: []) for _ in range(nbr_functions)]
        vertex_priorities = defaultdict(lambda: [])
        successors = defaultdict(lambda: [])
        predecessors = defaultdict(lambda: [])

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
