# SPORE: Symbolic Partial sOlvers for REalizability
A prototype symbolic implementation of partial solvers for (generalized) parity games applied to LTL realizability.

SPORE was developed by
* Charly Delfosse, University of Mons
* Gaëtan Staquet, University of Mons ([website](http://informatique.umons.ac.be/staff/Staquet.Gaetan/))
* Clément Tamines, University of Mons ([website](https://clement.tamin.es))

The LTL realizability toolchain of SPORE uses code from [tlsf2gpg](https://github.com/gaperez64/tlsf2gpg).



## About
SPORE is a prototype tool meant to test the feasibility of using generalized parity games in the context of LTL realizability. The
toolchain used by SPORE is the following:
1. Input LTL formulas in [TLSF format](https://arxiv.org/abs/1604.02284) are split into sub-formulas which are used to generate a generalized parity game.
This translation from LTL to generalized parity games is done using a modified version of [tlsf2gpg](https://github.com/gaperez64/tlsf2gpg).
2. SPORE implements both explicit and symbolic (BDD-based) algorithms to solve (generalized) parity games and decide whether the input formula is realizable. 
   A description of the partial solvers implemented in SPORE and references to the recursive algorithm for (generalized) parity 
   games can be found in [this paper](https://arxiv.org/abs/1907.06913).

## How to use
* Instructions on how to use and build tlsf2gpg can be found on tlsf2gpg's [repository](https://github.com/gaperez64/tlsf2gpg).  
* SPORE is written using Python 2.7 and should be fully Python 3 compatible. Dependencies can be found in [requirements.txt](https://github.com/Skar0/spore/blob/master/requirements.txt). Note that `dd` should be compiled with CUDD support.

The usage instructions for the standalone SPORE (generalized) parity game solver can be accessed using `python spore.py -h`.
The command to solve a (generalized) parity game using SPORE is: 

    python spore.py (-pg | -gpg) [-par | -snl | -rec] [-bdd | -reg] input_path

The following table describes the possible options:

| Option         | Description   
| :------------- |:-------------
| -pg            | Load a parity game (must be in PGSolver format).
| -gpg           | Load a generalized parity game (must be in extended PGSolver format).       
| -par           | Use the combination of the recursive algorithm with a partial solver to solve the game (default).
| -snl           | Perform a single call to the partial solver and use the recursive algorithm to solve the remaining game.
| -rec           | Use the recursive algorithm to solve the game.
| -bdd           | Use the symbolic implementation of the algorithms, using Binary Decision Diagrams (default).
| -reg           | Use the regular, explicit, implementation of the algorithms.

Examples on how to launch both the standalone and toolchain versions of SPORE can be found below.  

### Standalone SPORE

To solve and display realizability for a generalized parity game located in the file `gen_pgame.gpg` using the BDD-based implementation 
of the combination of the recursive algorithm and a partial solver:

    python spore.py -gpg -par -bdd gen_pgame.gpg

or simply

    python spore.py -gpg gen_pgame.gpg

To do so using the explicit implementation of the recursive algorithm:

    python spore.py -gpg -rec -reg gen_pgame.gpg

### Toolchain

To transform a TLSF file `system.tlsf` into a generalized parity game and decide its realizability using the BDD-based implementation 
of the combination of the recursive algorithm and a partial solver:

    spore_LTL_toolchain.sh system.tlsf

### Tests
Unit tests can be run using

    python -m unittest discover .

from the root directory of the project.
## Formats

The `input_path` argument must be the path to a file containing a parity game in [PGSolver format](https://github.com/tcsprojects/pgsolver) 
or a generalized parity game in extended PGSolver format. 

The extended PGSolver format follows the same format as PGSolver for
vertices and successors, with two changes. First, the first line of the file must be of the form `generalized-parity n m;` 
where `n` is the maximal index used for the vertices (as in the original format) and `m` is the number of priority functions.
Then, in each line describing a vertex, `m` priorities should be specified. Examples can be found in the `arenas/gpg/` directory.

Since SPORE is meant to be used for LTL realizability, the output of the tool is `REALIZABLE` if the LTL formula used to
generate the input game is realizable, and `UNREALIZABLE` if it is not.

## Citing
If you use this software for your academic work, please cite the following Reachability Problems paper on partial solvers for generalized parity games:
```
@inproceedings{DBLP:conf/rp/BruyerePRT19,
  author    = {V{\'{e}}ronique Bruy{\`{e}}re and
               Guillermo A. P{\'{e}}rez and
               Jean{-}Fran{\c{c}}ois Raskin and
               Cl{\'{e}}ment Tamines},
  editor    = {Emmanuel Filiot and
               Rapha{\"{e}}l M. Jungers and
               Igor Potapov},
  title     = {Partial Solvers for Generalized Parity Games},
  booktitle = {Reachability Problems - 13th International Conference, {RP} 2019,
               Brussels, Belgium, September 11-13, 2019, Proceedings},
  series    = {Lecture Notes in Computer Science},
  volume    = {11674},
  pages     = {63--78},
  publisher = {Springer},
  year      = {2019},
  url       = {https://doi.org/10.1007/978-3-030-30806-3\_6},
  doi       = {10.1007/978-3-030-30806-3\_6},
  timestamp = {Mon, 09 Sep 2019 15:37:02 +0200},
  biburl    = {https://dblp.org/rec/conf/rp/BruyerePRT19.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```
