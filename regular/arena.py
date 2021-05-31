# -*- coding: utf-8 -*-
# SPORE: Symbolic Partial sOlvers for REalizability. 
# Copyright (C) 2021 - Charly Delfosse (University of Mons), Gaëtan Staquet (University of Mons), Clément Tamines (University of Mons)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from collections import defaultdict


class Arena:
    """
    Class used to represent a game arena. Internally, the arena is represented using lists and dictionaries.
    """

    def __init__(self):

        # classical arena information
        self.nbr_vertices = 0  # type: int
        self.nbr_functions = 1  # type: int

        # list of all vertices 
        self.vertices = None  # type: list[int]
        # defaultdict of int (vertex): int (player for that vertex)
        self.player = None  # type: defaultdict[int, int]
        # list of defaultdict of int (priority): list of int (vertices of that priority)
        self.priorities = None  # type: list[defaultdict[int, list[int]]]
        # defaultdict of int (vertex): list of int (priorities for that vertex)
        self.vertex_priorities = None  # type: defaultdict[int, list[int]]
        # defaultdict of int (vertex): list of int (successors)
        self.successors = None  # type: defaultdict[int, list[int]]
        # defaultdict of int (vertex): list of int (predecessors)
        self.predecessors = None  # type: defaultdict[int, list[int]]

    def subarena(self, removed):
        """
        Creates a sub-arena of the current arena by removing the vertices provided in the removed set (in practice, a
        new Arena object is created and the original arena remains unchanged).
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
