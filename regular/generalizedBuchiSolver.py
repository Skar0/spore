from regular.arena import Arena
from regular.attractor import monotone_attractor, attractor, safe_attractor


def generalized_buchi_inter_safety(arena, sets, avoid):
    """
    Computes the intersection of a generalized buchi and safety objectives.
    :param arena: the arena we consider
    :type arena: Arena
    @param sets: the sets for the generalized buchi objective
    @type sets: list of (list of int)
    @param avoid: set of vertices to avoid
    @type avoid: list of int
    @return: the vertices which satisfy the intersections
    @rtype: list of int
    """

    nbr_of_sets = len(sets)

    # this is a repeat until loop which creates a fixpoint
    while True:

        # for each set
        for l in range(nbr_of_sets):

            y = safe_attractor(arena, sets[l], avoid, 0)

            s = [vertex for vertex in arena.vertices if vertex not in y]

            if s:
                break  # we've found a dimension in which player can win

        d = attractor(arena, s, 1)

        # TODO this could be simplified
        sets[l] = list(set(sets[l]).intersection(set(arena.vertices)))

        arena = arena.subarena(d)

        if len(d) == 0:
            break

    return arena.vertices


def even_tuples_iterator(depth, priorities, sizes, li, k, t):
    """
    Iterate over the k-uples consisting of even priorities.
    :param depth:
    :type depth:
    :param priorities:
    :type priorities:
    :param sizes:
    :type sizes:
    :param li:
    :type li:
    :param k:
    :type k:
    :param t:
    :type t:
    """

    if depth == 0:
        yield [priorities[index][element] for index, element in enumerate(li)]

    else:
        for i in range(t, k):
            li[i] += 1
            if not li[i] >= sizes[i]:
                for j in even_tuples_iterator(depth - 1, priorities, sizes, li, k, i):
                    yield j
            li[i] -= 1


