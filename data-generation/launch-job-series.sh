#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Job-launcher
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/launcher-future_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1 # make sure it runs when all jobs are completed
#SBATCH --mem-per-cpu=1 # megabytes
#SBATCH --partition=batch

# Starts a series of jobs given its index and prepares the submission of the following series.
# To do so, it submits the first series, and itself with the series just submitted as a 
# dependency, such that the queue size is not exceeded.
#
# Usage: ./launch-job-series.sh <idx>    or
#        sbacth launch-job-series.sh <idx>

if [[ -z "$1" ]]; then
    echo "No series index provided, stopping"
    echo "Usage: $0 <idx>"
    exit
fi

serie_idx=$1
N_SAMPLES=$(python -c "from config import N_SAMPLES; print(N_SAMPLES)")
SIM_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
LOG_FILE="slurm-outputs/$SIM_DIR/series-submitted.txt"

series_size=400

total=$(( ($N_SAMPLES / $series_size) + 1 ))

actual_start=$((serie_idx*series_size))
remaining=$(( $N_SAMPLES - $actual_start))
max=$(( $remaining < $series_size ? $remaining : $series_size-1))

echo "max: $max"

if (($serie_idx >= $total)); then
    echo "Series number $serie_idx exceeds maximum, exitting"
    exit
fi

if (($serie_idx > 25)); then
    echo "Safeguard exit"
    exit
fi


echo "Starting jobs serie $serie_idx in [0-$((total-1))]"
echo "thus $((serie_idx*series_size)) to $((serie_idx*series_size+max))"
echo "Range [$min-$max] submitted" >> $LOG_FILE
#                           v-- ensures max 100 jobs simultaneously
ID=$(sbatch --array=0-$max%100 --output=slurm-outputs/$SIM_DIR/simulation_%a.log --parsable launch-simulation-jobs.sh $serie_idx)

echo "Submitting with ${ID%%;*} as dependency, launch-job-series.sh $((serie_idx+1))"
sbatch --dependency=afterok:${ID%%;*} launch-job-series.sh $((serie_idx+1))
