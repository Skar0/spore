from cpplib import bool

cdef class Arena:
    cdef unsigned long nbr_vertices
    cdef unsigned long nbr_functions
    cdef list vertices
    cdef list player
    cdef list priorities
    cdef dict vertex_priorities
    cdef dict successors
    cdef dict predecessors

    cdef Arena subarena(self, list removed)