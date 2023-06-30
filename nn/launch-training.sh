#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-reference
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=logs/training-%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1  # python is not parallel
#SBATCH --mem-per-cpu=3200 # megabytes
#SBATCH --partition=batch

module load Python/3.9.6-GCCcore-11.2.0
module load TensorFlow/2.7.1-foss-2021b 

if [ "$1" = "--baselines" ]; then
    srun python baselines.py
else
    srun python train.py
fi