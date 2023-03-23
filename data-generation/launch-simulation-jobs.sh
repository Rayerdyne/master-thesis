#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-data-generation
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=res_array_%A_%a.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8000 # megabytes
#SBATCH --partition=batch
#
#SBATCH --array=0-10

# Adapted from LaunchParallelJobs_carla.sh


F_HOME="/home/ulg/thermlab/fstraet"

if [ -z "$1" ]; then
    echo "Missing argument"
    echo "Usage:"
    echo "    $0 <path-to-simulation-dirs>"
    exit
else
    BASE_DIR=$(cd $1; pwd)
    SIM_DIRS="$BASE_DIR/*"
fi

CUR_DIR=${SIM_DIRS[$SLURM_ARRAY_TASK_ID]}

# Load Python 3.9 and environment
module load Python/3.9.6-GCCcore-11.2.0
source $F_HOME/Dispa-SET/.env/bin/activate

export GAMSPATH=$F_HOME/gams37.1_linux_x64_64_sfx


echo "Job ID: $SLURM_JOBID"
echo "Job dir: $SLURM_SUBMIT_DIR"
echo "Running simulation dir: $CUR_DIR"
cd $CUR_DIR

srun $GAMSPATH/gams UCM_h.gms > $CUR_DIR/gamsrun.log
# srun pwd > "gamsrun$SLURM_SUBMIT_DIR.log"

echo "Job ID $SLURM_JOBID is finished"

