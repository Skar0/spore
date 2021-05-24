from collections import defaultdict, deque


def count_outgoing_edges(arena, player):
    """
    Computes the number of outgoing edges for each vertex of player in the arena.
    :param arena: the arena
    :type arena: Arena
    :param player: the player whose vertices are considered
    :type player: int
    :return: a dictionary where a key is a vertex and the value is the number of outgoing edges of that vertex.
    :rtype: defaultdict of int: int
    """

    nbr_outgoing_edges = defaultdict(int)  # default value is zero for non-existing key

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

    opponent = 0 if player else 1  # opponent is 0 if player is 1

    nbr_outgoing_edges = count_outgoing_edges(arena, opponent)

    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)

    # dictionary used to check if a vertex has been visited without iterating over the attractor (in O(1) on average)
    visited = defaultdict(int)  # default value is zero for non-existing key

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

            if not visited[pred]:  # if pred is not yet visited, its visited value is 0 by default

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


def monotone_attractor(arena, s, priority, function):
    """
    Computes the monotone attractor of the target set, meaning the attractor without visiting bigger priorities than
    the one of the target set. Notice that s does not automatically belong to this monotone attractor.
    :param arena: the arena in which we compute the attractor
    :type arena: Arena
    :param s: the set for which we compute the attractor
    :type s: list of int
    :param priority: the priority of vertices in s
    :type priority: int
    :param function: the priority function we consider
    :type function: int
    :return: the computed attractor
    :rtype: list of int
    """

    player = priority % 2  # the player for which we compute the attractor
    opponent = 0 if player else 1  # opponent is 0 if player is 1

    nbr_outgoing_edges = count_outgoing_edges(arena, opponent)

    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)

    # dictionary used to check if a vertex has been visited without iterating over the attractor (in O(1) on average)
    visited = defaultdict(int)  # default value is zero for non-existing key

    attractor = []  # the attractor

    for vertex in s:
        queue.append(vertex)  # add vertex to the end of the queue

    # while queue is not empty
    while queue:

        current_vertex = queue.popleft()  # remove and return vertex on the left side of the queue (first in, first out)

        # iterating over the predecessors of current_vertex
        for pred in arena.predecessors[current_vertex]:

            # get pred info
            pred_player = arena.player[pred]
            pred_priority = arena.vertex_priorities[pred][function]

            if not visited[pred]:  # if pred is not yet visited, its visited value is 0 by default

                # if pred belongs to the correct player and its priority is lower or equal, add it
                if pred_player == player and pred_priority <= priority:

                    # if vertex has not been considered yet (not already been in the queue) add it
                    # this is to avoid considering the same vertex twice, which can happen only for the target vertices
                    # and can mess up the decrementing of the counters for vertices of the opponent
                    if pred not in s:
                        queue.append(pred)

                    # mark as visited, add to attractor
                    visited[pred] = 1
                    attractor.append(pred)

                # if pred belongs to the opposite player and its priority is lower or equal, check its counters
                elif pred_player == opponent and pred_priority <= priority:

                    # belongs to opponent, decrement nbr_outgoing_edges. If nbr_outgoing_edges is 0, add to attractor
                    nbr_outgoing_edges[pred] -= 1

                    if nbr_outgoing_edges[pred] == 0:

                        # if vertex has not been considered yet (not already been in the queue) add it
                        if pred not in s:
                            queue.append(pred)

                        # mark as visited, add to attractor
                        visited[pred] = 1
                        attractor.append(pred)

    return attractor


def safe_attractor(arena, s, avoid, player):
    """
    Computes the safe attractor of the target set, meaning the attractor without visiting a specific set of vertices.
    :param arena: the arena in which we compute the attractor
    :type arena: Arena
    :param s: the set for which we compute the attractor
    :type s: list of int
    :param avoid: the set of vertices to avoid
    :type avoid: list of int
    :param player: the player for which we compute the attractor
    :type player: int
    :return: the computed attractor
    :rtype: list of int
    """

    opponent = 0 if player else 1  # opponent is 0 if player is 1

    nbr_outgoing_edges = count_outgoing_edges(arena, opponent)

    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)

    # dictionary used to check if a vertex has been visited without iterating over the attractor (in O(1) on average)
    visited = defaultdict(int)  # default value is zero for non-existing key

    attractor = []  # the attractor

    # for vertices in s and not in avoid
    for vertex in set(s) - set(avoid):
        queue.append(vertex)  # add vertex to the end of the queue
        visited[vertex] = 1  # mark as visited
        attractor.append(vertex)  # add vertex to the attractor

    while queue:

        current_vertex = queue.popleft()  # remove and return vertex on the left side of the queue (first in, first out)

        # iterating over the predecessors of vertex current_vertex which are not in avoid
        for pred in set(arena.predecessors[current_vertex]) - set(avoid):

            if not visited[pred]:  # if pred is not yet visited, its visited value is 0 by default

                # get pred info
                pred_player = arena.player[pred]

                if pred_player == player:
                    # belongs to player
                    queue.append(pred)
                    visited[pred] = 1
                    attractor.append(pred)  # add pred to the attractor

                else:

                    # belongs to opponent
                    nbr_outgoing_edges[pred] -= 1

                    if nbr_outgoing_edges[pred] == 0:

                        queue.append(pred)
                        visited[pred] = 1
                        attractor.append(pred)  # add pred to the attractor

    return attractor
