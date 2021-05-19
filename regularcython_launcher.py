import regularcython.gpg2arena
import regularcython.generalizedRecursive

arena = regularcython.gpg2arena.gpg2arena("./arenas/gpg/example_4.gpg")
winning_region_player0, winning_region_player1 = regularcython.generalizedRecursive.generalized_recursive(arena)
vertex_0_won_by_player0 = 0 in winning_region_player0
print(vertex_0_won_by_player0)

# Printing the full solution
# print(winning_region_player0)
# print(winning_region_player1)
