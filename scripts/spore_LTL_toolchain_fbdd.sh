#!/bin/bash
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

# $1 is the command line parameter given to spore_LTL_toolchain_fbdd.sh; it corresponds to the .tlsf file
./scripts/create_parity_automata.sh $1 "game"
# the generated automata are put in automata/game/ (see create_parity_automata.sh)
python3 spore.py -gpg -fbdd -dynord "automata/game/data.txt"
# the game is then solved using spore
