from collections import defaultdict, deque


def count_outgoing_edges(arena, player):
    """
    Computes the number of outgoing edges for each vertex of player in the arena.
    :param arena: the arena
    :type arena: Arena
    :param player: the player whose vertices are considered
    :type player: int
    :return: a dictionary where keys are nodes and values are the number of outgoing edges of that node.
    :rtype: defaultdict of int: int
    """
    cdef int vertex
    cdef dict nbr_outgoing_edges

    nbr_outgoing_edges = <dict>defaultdict(int)

    for vertex in arena.vertices:
        if arena.player[vertex] == player:
            nbr_outgoing_edges[vertex] = len(arena.successors[vertex])

    return nbr_outgoing_edges


def attractor(arena, s, player):
    """
    Computes the attractor of set s for player in the arena.
    :param arena: the arena in which we compute the attractor
    :type arena: Arena
    :param s: the set for which we compute the attractor
    :type s: list of int
    :param player: the player for which we compute the attractor
    :type player: int
    :return: the computed attractor
    :rtype: list of int
    """
    cdef int opponent, vertex, current_vertex, pred
    # cdef list queue     # To correctly "cast" to deque, we need to use C++ bindings
    cdef dict visited, nbr_outgoing_edges
    cdef list attractor

    opponent = 0 if player else 1  # opponent is 0 if player is 1

    # TODO check the collections used here (queue with append and list with append)
    nbr_outgoing_edges = <dict>count_outgoing_edges(arena, opponent)

    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)

    # dictionary used to check if a vertex has been visited without iterating over the attractor (in O(1) on average)
    visited = <dict>defaultdict(lambda: 0)

    attractor = []  # the attractor

    # for each vertex in the set s
    for vertex in s:
        queue.append(vertex)  # add vertex to the end of the queue
        visited[vertex] = 1  # mark vertex as visited
        attractor.append(vertex)  # add vertex to the attractor

    # while queue is not empty
    while queue:

        current_vertex = queue.popleft()  # remove and return vertex on the left side of the queue (first in, first out)

        # iterating over the predecessors of current_vertex
        for pred in arena.predecessors[current_vertex]:

            if visited[pred] == 0:  # if pred is not yet visited, its visited value is 0 by default

                if arena.player[pred] == player:

                    # belongs to player, mark as visited, add to queue and attractor
                    queue.append(pred)
                    visited[pred] = 1
                    attractor.append(pred)

                else:

                    # belongs to opponent, decrement nbr_outgoing_edges. If nbr_outgoing_edges is 0, add to attractor
                    nbr_outgoing_edges[pred] -= 1

                    if nbr_outgoing_edges[pred] == 0:
                        queue.append(pred)
                        visited[pred] = 1
                        attractor.append(pred)

    return attractor
