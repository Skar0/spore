from bdd.bdd_util import *
from collections import defaultdict, deque


def explicit2symbolic_spot(aut, manager):
    """
    Construct a new symbolic automaton from a parity automaton generated by Spot. Spot uses BuDDy as binary decision
    diagram (BDD) library for atomic propositions, but deals with explicit automata.

    Spot : https://spot.lrde.epita.fr/
    BuDDy : http://buddy.sourceforge.net/manual/main.html

    :param aut: the explicit spot automaton
    :type aut: spot.twa_graph
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: a symbolic DPA object that represents the explicit automaton
    :rtype: SymbolicGenDPA
    """

    # import spot here because don't want to import it if we don't use this method (if spot isn't installed)
    import spot  # spot is already setup

    nbr_states = aut.num_states()
    # nbr_edges = aut.num_edges()

    nbr_digits_vertices = len(bin(nbr_states - 1)) - 2  # binary representation is prefixed by '0b'
    # equivalent : math.ceil(math.log(num_states, 2))

    # variables to encode states
    vars = ['x{}'.format(j) for j in range(nbr_digits_vertices)]
    vars_bis = ['xb{}'.format(j) for j in range(nbr_digits_vertices)]
    all_vars = vars + vars_bis
    mapping_bis = dict(zip(vars, vars_bis))
    inv_mapping_bis = dict(zip(vars_bis, vars))

    manager.declare(*all_vars)

    # Get bool expression that is true iff we use digits of init state
    init = build_symbolic_equal(aut.get_init_state_number(), nbr_digits_vertices, manager)

    # Get a state automaton, colors are encoded in transitions, size is exactly the dimension
    dimension = next(aut.out(aut.get_init_state_number()).__iter__()).acc.count()
    priorities = [defaultdict(lambda: manager.false) for _ in range(dimension)]
    transitions = manager.false

    # Graph exploration on the spot graph (automaton), only a queue since we have no deadlocks and we want to consider
    # reachable states only
    visited = [False] * nbr_states
    queue = deque([aut.get_init_state_number()])
    visited[aut.get_init_state_number()] = True
    while queue:
        s = queue.popleft()
        first_visit = True
        for t in aut.out(s):

            # add destination node in the queue (if not already visited)
            if not visited[t.dst]:
                visited[t.dst] = True
                queue.append(t.dst)

            # for each transition, get source and destination nodes as bdd
            src_bdd = build_symbolic_equal(t.src, nbr_digits_vertices, manager)
            dst_bdd = build_symbolic_equal(t.dst, nbr_digits_vertices, manager)

            if first_visit:
                # priorities are encoded in transitions, but in a DPA every transitions
                # from a node have the same priority, so we just get it once
                first_visit = False
                prios = t.acc.as_string()[1:-1].split(",")  # as_string() returns {prio1,...,prio_n}

                for dim in range(dimension):
                    priorities[dim][int(prios[dim])] |= src_bdd

            # get the label of the transition (transform it to "True" if it's "1", dd does not take "1")
            label_str = spot.bdd_format_formula(aut.get_dict(), t.cond)
            if label_str == "1":
                label_str = "True"

            label = manager.add_expr(label_str)  # use label in transition expression
            transitions |= src_bdd & label & manager.let(mapping_bis, dst_bdd)

    # Add every previous variables in the new automaton
    dpa = SymbolicGenDPA()
    dpa.vars = vars
    dpa.vars_bis = vars_bis
    dpa.all_vars = all_vars
    dpa.mapping_bis = mapping_bis
    dpa.inv_mapping_bis = inv_mapping_bis

    dpa.nbr_vertices = nbr_states
    dpa.nbr_digits_vertices = nbr_digits_vertices

    dpa.dimension = dimension
    dpa.priorities = priorities

    dpa.transitions = transitions

    dpa.init = init

    return dpa


