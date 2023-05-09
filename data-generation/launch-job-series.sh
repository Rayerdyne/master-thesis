#!/bin/bash

serie_idx=$1
N_SAMPLES=$(python -c "from config import N_SAMPLES; print(N_SAMPLES)")
SIM_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
LOG_FILE="$SIM_DIR/logs/series-submitted.txt"

series_size=450
min=$((serie_idx*series_size))
max=$(((serie_idx+1)*series_size-1))

max=$(( $max < $N_SAMPLES ? $max : $N_SAMPLES ))

echo "min max: ($min, $max)"

if (($min > $max)); then
    echo "Series number $serie_idx exceeds maximum"
    exit
fi

for (( i=$min ; i <= $max ; i += $series_size ));
do
    a=$(( $i + $series_size - 1))
    up=$(( $a < $max ? $a : $max))
    echo "Starting jobs range [$i-$up]"
    echo "Range [$i-$up] submitted" >> $LOG_FILE
    #                           v-- ensures max 100 jobs simultaneously
    sbatch --array=$i-$up%100 --output=$SIM_DIR/logs/res_%A_%a.txt launch-simulation-jobs.sh
done
