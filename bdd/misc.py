# -*- coding: utf-8 -*-
# SPORE: Symbolic Partial sOlvers for REalizability. 
# Copyright (C) 2021 - Charly Delfosse (University of Mons), Gaëtan Staquet (University of Mons), Clément Tamines (University of Mons)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

def int2dict(index, vars):
    """
    Transforms a vertex index in base 10 into a dictionary of Booleans. Variable x0 is the most significant bit.
    :param index: a vertex index in base 10
    :type index: int
    :param vars: variables declared in the BDD for the binary representation of vertices
    :type vars: list of str
    :return: a dictionary of Boolean values for each of the variables in vars, corresponding to the binary
    representation of index
    :rtype: dict of str: bool
    """

    nbr_vars = len(vars)
    binary_representation = format(index,
                                   '0' + str(nbr_vars) + 'b')  # string containing the binary representation of index
    return {vars[i]: bool(int(binary_representation[i])) for i in range(nbr_vars)}


def dict2int(dict_encoding, vars):
    """
    Transforms a dictionary of Booleans into a base 10 number. Variable x0 is the most significant bit for the binary
    representation of the number in the dictionary.
    :param dict_encoding: a dictionary of Boolean values for each of the variables in vars, corresponding to the binary
    representation of a vertex index
    :type dict_encoding: dict of str: bool
    :param vars: variables declared in the BDD for the binary representation of vertices
    :type vars: list of str
    :return: the vertex index corresponding to the provided dictionary in base 10
    :rtype: int
    """

    nbr_vars = len(vars)

    binary_representation = ""

    for i in range(nbr_vars):
        binary_representation = binary_representation + str(int(dict_encoding[vars[i]]))

    return int(binary_representation, 2)


def bdd2int(bdd, vars, manager, mapping=None):
    """
    Transforms all vertex indexes represented by a BDD into a list of the corresponding indexes in base 10. If a value
    for mapping is provided, then the base 10 value of the index in the BDD correspond to a different index in the
    original game, contained in mapping[index]. Otherwise, the index was encoded in the BDD as-is.
    :param bdd: a BDD representing a set of vertices
    :type bdd: dd.cudd.Function
    :param vars: list of variables used to represent the vertices in the BDD
    :type vars: list of str
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :param mapping: mapping for the correspondence between int index and BDD  node representation
    :type mapping: list of dd.cudd.Function
    :return: a list of indexes corresponding to the provided BDD
    :rtype: list of int
    """

    result = []

    for dict_representation in manager.pick_iter(bdd, vars):

        if not mapping:
            int_representation = dict2int(dict_representation, vars)
            result.append(int_representation)
        else:
            # look for the index corresponding to that dict_representation in the mapping
            for index in range(len(mapping)):
                # mapping[index] is a BDD node with a single assigment of vars that makes it true
                if dict_representation == next(manager.pick_iter(mapping[index], vars)):
                    result.append(index)

    return result
