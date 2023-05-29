#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Sbatcher
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/launcher-future_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1 # make sure it runs when all jobs are completed
#SBATCH --mem-per-cpu=1 # megabytes
#SBATCH --partition=batch
#SBATCH --array=1-4

echo coucou
series_idx=$1

N_SAMPLES=$(python -c "from config import N_SAMPLES; print(N_SAMPLES)")
SIM_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
LOG_FILE="slurm-outputs/$SIM_DIR/series-submitted.txt"

series_size=400
total=$(( ($N_SAMPLES / $series_size) + 1 ))

if ((series_idx >= total)); then
    echo Reached maximum index, stopping
    exit 0
fi

echo $((series_idx+1))
