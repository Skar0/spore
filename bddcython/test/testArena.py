import unittest
import dd.cudd as _bdd
from collections import defaultdict

from bdd import gpg2bdd
from bdd.misc import bdd2int
from bdd.pg2bdd import pg2bdd


def retrieve_expected_pg_arena(path):
    # open file
    with open(path, "r") as pg_file:

        info_line = pg_file.readline()  # first line has max index for vertices, vertices index start at 0

        max_index = int(info_line.rstrip().split(" ")[1][:-1])

        nbr_vertices = max_index + 1

        expected_arena = [[], [], [], []]  # vertices of player 0, vertices of player 1, priorities, successors

        expected_arena[0] = []

        expected_arena[1] = []

        expected_arena[2] = defaultdict(lambda: [])

        expected_arena[3] = [[] for _ in range(nbr_vertices)]

        # iterate over vertices
        for line in pg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            priority = int(infos[1])
            player = int(infos[2])
            successors = [int(succ) for succ in infos[3].split(",")]

            expected_arena[2][priority].append(index)

            expected_arena[3][index].extend(successors)

            if not player:
                expected_arena[0].append(index)
            else:
                expected_arena[1].append(index)

        return expected_arena


def retrieve_expected_gpg_arena(path):
    # open file
    with open(path, "r") as gpg_file:

        # first line has max index for vertices and number of priority functions; vertices and function index start at 0
        info_line = gpg_file.readline().rstrip().split(" ")

        max_index = int(info_line[1])

        nbr_functions = int(info_line[2][:-1])

        nbr_vertices = max_index + 1

        expected_arena = [[], [], [], []]  # vertices of player 0, vertices of player 1, priorities, successors

        expected_arena[0] = []

        expected_arena[1] = []

        expected_arena[2] = [defaultdict(lambda: []) for _ in range(nbr_functions)]

        expected_arena[3] = [[] for _ in range(nbr_vertices)]

        # iterate over vertices
        for line in gpg_file:
            infos = line.rstrip().split(" ")  # strip line to get info
            index = int(infos[0])
            priority = [int(p) for p in infos[1].split(",")]
            player = int(infos[2])
            successors = [int(succ) for succ in infos[3].split(",")]

            for func in range(len(priority)):
                expected_arena[2][func][priority[func]].append(index)

            expected_arena[3][index].extend(successors)

            if not player:
                expected_arena[0].append(index)
            else:
                expected_arena[1].append(index)

        return expected_arena


class TestArena(unittest.TestCase):
    """
    Test cases for arenas encoded as BDDs.
    """

    def setUp(self):
        self.pg_test_files_path = "./arenas/pg/"
        self.pg_test_files = ["example_1.pg", "example_2.pg", "example_3.pg", "example_4.pg",
                              "example_5.pg"]
        self.pg_expected_values = [] * len(self.pg_test_files)

        self.gpg_test_files_path = "./arenas/gpg/"
        self.gpg_test_files = ["example_1.gpg", "example_2.gpg", "example_3.gpg", "example_4.gpg", "example_1_pg.gpg",
                               "example_2_pg.gpg", "example_3_pg.gpg", "example_4_pg.gpg", "example_5_pg.gpg"]
        self.gpg_expected_values = [] * len(self.gpg_test_files)

    def test_pg_arena_creation(self):
        """
        Check if arenas are correctly loaded from files.
        """

        for file in self.pg_test_files:

            file_path = self.pg_test_files_path + file

            manager = _bdd.BDD()

            # load arena and get number of vertices
            arena, vertices_bdd = pg2bdd(file_path, manager, is_gpg=False)

            nbr_vertices = len(vertices_bdd)

            expected_arena = retrieve_expected_pg_arena(file_path)

            self.assertEqual(arena.nbr_functions, 1)

            actual_player0 = set(bdd2int(arena.player0_vertices, arena.vars, manager, mapping=vertices_bdd))

            expected_player0 = set(expected_arena[0])

            self.assertEqual(expected_player0, actual_player0)

            actual_player1 = set(bdd2int(arena.player1_vertices, arena.vars, manager, mapping=vertices_bdd))

            expected_player1 = set(expected_arena[1])

            self.assertEqual(expected_player1, actual_player1)

            for priority, s in expected_arena[2].items():
                actual_priority = set(bdd2int(arena.priorities[0][priority], arena.vars, manager,
                                                    mapping=vertices_bdd))

                expected_priority = set(s)

                self.assertEqual(expected_priority, actual_priority)

            for index in range(nbr_vertices):
                vertex_encoding = vertices_bdd[index]  # BDD encoding of the vertex

                edges_vertex = vertex_encoding & arena.edges

                edges_vertex = manager.exist(arena.vars, edges_vertex)

                edges_vertex = manager.let(arena.inv_mapping_bis, edges_vertex)

                actual_successors = set(bdd2int(edges_vertex, arena.vars, manager,
                                                      mapping=vertices_bdd))

                expected_successors = set(expected_arena[3][index])

                self.assertEqual(expected_successors, actual_successors)

    def test_gpg_arena_creation(self):
        """
        Check if arenas are correctly loaded from files.
        """

        for file in self.gpg_test_files:

            file_path = self.gpg_test_files_path + file

            manager = _bdd.BDD()

            # load arena and get number of vertices
            arena, vertices_bdd = gpg2bdd.gpg2bdd(file_path, manager)

            nbr_vertices = len(vertices_bdd)

            expected_arena = retrieve_expected_gpg_arena(file_path)

            self.assertEqual(arena.nbr_functions, len(expected_arena[2]))

            actual_player0 = set(bdd2int(arena.player0_vertices, arena.vars, manager, mapping=vertices_bdd))

            expected_player0 = set(expected_arena[0])

            self.assertEqual(expected_player0, actual_player0)

            actual_player1 = set(bdd2int(arena.player1_vertices, arena.vars, manager, mapping=vertices_bdd))

            expected_player1 = set(expected_arena[1])

            self.assertEqual(expected_player1, actual_player1)

            for func in range(arena.nbr_functions):
                for priority, s in expected_arena[2][func].items():
                    actual_priority = set(bdd2int(arena.priorities[func][priority], arena.vars, manager,
                                                        mapping=vertices_bdd))

                    expected_priority = set(s)

                    self.assertEqual(expected_priority, actual_priority)

            for index in range(nbr_vertices):
                vertex_encoding = vertices_bdd[index]  # BDD encoding of the vertex

                edges_vertex = vertex_encoding & arena.edges

                edges_vertex = manager.exist(arena.vars, edges_vertex)

                edges_vertex = manager.let(arena.inv_mapping_bis, edges_vertex)

                actual_successors = set(bdd2int(edges_vertex, arena.vars, manager,
                                                      mapping=vertices_bdd))

                expected_successors = set(expected_arena[3][index])

                self.assertEqual(expected_successors, actual_successors)


if __name__ == '__main__':
    unittest.main()
