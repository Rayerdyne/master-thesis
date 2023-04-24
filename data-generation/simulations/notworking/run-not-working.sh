#!/bin/bash
DIR=~/Unif/tfe

# activate environment
source "$DIR/Dispa-SET/.env/bin/activate"

# locate gams
export GAMSPATH=$DIR/gams37.1_linux_x64_64_sfx

$GAMSPATH/gams UCM_h.gms > gamsrun.log

echo "Job finished"