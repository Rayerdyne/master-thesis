#!/bin/bash
#
#SBATCH --main-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET data generation
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=res_array_%A_%a.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8000 # megabytes
#SBATCH --partition=batch
#
#SBATCH --array=0-214

# Adapted from LaunchParallelJobs_carla.sh


F_HOME="/home/ulg/thermlab/fstraet"

FILES=($F_HOME/.../*)
CUR_FILE=${FILES[$SLURM_ARRAY_TASK_ID]}

# Load Python 3.9 and environment
module load Python/3.9.6-GCCcore-11.2.0
source $F_HOME/Dispa-SET/.env/bin/activate

export GAMSPATH=$F_HOME/gams37.1_linux_x64_64_sfx


echo "Job ID: $SLURM_JOBID"
echo "Job dir: $SLURM_SUBMIT_DIR"
echo "Running on file $CUR_FILE"

srun thing

echo "Job ID $SLURM_JOBID is finished"

