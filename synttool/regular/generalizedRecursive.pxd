from attractor cimport attractor
from arena cimport Arena

cdef list transform_game(Arena arena)
cdef list generalized_recursive(Arena arena)
cdef tuple disj_parity_win(Arena arena, list max_priorities) # It should return (list, list) but that notation is not yet supported by Cython