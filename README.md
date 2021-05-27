# SPORE: Symbolic Partial sOlvers for REalizability
A prototype symbolic implementation of partial solvers for generalized parity games applied to LTL realizability.


## About
SPORE is meant to test the feasibility of using generalized parity games in the context of LTL realizability. 
Input LTL formulas in [TLSF](https://arxiv.org/abs/1604.02284) format are split into a conjunction of smaller sub-formulas and these sub-formulas are used to create a generalized parity game.
This translation from LTL to generalized parity games is done using a modified version of [tlsf2gpg](https://github.com/gaperez64/tlsf2gpg).
Then, SPORE implements both explicit and symbolic (BDD-based) algorithms to solve the generated games. 

## How to build
Execute the following commands

    virtualenv --python=python2.7 env
    source env/bin/activate
    python setup.py build_ext --inplace

Then, you can import the packages from the root of this project.

### Unit tests
Once `synttool` is installed, the unit tests can be run as:

    python -m unittest discover .

from the root directory of the project