def explicit2symbolic_path(path, manager):
    """
    Construct a new symbolic automaton from a parity automaton generated by Spot (ltl2tgba command)
    :param path: the path to the file that contains an automaton as HOA format created by ltl2tgba command.
    :type path: str
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: a symbolic DPA object that represents the explicit automaton
    :rtype: SymbolicGenDPA
    """

    with open(path, 'r') as f:
        f.readline()  # HOA: v1
        f.readline()  # name
        nbr_states = int(f.readline().strip().split('States: ')[1])
        init_state_number = int(f.readline().strip().split('Start: ')[1])
        ap = list(map(lambda x: x[1:-1], f.readline().strip().split(" ")[2:]))
        f.readline()  # acc-name (parity max even)
        f.readline()  # Acceptance (priorities Inf Fin ...)
        f.readline()  # properties
        f.readline()  # properties
        f.readline()  # --BODY--

        nbr_digits_vertices = len(bin(nbr_states - 1)) - 2  # binary representation is prefixed by '0b'
        # equivalent : math.ceil(math.log(num_states, 2))

        # variables to encode states
        vars = ['x{}'.format(j) for j in range(nbr_digits_vertices)]
        vars_bis = ['xb{}'.format(j) for j in range(nbr_digits_vertices)]
        all_vars = vars + vars_bis
        mapping_bis = dict(zip(vars, vars_bis))
        inv_mapping_bis = dict(zip(vars_bis, vars))

        manager.declare(*all_vars)
        # TODO: reorder variables ? According to R. Abraham : (1) APs, (2) current state, (3) succcessor state

        # Get bool expression that is true iff we use digits of init state
        states = [build_symbolic_equal(i, nbr_digits_vertices, manager) for i in range(nbr_states)]
        init = states[init_state_number]

        # Get a state automaton, colors are encoded in transitions, size is exactly the dimension
        # We don't know dimension yet, first state will gives us the dimension
        dimension = -1
        priorities = None
        transitions = manager.false

        read = f.readline().strip()
        # while there is a state or a transition
        while read != "--END--":

            # We read a state information (number, priorities)
            # e.g. "State: 3 {1,3}" : state number 3, two dimensions
            if read.startswith("State: "):
                state_info = read[7:].split(" ")
                state_number = int(state_info[0])
                src_bdd = states[state_number]
                prios = list(map(lambda x: int(x), state_info[1][1:-1].split(",")))
                if dimension == -1:
                    dimension = len(prios)
                    priorities = [defaultdict(lambda: manager.false) for _ in range(dimension)]

                for dim in range(dimension):
                    priorities[dim][int(prios[dim])] |= src_bdd

            # We read a transition coming from the previous state we saw to a node we have to read
            # e.g. "[0 | 1&!0] 3" : the previous src state has a transition to the state number 3, the label is
            # first AP or second AP and not first AP.
            else:
                label_str, dst_nbr = read.split("] ")
                label_str = label_str[1:]
                dst_bdd = states[int(dst_nbr)]  # dst node as bdd function

                if label_str == "t":
                    label_str = "True"  # if the label is "t", it means true
                else:
                    new_label_str = ""
                    cur_nbr = ""
                    # We read the label, when we see a number, we concatenate it to a str cur_nbr, when we see other
                    # char than digit, the corresponding AP of the number is added to the final label then we add the
                    # read character
                    for i in range(len(label_str)):
                        char = label_str[i]
                        if not char.isdigit():
                            if cur_nbr != "":
                                new_label_str += ap[int(cur_nbr)]
                                cur_nbr = ""
                            new_label_str += char
                        else:
                            cur_nbr += char

                    if cur_nbr != "":  # if the last char was a digit
                        new_label_str += ap[int(cur_nbr)]

                    label_str = new_label_str

                # Add the transition and the label as bdd function
                # TODO: Produces "maximum recursion depth exceeded" for some benchmarks, when there are too many labels.
                # TODO: Increase the recursion limit solve it for some cases, otherwise we get "Segmentation fault
                # TODO: (core dumped)" or "killed" then the program exits.
                label = manager.add_expr(label_str)
                transitions |= src_bdd & label & manager.let(mapping_bis, dst_bdd)

            read = f.readline().strip()  # loop, read the next line

        # Add every previous variables in the new automaton
        dpa = SymbolicGenDPA()
        dpa.vars = vars
        dpa.vars_bis = vars_bis
        dpa.all_vars = all_vars
        dpa.mapping_bis = mapping_bis
        dpa.inv_mapping_bis = inv_mapping_bis

        dpa.nbr_vertices = nbr_states
        dpa.nbr_digits_vertices = nbr_digits_vertices

        dpa.dimension = dimension
        dpa.priorities = priorities

        dpa.transitions = transitions

        dpa.init = init

        return dpa


