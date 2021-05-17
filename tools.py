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

    # TODO avoid conversion from str to int to bool, find a better way to create the dictionary of Booleans

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
