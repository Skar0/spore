import copy
from functools import reduce


def x(x_): return "x" + str(x_)
def xb(x_): return "xb" + str(x_)
def and_iter(u, v): return u & v


def decomp_data_file(path):
    """
    Reads a file data.txt and return a tuple of length 3 : the list of APs input, the list of APs output
    and the list for formulas. The input file is the data.txt output of create_parity_automata.sh. The format is :

    APs input
    APs output
    path file to the automaton 1
    path file to the automaton 2
    ...
    """

    automata_path = []
    input_signals = []
    output_signals = []

    with open(path, "r") as file:
        # lists to store input and output signals
        input_signals = file.readline().rstrip().split(" ")
        output_signals = file.readline().rstrip().split(" ")

        # iterate over automata
        for formula in file:
            automata_path.append(formula.rstrip())

    return input_signals, output_signals, automata_path


def merge_two_dicts(d1, d2):
    """
    Merge two dict and return de result without modify inputs.
    In python 3.9+, this method can be replaced by : dict1 | dict2
    In python 3.5+ it can be : {**dict1, **dict2}
    """
    d12 = d1.copy()
    d12.update(d2)
    return d12


def reachable_states(init, transitions, vars, inv_mapping_bis, ap, manager):
    """
    Construct a bdd function over the same variables then vars that represents reachable states from the given initial
    state with transition Function.
    :param init: the initial state for the reachability analysis
    :type init: dd.cudd.Function
    :param transitions: boolean expression to describe transitions or edges
    :type transitions: dd.cudd.Function
    :param vars: existing variables we want to find on each step.
    :type vars: list[str]
    :param inv_mapping_bis: mapping that replaces bis vars to vars
    :type inv_mapping_bis: dict[str,str]
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: a boolean expression that only represents the node given
    :rtype: dd.cudd.Function
    """
    var_and_ap = vars + ap

    states = init
    states_old = None
    while states != states_old:
        states_old = states

        transi_starting_by_states = transitions & states

        # If we want to deal with edges, we need to use exist on vars AND ap ...
        # Unless we don't use AP on edges anymore
        single_step = manager.exist(var_and_ap, transi_starting_by_states)

        tmp2 = manager.let(inv_mapping_bis, single_step)

        states = states | tmp2

    return states


def build_symbolic_equal(node, nbr_digit_vertices, manager):
    """
    Construct a boolean expression over n variables {x0, ... xn} that is true iff those variables are replaced by
    digits of the node.
    :param node: the node number
    :type node: int
    :param nbr_digit_vertices: the number of digit we want to consider
    :type nbr_digit_vertices: int
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: a boolean expression that only represents the given node
    :rtype: dd.cudd.Function
    """

    # use more digits if needed to keep every variables
    binary = format(node, "0" + str(nbr_digit_vertices) + "b")
    var_x = lambda k: manager.var(x(k))

    # use n-k-1 to keep order, x0: 1st digit, ... and not xn: 1st digit
    return reduce(and_iter,
                  [var_x(k) if int(binary[nbr_digit_vertices - k - 1]) else ~var_x(k) for k in
                   range(nbr_digit_vertices)])


def build_symbolic_set(set_node, nbr_digit_vertices, manager):
    """
    Construct a boolean expression over n variables {x0, ... xn} that is true iff those variables are replaced by
    digits of one of the node in set_node
    :param set_node: the set of nodes
    :type set_node: list (iterable)
    :param nbr_digit_vertices: the number of digit we want to consider
    :type nbr_digit_vertices: int
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: a boolean expression that only represents the nodes given in the set
    :rtype: dd.cudd.Function
    """

    return reduce(lambda u, v: u | v,
                  [build_symbolic_equal(node, nbr_digit_vertices, manager) for node in set_node])


def get_model_list(models, vars, vars_bis=None):
    """
    For debug purpose : take a list of dict from bdd.pick_iter(...) and returns a list
    of their value as more understandable string.
    """

    if vars_bis is None:
        vars_bis = []
    return list(map(lambda d: get_model(d, vars, vars_bis), models))


def get_model(dic, vars, vars_bis=None):
    """
    for debug purpose : takes a dict resulting of a SATany and returns a string
    """

    if vars_bis is None:
        vars_bis = []
    d = copy.copy(dic)
    res = ""
    for var in vars:
        if var in d:
            res += ("" if d.pop(var) else "!") + var + " & "

    label = ""
    if vars_bis:
        res = res[:-3] + " -> "
        for var in vars_bis:
            if var in d:
                res += ("" if d.pop(var) else "!") + var + " & "

        for ap in d:
            label = label + ("" if d[ap] else "!") + ap + " & "

    if label == "":
        return res[:-3]
    else:
        return res[:-3] + "  (" + label[:-3] + ")"


def print_automaton_info(aut, manager):
    details = aut.nbr_digits_vertices < 10
    print("---", aut)
    print("initial state:", get_model_list(list(manager.pick_iter(aut.init, care_vars=aut.vars)), aut.vars))

    if details:
        transi = list(manager.pick_iter(aut.transitions))
        print("transitions :", len(transi))
        for t in transi:
            print(get_model(t, aut.vars, aut.vars_bis))

        print("priorities")
        i = 0
        for dim in map(
                lambda d: dict(map(lambda i: (i[0], list(manager.pick_iter(i[1], care_vars=aut.vars))), d.items())),
                aut.priorities):
            print(">> dimension =", i)
            for prio, state in dim.items():
                print("  priorité", prio, ":", get_model_list(state, aut.vars))
            i += 1


def print_arena_info(arena, init, manager):
    print("PARITY GAME :")
    print("--- Generalised Parity Game : variables: {}, number of states: {}, dimension: {}"
          .format(arena.vars, arena.nbr_vertices, arena.nbr_functions))

    print("initial state:",
          get_model_list(list(manager.pick_iter(init, care_vars=arena.vars)), arena.vars))

    print("Reachable states :")
    R = reachable_states(init, arena.edges, arena.vars, arena.inv_mapping_bis, [], manager)
    for i in manager.pick_iter(R, care_vars=arena.vars):
        print(get_model(i, arena.vars))

    print("Vertices of p0 :")
    for model in manager.pick_iter(arena.player0_vertices, care_vars=arena.vars):
        print(get_model(model, arena.vars))
    print("Vertices of p1 :")
    for model in manager.pick_iter(arena.player1_vertices, care_vars=arena.vars):
        print(get_model(model, arena.vars))

    transi = list(manager.pick_iter(arena.edges, care_vars=arena.all_vars))
    print("transitions :", len(transi))
    for t in transi:
        print(get_model(t, arena.vars, arena.vars_bis))

    print("priorities")
    i = 0
    for dim in map(
            lambda d: dict(map(lambda j: (j[0], list(manager.pick_iter(j[1], care_vars=arena.vars))), d.items())),
            arena.priorities):
        print(">> dimension =", i)
        for prio, state in dim.items():
            print("  priority", prio, ":", get_model_list(state, arena.vars))
        i += 1