#!/bin/bash

# $1 is the command line parameter given to tool.sh; it corresponds to the .tlsf file
./tlsf2gpg.sh $1 > "generated_game.gpg"
# the generated game is put in a temp file
python regular_launcher.py "generated_game.gpg"
# the game is then solved
