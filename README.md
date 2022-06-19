# SPORE: Symbolic Partial sOlvers for REalizability
A prototype symbolic implementation of partial solvers for (generalized) parity games applied to LTL realizability.

SPORE was developed by
* Charly Delfosse, University of Mons ([website](http://math.umons.ac.be/staff/Delfosse.Charly/))
* Christophe Grandmont, University of Mons
* Gaëtan Staquet, University of Mons ([website](http://informatique.umons.ac.be/staff/Staquet.Gaetan/))
* Clément Tamines, University of Mons ([website](https://clement.tamin.es))

The LTL realizability toolchain of SPORE uses code from either [tlsf2gpg](https://github.com/gaperez64/tlsf2gpg), or
[SyfCo](https://github.com/reactive-systems/syfco) and [ltl2tgba](https://spot.lrde.epita.fr/ltl2tgba.html).



## About
SPORE is a prototype tool meant to test the feasibility of using generalized parity games in the context of LTL realizability. The
toolchain used by SPORE is the following:
1. Input LTL formulas in [TLSF format](https://arxiv.org/abs/1604.02284) are split into sub-formulas which are used to generate a generalized parity game.
This translation from LTL to generalized parity games is done using a modified version of [tlsf2gpg](https://github.com/gaperez64/tlsf2gpg).
2. SPORE implements both explicit and symbolic (BDD-based) algorithms to solve (generalized) parity games and decide whether the input formula is realizable. 
   A description of the partial solvers implemented in SPORE and references to the recursive algorithm for (generalized) parity 
   games can be found in [this paper](https://arxiv.org/abs/1907.06913).

#### Updated full BDD approach
In order to optimize the practical execution time of SPORE's LTL realizability toolchain, the following updated operations have been introduced to obtain the generalized parity game.
1. The script `scripts/create_parity_automata.sh` extracts the input and output atomic propositions from the LTL formula in [TLSF format](https://arxiv.org/abs/1604.02284) and splits it into sub-formulas using [SyfCo](https://github.com/reactive-systems/syfco).
2. Every LTL formula is then sent to [ltl2tgba](https://spot.lrde.epita.fr/ltl2tgba.html),
   a command from [Spot](https://spot.lrde.epita.fr/), which generates a corresponding deterministic parity automaton. These automata are stored in a temporary `automata/game/` folder in the [Hanoi Omega-Automata (HOA) format](http://adl.github.io/hoaf/).
3. SPORE translates those automata into symbolic parity automata, then computes the product of those automata,
   leading to a single generalized parity automata. It is afterwards translated into a symbolic generalized parity
   game, and the same algorithms introduced in the regular version of SPORE are used to solve the generalized parity game and decide whether the input formula is realizable.
   
The improvement in this updated version, which we call the "full BDD" approach, is therefore to allow for an earlier introduction of BDDs in the LTL to generalized parity game translation, leading to a smaller symbolic representation of this game. In the regular version, the generalized parity game was created explicitly before being translated into a BDD representation.

## How to use
* Instructions on how to use and build tlsf2gpg can be found on tlsf2gpg's [repository](https://github.com/gaperez64/tlsf2gpg).  
* SPORE is written using Python 2.7 and should be fully Python 3 compatible. Dependencies can be found in [requirements.txt](https://github.com/Skar0/spore/blob/master/requirements.txt). Note that `dd` should be compiled with CUDD support.
* The full BDD approach requires SyfCo. Instructions on how to install are provided in its [repository](https://github.com/reactive-systems/syfco).
* The full BDD approach also requires Spot, more precisely the [ltl2tgba](https://spot.lrde.epita.fr/ltl2tgba.html) command.
  Instructions on how to compile Spot can be found on Spot's [website](https://spot.lrde.epita.fr/install.html).
  If needed, the user can increase the number of acceptance sets used by Spot using the following option `./configure --enable-max-accsets=64` to allow the generation of some additional automata.

The usage instructions for the standalone SPORE (generalized) parity game solver can be accessed using `python spore.py -h`.
The command to solve a (generalized) parity game using SPORE is: 

    python spore.py (-pg | -gpg) [-par | -snl | -rec] [-bdd | -reg | -fbdd] [-dynord | -arbord] [-rstredge] input_path

The following table describes the possible options:

| Option            | Description   
| :---------------- |:-----------
| -pg               | Load a parity game (must be in PGSolver format).
| -gpg              | Load a generalized parity game (must be in extended PGSolver format).       
| -par              | Use the combination of the recursive algorithm with a partial solver to solve the game (default).
| -snl              | Perform a single call to the partial solver and use the recursive algorithm to solve the remaining game.
| -rec              | Use the recursive algorithm to solve the game.
| -bdd              | Use the symbolic implementation of the algorithms, using Binary Decision Diagrams (default).
| -reg              | Use the regular, explicit, implementation of the algorithms.
| -fbdd             | Use the full BDD approach consisting of the symbolic implementation of the algorithms, using Binary Decision Diagrams, and in addition, use a symbolic implementation of automata.
| -dynord           | With -fbdd only, use the dynamic ordering available in dd with CUDD as backend.
| -arbord           | With -fbdd only, enable an arbitrary ordering of the BDD just before the computation of the product automaton : (1) state variables, (2) atomic propositions, (3) state variable bis.
| -rstredge &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; | With -fbdd only, enable the restriction of edges to reachable vertices, incoming and outgoing, when the symbolic arena is built.

Examples on how to launch both the standalone and toolchain versions of SPORE can be found below.  

### Standalone SPORE -reg or -bdd

To solve and display realizability for a generalized parity game located in the file `gen_pgame.gpg` using the BDD-based implementation 
of the combination of the recursive algorithm and a partial solver:

    python spore.py -gpg -par -bdd gen_pgame.gpg

or simply

    python spore.py -gpg gen_pgame.gpg

To do so using the explicit implementation of the recursive algorithm:

    python spore.py -gpg -rec -reg gen_pgame.gpg

### Standalone SPORE -fbdd

With the argument -fbdd, corresponding to the full BDD approach, the input path must be the file `automata/game/data.txt` that
contains input and output atomic propositions, and paths to the automata:

    python spore.py -gpg -par -fbdd automata/game/data.txt

Other parameters such as -dynord, -arbord and -rstredge are also available in this case.


### Toolchain for tlsf2gpg (regular and BDD approach)

To transform a TLSF file `system.tlsf` into a generalized parity game and decide its realizability using the BDD-based implementation of the combination of the recursive algorithm and a partial solver:

    ./scripts/spore_LTL_toolchain.sh system.tlsf

### Toolchain for SyfCo and ltl2tgba (full BDD approach)

To transform a TLSF file `system.tlsf` into parity automata and decide its realizability using the symbolic generalized
parity game computed from the product of those symbolic automata, using the BDD-based implementation of the combination
of the recursive algorithm and a partial solver:

    ./scripts/spore_LTL_toolchain_fbdd.sh system.tlsf

### Tests
Unit tests can be run using

    python -m unittest discover .

from the root directory of the project.

## Formats

For the regular and BDD approach, using tlsf2gpg, the `input_path` argument must be the path to a file containing a parity
game in [PGSolver format](https://github.com/tcsprojects/pgsolver) or a generalized parity game in extended PGSolver format.

The extended PGSolver format follows the same format as PGSolver for
vertices and successors, with two changes. First, the first line of the file must be of the form `generalized-parity n m;` 
where `n` is the maximal index used for the vertices (as in the original format) and `m` is the number of priority functions.
Then, in each line describing a vertex, `m` priorities should be specified. Examples can be found in the `arenas/gpg/` directory.

For the full BDD approach, the `input_path` argument must be the path to a file `data.txt` generated by
`create_parity_automata.sh`. This file contains a list of input atomic propositions as first line, a list of output atomic
propositions in the second line, and then as many lines as there are parity automata generated by `ltl2tgba`, which correspond to the paths to their respective automaton files.

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

Alternatively, SPORE is also featured in the report concerning the reactive synthesis competition:
```
@article{DBLP:journals/corr/abs-2206-00251,
  author    = {Swen Jacobs and
               Guillermo A. P{\'{e}}rez and
               Remco Abraham and
               V{\'{e}}ronique Bruy{\`{e}}re and
               Micha{\"{e}}l Cadilhac and
               Maximilien Colange and
               Charly Delfosse and
               Tom van Dijk and
               Alexandre Duret{-}Lutz and
               Peter Faymonville and
               Bernd Finkbeiner and
               Ayrat Khalimov and
               Felix Klein and
               Michael Luttenberger and
               Klara J. Meyer and
               Thibaud Michaud and
               Adrien Pommellet and
               Florian Renkin and
               Philipp Schlehuber{-}Caissier and
               Mouhammad Sakr and
               Salomon Sickert and
               Ga{\"{e}}tan Staquet and
               Clement Tamines and
               Leander Tentrup and
               Adam Walker},
  title     = {The Reactive Synthesis Competition {(SYNTCOMP):} 2018-2021},
  journal   = {CoRR},
  volume    = {abs/2206.00251},
  year      = {2022},
  url       = {https://doi.org/10.48550/arXiv.2206.00251},
  doi       = {10.48550/arXiv.2206.00251},
  eprinttype = {arXiv},
  eprint    = {2206.00251},
  timestamp = {Mon, 13 Jun 2022 15:31:50 +0200},
  biburl    = {https://dblp.org/rec/journals/corr/abs-2206-00251.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```
