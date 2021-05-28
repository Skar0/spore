import sys
import dd.cudd as _bdd
from bdd.generalizedRecursive import generalized_recursive_with_psolver_multiple_calls
from bdd.gpg2bdd import gpg2bdd

manager = _bdd.BDD()
arena, all_vertices = gpg2bdd(sys.argv[1], manager)
winning_region_player0, winning_region_player1 = generalized_recursive_with_psolver_multiple_calls(arena, manager)
vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
vertex_0_won_by_player0 = manager.let(vertex_0_dict_rep, winning_region_player0) == manager.true

if vertex_0_won_by_player0:
    print("REALIZABLE")
else:
    print("UNREALIZABLE")

# Printing the full solution (this may take a very long time)
# import bdd.misc
# print(bdd.misc.bdd2int(winning_region_player0, arena.vars, manager, all_vertices))
# print(bdd.misc.bdd2int(winning_region_player1, arena.vars, manager, all_vertices))
