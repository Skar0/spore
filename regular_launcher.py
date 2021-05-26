import sys
import regular.gpg2arena
import regular.generalizedRecursive

file_name = sys.argv[1]
arena = regular.gpg2arena.gpg2arena(file_name)
winning_region_player0, winning_region_player1 = regular.generalizedRecursive.generalized_recursive(arena)
vertex_0_won_by_player0 = 0 in winning_region_player0
if vertex_0_won_by_player0:
    print("REALIZABLE")
else:
    print("UNREALIZABLE")

# Printing the full solution
# print(winning_region_player0)
# print(winning_region_player1)
