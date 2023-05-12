#!/bin/bash

serie_idx=$1
N_SAMPLES=$(python -c "from config import N_SAMPLES; print(N_SAMPLES)")
SIM_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
LOG_FILE="slurm-outputs/$SIM_DIR/series-submitted.txt"

series_size=400
min=$((serie_idx*series_size))
max=$(((serie_idx+1)*series_size-1))

max=$(( $max < $N_SAMPLES ? $max : $N_SAMPLES ))
total=$(( ($N_SAMPLES / $series_size) + 1 ))

echo "min max: ($min, $max)"

if (($min > $max)); then
    echo "Series number $serie_idx exceeds maximum"
    exit
fi

echo "Starting jobs range [$min-$max], serie $serie_idx in [0-$((total-1))]"
echo "Range [$min-$max] submitted" >> $LOG_FILE
#                           v-- ensures max 100 jobs simultaneously
sbatch --array=$min-$max%100 --output=slurm-outputs/$SIM_DIR/simulation_%a.log launch-simulation-jobs.sh
