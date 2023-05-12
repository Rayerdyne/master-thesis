#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-reference
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/reference_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4800 # megabytes
#SBATCH --partition=batch

srun python reference.py