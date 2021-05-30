#!/bin/bash

# $1 is the command line parameter given to spore_LTL_toolchain.sh; it corresponds to the .tlsf file
./tlsf2gpg.sh $1 > "generated_game.gpg"
# the generated game is put in a temp file
python spore.py -gpg "generated_game.gpg"
# the game is then solved using spore