def generalized_buchi_partial_solver(arena, partial_winning_region_player0, partial_winning_region_player1):
    """
    Partial solver for generalized parity games using fatal attractors. Implementation using inline version of
    generalized buchi inter safety games.
    :param arena: the arena we consider
    :type arena: Arena
    :param partial_winning_region_player0: should be empty list when called
    :type partial_winning_region_player0: []
    :param partial_winning_region_player1: should be empty list when called
    :type partial_winning_region_player1: []
    :return: a partial solution sub-arena, partial_player0, partial_player1 in which sub-arena remains unsolved and
    partial_player0 (resp. partial_player1) is included in the winning region of player 0 (resp. player 1) in arena.
    :rtype: Arena, list of int, list of int
    """

    # base case : game is empty
    if arena.nbr_vertices == 0:
        return arena, partial_winning_region_player0, partial_winning_region_player1

    # retrieve useful information on the game
    priorities = [[] for _ in range(arena.nbr_functions)]  # list of list of priorities for each function
    even_priorities = [[] for _ in range(arena.nbr_functions)]  # list of list of even priorities for each function
    sizes = [0] * arena.nbr_functions  # sizes for the lists of priorities
    even_sizes = [0] * arena.nbr_functions  # sizes for the lists of even priorities
    empty_set = set()  # useful when computing fatal attractor for player 1

    # retrieve all priorities and put them in the lists of priorities for each function
    for func in range(arena.nbr_functions):
        priorities[func] = sorted(arena.priorities[func].keys(), reverse=True)
        even_priorities[func] = [prio for prio in priorities[func] if not (prio % 2)]

        # if there are no even priorities according to one of the functions, the game is completely won by player 1
        # return empty sub-game and all vertices added to partial_winning_region_player1
        if len(even_priorities[func]) == 0:
            partial_winning_region_player1.extend(arena.vertices)
            return Arena(), partial_winning_region_player0, partial_winning_region_player1

        sizes[func] = len(priorities[func])
        even_sizes[func] = len(even_priorities[func])

    # here we have sorted lists of priorities as well as their sizes

    indexes = [0] * arena.nbr_functions  # index for each function to go trough its priorities
    depth = 0  # depth is needed for the level of the lattice
    max_size = max(even_sizes)  # needed for the maximum level of the lattice

    # while we have not considered every couple of the lattice i.e. not reached the maximal depth for the levels in
    # the lattice for the even priorities or we have not considered every priority in the list of priorities
    while (not all(indexes[w] == sizes[w] for w in range(arena.nbr_functions))) or (depth != max_size + 2):

        # for each function, we treat odd priorities in order in the list until we have reached an even priority
        for i in range(arena.nbr_functions):

            # while we can advance in the list and we encounter an odd priority, we consider it
            while indexes[i] < sizes[i] and priorities[i][indexes[i]] % 2 == 1:

                # we have an odd priority to consider
                odd_priority = priorities[i][indexes[i]]

                # set of vertices of color 'odd_priority' according to function i
                target_set = set(arena.priorities[i][odd_priority])

                # perform fixpoint computation to find fatal attractor for player odd

                cache = set()

                while cache != target_set and target_set != empty_set:

                    cache = target_set

                    monotone_att = monotone_attractor(arena, target_set, odd_priority, i)

                    if target_set.issubset(monotone_att):

                        regular_att = attractor(arena, monotone_att, 1)

                        partial_winning_region_player1.extend(regular_att)

                        return generalized_buchi_partial_solver(arena.subarena(regular_att),
                                                                partial_winning_region_player0,
                                                                partial_winning_region_player1)

                    else:
                        target_set = target_set.intersection(monotone_att)

                # if we have not found a fatal attractor, we go forward in the list and restart the same logic until
                # reaching an even priority or the end of the list
                indexes[i] += 1

            # we have found an even priority at position indexes[i], at next iteration of the outer while, we restart
            # from the next index in the list
            if indexes[i] < sizes[i]:
                indexes[i] += 1

        # when this is reached, we know we have handled every odd priorities until reaching an even priority for each
        # function i.e. if [5,3,4,1,0] and [2,1,0] are the priorities, after first iteration of outer while we have
        # handled 5, 3 and reached 4 in the first list and reached 2 in the second (assuming there was no recursive
        # call after handling 5 and 3).

        # go through every k-uple of even priorities in the current level
        for kuple in even_tuples_iterator(depth, even_priorities, even_sizes, [0] * arena.nbr_functions,
                                          arena.nbr_functions, 0):

            # we now will compute a generalized buchi inter safety game
            avoid = []  # vertices for the safety game, to be avoided
            sets_gen = [[] for _ in range(arena.nbr_functions)]  # sets of vertices to be visited infinitely often

            for vertex in arena.vertices:

                flag = False  # is the vertex to be avoided (greater priority than required for some function)

                # for each function
                for func_index in range(arena.nbr_functions):

                    # priority of the vertex according to that function
                    prio = arena.vertex_priorities[vertex][func_index]

                    # priority is odd and greater than the corresponding one in the k-uple, we want to avoid the vertex
                    if prio % 2 == 1 and prio > kuple[func_index]:
                        flag = True
                    # else if the priority is the one we want to see, add it to the set to be visited infinitely often
                    elif prio == kuple[func_index]:
                        sets_gen[func_index].append(vertex)

                # if the flag is true, we don't want to see this vertex
                if flag:
                    avoid.append(vertex)

            # solution of the generalized buchi inter safety game
            win = generalized_buchi_inter_safety(arena, sets_gen, avoid)

            # if we have some winning region
            if len(win) != 0:
                att2 = attractor(arena, win, 0)
                partial_winning_region_player0.extend(att2)
                return generalized_buchi_partial_solver(arena.subarena(att2),
                                                partial_winning_region_player0,
                                                partial_winning_region_player1)

        depth += 1

    return arena, partial_winning_region_player0, partial_winning_region_player1


def odd_tuples_iterator(depth, priorities, sizes, li, k, t):
    """
    Iterate over the k-uples consisting of even priorities.
    :param depth:
    :type depth:
    :param priorities:
    :type priorities:
    :param sizes:
    :type sizes:
    :param li:
    :type li:
    :param k:
    :type k:
    :param t:
    :type t:
    """

    if depth == 0:
        yield [priorities[index][element] for index, element in enumerate(li)]

    else:
        for i in range(t, k):
            li[i] += 1
            if not li[i] >= sizes[i]:
                for j in even_tuples_iterator(depth - 1, priorities, sizes, li, k, i):
                    yield j
            li[i] -= 1

