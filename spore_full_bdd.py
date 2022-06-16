import sys
import dd.cudd as _bdd
import bdd.generalizedRecursive
from bdd.dpa2bdd import explicit2symbolic_path
from bdd.dpa2gpg import symb_dpa2gpg
from bdd.bdd_util import decomp_data_file, x, xb

# Increase the recursion limit to avoid error when we read a long label with explicit2symbolic_path
sys.setrecursionlimit(50000)

if len(sys.argv) > 1:
    syfco_decomp_output_path = sys.argv[1]
else:
    print("Please provide valid data file.")
    exit()

fbdd_dynamic_reordering = len(sys.argv) > 2 and sys.argv[2] == "True"
fbdd_arbitrary_reordering = len(sys.argv) > 3 and sys.argv[3] == "True"

info = True

if info: print("Read LTL formula ...")
input_signals, output_signals, automata_path = decomp_data_file(syfco_decomp_output_path)
aps = input_signals + output_signals

manager = _bdd.BDD()
manager.declare(*input_signals)
manager.declare(*output_signals)
manager.configure(reordering=fbdd_dynamic_reordering)

if info: print("Translate automata ...")
automata = []
for formula in automata_path:
    print(formula)
    automata.append(explicit2symbolic_path(formula, manager))

if fbdd_arbitrary_reordering:
    nb_total_var = sum(map(lambda a: len(a.vars), automata))
    new_order = dict()
    i = 0
    for var in input_signals + output_signals:
        new_order[var] = i
        i += 1
    for var in range(nb_total_var):
        manager.declare(x(var))
        new_order[x(var)] = i
        i += 1
    for var in range(nb_total_var):
        manager.declare(xb(var))
        new_order[xb(var)] = i
        i += 1
    _bdd.reorder(manager, new_order)

prod = automata[0]
nb_aut = len(automata)
for i in range(1, nb_aut):
    if info: print("Creating product  ... ({}/{})".format(i, nb_aut), end='\r')
    prod = prod.product(automata[i], manager)
if info: print("Creating product  ... ({a}/{a})".format(a=nb_aut))

if info: print("Build the parity game ...")
arena, init = symb_dpa2gpg(prod, input_signals, output_signals, manager)

if info: print("Solving ...")
if len(sys.argv) > 2:
    type_algo = int(sys.argv[2])
else:
    type_algo = 1

vertex_0_dict_rep = next(manager.pick_iter(init))

if type_algo == 0:
    winning_region_player0, winning_region_player1 = bdd.generalizedRecursive.generalized_recursive(arena, manager)
    algo = "Zielonka recursive"

elif type_algo == 1:
    winning_region_player0, winning_region_player1 = \
        bdd.generalizedRecursive.generalized_recursive_with_psolver(arena, manager)
    algo = "Zielonka with partial solver"

else:  # type == 2
    winning_region_player0, winning_region_player1 = \
        bdd.generalizedRecursive.generalized_recursive_with_psolver_multiple_calls(arena, manager)
    algo = "Zielonka with partial solver multiple calls"

vertex_0_won_by_player0 = manager.let(vertex_0_dict_rep, winning_region_player0) == manager.true
if vertex_0_won_by_player0:
    if info: print(algo, ": REALIZABLE")
    print("10")
else:
    if info: print(algo, ": UNREALIZABLE")
    print("20")
