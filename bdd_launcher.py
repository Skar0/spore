import bdd.gpg2bdd
import bdd.generalizedRecursive
import dd.cudd as _bdd
import bdd.misc

manager = _bdd.BDD()
arena, all_vertices = bdd.gpg2bdd.gpg2bdd("./arenas/gpg/example_4.gpg", manager)
winning_region_player0, winning_region_player1 = bdd.generalizedRecursive.generalized_recursive(arena, manager)
vertex_0_dict_rep = next(manager.pick_iter(all_vertices[0]))
vertex_0_won_by_player0 = manager.let(vertex_0_dict_rep, winning_region_player0) == manager.true
print(vertex_0_won_by_player0)

# Printing the full solution (this takes a very long time)
# print(bdd.misc.bdd2int(w0, arena.vars, manager, all_vertices))
# print(bdd.misc.bdd2int(w1, arena.vars, manager, all_vertices))