def generalized_buchi_partial_solver_inverted_players(arena, partial_winning_region_player0, partial_winning_region_player1):
    """
    Partial solver for generalized parity games using fatal attractors. Implementation using inline version of
    generalized buchi inter safety games. The players are inverted as we consider a game with complemented priorities.
    :param arena: the arena we consider
    :type arena: Arena
    :param partial_winning_region_player0: should be empty list when called
    :type partial_winning_region_player0: []
    :param partial_winning_region_player1: should be empty list when called
    :type partial_winning_region_player1: []
    :return: a partial solution sub-arena, partial_player0, partial_player1 in which sub-arena remains unsolved and
    partial_player0 (resp. partial_player1) is included in the winning region of player 0 (resp. player 1) in arena.
    :rtype: Arena, list of int, list of int
    """

    # base case : game is empty
    if arena.nbr_vertices == 0:
        return arena, partial_winning_region_player0, partial_winning_region_player1

    # retrieve useful information on the game
    priorities = [[] for _ in range(arena.nbr_functions)]  # list of list of priorities for each function
    odd_priorities = [[] for _ in range(arena.nbr_functions)]  # list of list of odd priorities for each function
    sizes = [0] * arena.nbr_functions  # sizes for the lists of priorities
    odd_sizes = [0] * arena.nbr_functions  # sizes for the lists of odd priorities
    empty_set = set()  # useful when computing fatal attractor for player 1

    # retrieve all priorities and put them in the lists of priorities for each function
    for func in range(arena.nbr_functions):
        priorities[func] = sorted(arena.priorities[func].keys(), reverse=True)
        odd_priorities[func] = [prio for prio in priorities[func] if (prio % 2)]

        # if there are no even priorities according to one of the functions, the game is completely won by player 1
        # because all priorities are even and in the original game they are therefore odd
        # return empty sub-game and all vertices added to partial_winning_region_player1
        if len(odd_priorities[func]) == 0:
            partial_winning_region_player1.extend(arena.vertices)
            return Arena(), partial_winning_region_player0, partial_winning_region_player1

        sizes[func] = len(priorities[func])
        odd_sizes[func] = len(odd_priorities[func])

    # here we have sorted lists of priorities as well as their sizes

    indexes = [0] * arena.nbr_functions  # index for each function to go trough its priorities
    depth = 0  # depth is needed for the level of the lattice
    max_size = max(odd_sizes)  # needed for the maximum level of the lattice

    # while we have not considered every couple of the lattice i.e. not reached the maximal depth for the levels in
    # the lattice for the even priorities or we have not considered every priority in the list of priorities
    while (not all(indexes[w] == sizes[w] for w in range(arena.nbr_functions))) or (depth != max_size + 2):

        # for each function, we treat even priorities in order in the list until we have reached an odd priority
        for i in range(arena.nbr_functions):

            # while we can advance in the list and we encounter an even priority, we consider it
            while indexes[i] < sizes[i] and priorities[i][indexes[i]] % 2 == 0:

                # we have an even priority to consider
                even_priority = priorities[i][indexes[i]]

                # set of vertices of color 'even_priority' according to function i
                target_set = set(arena.priorities[i][even_priority])

                # perform fixpoint computation to find fatal attractor for player odd

                cache = set()

                while cache != target_set and target_set != empty_set:

                    cache = target_set

                    monotone_att = monotone_attractor(arena, target_set, even_priority, i, specific_player=1)

                    if target_set.issubset(monotone_att):

                        regular_att = attractor(arena, monotone_att, 1)

                        partial_winning_region_player1.extend(regular_att)

                        return generalized_buchi_partial_solver(arena.subarena(regular_att),
                                                                partial_winning_region_player0,
                                                                partial_winning_region_player1)

                    else:
                        target_set = target_set.intersection(monotone_att)

                # if we have not found a fatal attractor, we go forward in the list and restart the same logic until
                # reaching an odd priority or the end of the list
                indexes[i] += 1

            # we have found an odd priority at position indexes[i], at next iteration of the outer while, we restart
            # from the next index in the list
            if indexes[i] < sizes[i]:
                indexes[i] += 1

        # when this is reached, we know we have handled every even priorities until reaching an odd priority for each
        # function

        # go through every k-uple of odd priorities in the current level
        for kuple in odd_tuples_iterator(depth, odd_priorities, odd_sizes, [0] * arena.nbr_functions,
                                          arena.nbr_functions, 0):

            # we now will compute a generalized buchi inter safety game
            avoid = []  # vertices for the safety game, to be avoided
            sets_gen = [[] for _ in range(arena.nbr_functions)]  # sets of vertices to be visited infinitely often

            for vertex in arena.vertices:

                flag = False  # is the vertex to be avoided (greater priority than required for some function)

                # for each function
                for func_index in range(arena.nbr_functions):

                    # priority of the vertex according to that function
                    prio = arena.vertex_priorities[vertex][func_index]

                    # priority is even and greater than the corresponding one in the k-uple, we want to avoid the vertex
                    if prio % 2 == 0 and prio > kuple[func_index]:
                        flag = True
                    # else if the priority is the one we want to see, add it to the set to be visited infinitely often
                    elif prio == kuple[func_index]:
                        sets_gen[func_index].append(vertex)

                # if the flag is true, we don't want to see this vertex
                if flag:
                    avoid.append(vertex)

            # solution of the generalized buchi inter safety game
            win = generalized_buchi_inter_safety(arena, sets_gen, avoid)

            # if we have some winning region
            if len(win) != 0:
                att2 = attractor(arena, win, 0)
                partial_winning_region_player0.extend(att2)
                return generalized_buchi_partial_solver(arena.subarena(att2),
                                                partial_winning_region_player0,
                                                partial_winning_region_player1)

        depth += 1

    return arena, partial_winning_region_player0, partial_winning_region_player1