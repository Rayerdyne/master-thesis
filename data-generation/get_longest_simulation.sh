#!/bin/bash

# This script will get the longest simulation time that ran, by fetching the job ids in the
# finished.txt file then calling `seff` on them. It will sort the result and duplicates are 
# removed.
# This will be used once to set the ideal timeout for the GAMS simulation.

BASE_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
FINISHED=slurm-outputs/$BASE_DIR/finished.txt

echo $FINISHED

# get the ids of the jobs in a temp file
sed -n -E "s/.*job id ([0-9]+).*/\1/p" $FINISHED > ids.tmp.txt

# get the time they took in a temp file
cat ids.tmp.txt | xargs -n1 -d'\n' -- seff | sed -n -E "s/CPU Utilized: ([0-9]+):([0-9]+).*/\1:\2/p" > times.tmp.txt

# sort the time by decreasing order
sort -g -r times.tmp.txt | uniq | head -n 20

# clean temp files
# rm ids.tmp.txt
# rm times.tmp.txt