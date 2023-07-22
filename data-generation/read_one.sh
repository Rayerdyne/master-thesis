#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --job-name=readone
#SBATCH --time=0-01:01:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/read_one-%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8000 # MB
#SBATCH --partition=batch

idx=0

# BASE_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
BASE_DIR="simulations/MILP-test"
DIRS=($BASE_DIR/sim-${idx}_*)
dir=${DIRS[0]}

srun python read_results.py --single $dir 4