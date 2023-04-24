#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Simulation-main-script
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/main-%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8000 # MB
#SBATCH --partition=batch

N_SAMPLES=$(python -c "from config import N_SAMPLES; print(N_SAMPLES)")
echo "Making a $N_SAMPLES simulation"

srun python reference.py

srun python sampling.py --sample-only

sbatch launch-simulation-jobs.sh --array=1-$N_SAMPLES