class SymbolicGenDPA:
    """
    This class represents a symbolic generalized deterministic parity automaton (DPA) encoded with DD library.
    Function explicit2symbolic_path builds a new DPA from a SPOT automaton located in a .hoaf file.

    A symbolic automaton has a set of variables to represent states and atomic propositions. With N variables, we can
    represents at most 2^N states. Atomic propositions are labels on transitions.

    DD : https://github.com/tulip-control/dd
    SPOT : https://spot.lrde.epita.fr/
    """

    def __init__(self):
        # list of variables x{i}, represent variables states
        self.vars = None  # type: list[str]
        # variables xb{i} to represent a copy for vars but as destination for transitions
        self.vars_bis = None  # type: list[str]
        # list of all variables (vars + vars_bis)
        self.all_vars = None  # type: list[str]
        # dict to map vars to vars_bis
        self.mapping_bis = None  # type: dict[str, str]
        # dict to map vars_bis to vars
        self.inv_mapping_bis = None  # type: dict[str, str]

        self.nbr_vertices = 0  # type: int
        # number of bits required to represent the vertices indexes in binary
        self.nbr_digits_vertices = 0  # type: int

        # a non-generalized parity automaton has a dimension of 1
        self.dimension = 1  # type: int

        # the transition relation as bool expression on variables "vars U AP U vars_bis"
        self.transitions = None  # type: dd.cudd.Function
        # list of dict, length is dimension number, each dict contains map priorities in the dict dimension
        self.priorities = None  # type: list[dict[int, dd.cudd.Function]]

        self.init = None  # type: dd.cudd.Function

    def remap(self, new_base_index, manager):
        """
        Create a new DPA but we shift variables by "new_base_index" value. The first variable goes
        from x{0} to x{new_base_index} in variable list and also in boolean expressions, for every variables.
        If we don't need to use self anymore, we can just modify priorities without any copy, but the time
        saving is probably negligible.
        :param new_base_index: the new index of the first variable
        :type new_base_index: int
        :param manager: the BDD manager
        :type manager: dd.cudd.BDD
        :return: a symbolic DPA object with the renamed variables.
        :rtype: SymbolicGenDPA
        """

        # Clone DPA to keep an unchanged automaton, priorities aren't copied deep so we don't want to copy here to
        # gain a little time. We manually reconstruct priorities list
        tmp = self.priorities
        self.priorities = None
        new = copy.copy(self)
        self.priorities = tmp

        # Rebase new variables and mapping dict in the copy
        new.vars = ['x{}'.format(j) for j in range(new_base_index, new_base_index + len(new.vars))]
        new.vars_bis = ['xb{}'.format(j) for j in range(new_base_index, new_base_index + len(new.vars_bis))]
        new.all_vars = new.vars + new.vars_bis
        new.mapping_bis = dict(zip(new.vars, new.vars_bis))
        new.inv_mapping_bis = dict(zip(new.vars_bis, new.vars))

        manager.declare(*new.all_vars)  # No effect if we declare a same variable many times

        remap_vars = dict(zip(self.all_vars, new.all_vars))  # Dict to rename vars inside boolean expressions

        # Rename boolean expressions that represents DPA
        new.init = manager.let(remap_vars, new.init)
        new.transitions = manager.let(remap_vars, new.transitions)

        new.priorities = []  # reconstruct a new priorities list
        for dim in self.priorities:
            # dim is a dict with priorities as key and bdd representing states with this prio as values
            prios = defaultdict(lambda: manager.false)
            for prio, function in dim.items():
                prios[prio] = manager.let(remap_vars, function)
            new.priorities.append(prios)

        return new

    def product(self, other, manager):
        """
        Construct the synchronized product of two automata : self and other.
        :param other: the other automaton to construct the product with
        :type other: SymbolicGenDPA
        :param manager: the BDD manager
        :type manager: dd.cudd.BDD
        :return: a symbolic DPA object which is the synchronized product of the two automata self and other
        :rtype: SymbolicGenDPA
        """

        # Remap other to have differents variable names
        other = other.remap(len(self.vars), manager)

        # If n1 is the state size of the first automaton and n2 the state size of the second, the number of digits is
        # ceil(log2(n1*n2)) (= ceil(log2(n1) + log2(n2))) which can be different of the sum of the two separatly
        # ceiling logs. E.g. for 5 states we use 3 variables, but a product of two 5-states automata, for a total of
        # 25 nodes, does not need 6 variables but only 5 (2^5 = 32 > 25). We have at most one unused variable. In
        # practical, all variables are used but not fully used, since every states isn't represented.
        # Actually, prod.nbr_vertices isn't correct since we can get non reachable states that should not be
        # considered. We cannot afford to calculate that with a SAT count.
        prod = SymbolicGenDPA()
        prod.nbr_vertices = self.nbr_vertices * other.nbr_vertices  # theoretical upper bound of states number
        prod.nbr_digits_vertices = len(bin(prod.nbr_vertices - 1)) - 2

        # Append lists and mapping of variables
        prod.vars = self.vars + other.vars
        prod.vars_bis = self.vars_bis + other.vars_bis
        prod.all_vars = self.all_vars + other.all_vars
        prod.mapping_bis = merge_two_dicts(self.mapping_bis, other.mapping_bis)
        prod.inv_mapping_bis = merge_two_dicts(self.inv_mapping_bis, other.inv_mapping_bis)

        prod.init = self.init & other.init  # initial state is simply the conjonction

        # If the conjunction of labels gives false, transition is ignored
        prod.transitions = self.transitions & other.transitions

        # The dimensions are concatenated, we always generate a generalized DPA
        prod.dimension = self.dimension + other.dimension

        # care_vars can get everything, no need to explicitly develop because priorities is a list of n dimensions,
        # each dim is a dict with priority as key and nodes (dd.cudd.Function) as values.
        prod.priorities = self.priorities + other.priorities

        return prod

    def restrict_reachable_states(self, ap, manager):
        """
        Calculate reachable states of the automaton and restrict this automaton. It's not used anywhere since we
        restrict in the game.
        :param ap: atomic propositions over the automaton
        :type ap: list[str]
        :param manager: the BDD manager
        :type manager: dd.cudd.BDD
        :return: the result of reachable_states call
        :rtype: dd.cudd.Function
        """
        reach_states = reachable_states(self.init, self.transitions, self.vars, self.inv_mapping_bis, ap, manager)

        # Without this, we can get illegal transitions e.g. from vertices that does not exist
        self.transitions &= reach_states & manager.let(self.mapping_bis, reach_states)

        self.priorities = copy.copy(self.priorities)
        for i in range(len(self.priorities)):
            dim = self.priorities[i]
            new_dim = defaultdict(lambda: manager.false)
            for prio in dim:
                new_dim[prio] = dim[prio] & reach_states
            self.priorities[i] = new_dim

        return reach_states

    def __str__(self):
        return "Generalised Parity Automaton : variables: {}, number of states: {}, dimension: {}" \
            .format(self.vars, self.nbr_vertices, self.dimension)

    def __repr__(self):
        return self.__str__()