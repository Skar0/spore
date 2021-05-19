from collections import defaultdict


class Arena:
    """
    Class used to represent a game arena. Internally, the arena is represented by Binary Decision Diagrams (BDD).
    """

    def __init__(self):

        # storing all variables and mappings needed for BDD operations
        self.vars = None
        self.vars_bis = None
        self.all_vars = None # TODO check if actually used
        self.mapping_bis = None
        self.inv_mapping_bis = None

        # classical arena information, with the addition of the number of bits required for a binary representation
        self.nbr_vertices = 0
        self.nbr_digits_vertices = 0
        self.nbr_functions = 1

        # classical arena information
        self.player0_vertices = None # TODO check if a BDD for all vertices is required
        self.player1_vertices = None
        self.edges = None
        self.priorities = None  # priorities[i] yields the ith priority function in a generalized parity game arena

    def subarena(self, vertices, manager):
        """
        Creates a sub-arena of the current arena by only keeping a provided set of vertices.
        :param vertices: the vertices to be kept in the sub-arena
        :type vertices: dd.cudd.Function
        :param manager: the BDD manager
        :type manager: dd.cudd.BDD
        :return: the sub-arena
        :rtype: Arena
        """

        edges_subarena = self.edges & vertices & manager.let(self.mapping_bis, vertices)
        player0_vertices_subarena = self.player0_vertices & vertices
        player1_vertices_subarena = self.player1_vertices & vertices
        priorities_subarena = [defaultdict(lambda: manager.false) for _ in range(self.nbr_functions)]

        # TODO check for optimization
        for function_index in range(self.nbr_functions):
            for priority, bdd in self.priorities[function_index].items():
                new_priority_bdd = bdd & (player1_vertices_subarena | player0_vertices_subarena)
                if not new_priority_bdd == manager.false:
                    priorities_subarena[function_index][priority] = new_priority_bdd

        subarena = Arena()
        subarena.vars = self.vars
        subarena.vars_bis = self.vars_bis
        subarena.all_vars = self.all_vars
        subarena.mapping_bis = self.mapping_bis
        subarena.inv_mapping_bis = self.inv_mapping_bis

        # TODO check if retaining the number of vertices in sub-games is required
        # subarena.nbr_vertices = ?

        subarena.nbr_digits_vertices = self.nbr_digits_vertices
        subarena.nbr_functions = self.nbr_functions

        subarena.player0_vertices = player0_vertices_subarena
        subarena.player1_vertices = player1_vertices_subarena
        subarena.edges = edges_subarena
        subarena.priorities = priorities_subarena

        return subarena
