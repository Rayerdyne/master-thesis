#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-reference
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/reference_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1  # python is not parallel
#SBATCH --mem-per-cpu=4800 # megabytes
#SBATCH --partition=batch

# Starts the reference job on the cluster.
#
# Separating this run from the main.sh script allow to optimize resource usage, as
# main.sh doesn't need to carry out heavy computations.
#
# Usage: sbatch launch-reference-job.sh

srun python reference.py