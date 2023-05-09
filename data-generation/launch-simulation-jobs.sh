#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Dispa-SET-data-generation
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/res_365_%A_%a.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=600 # megabytes, 600*cpus=4800 = typical amount of memory required
#SBATCH --partition=batch
#
# called via main.sh with
# sbatch --array=1-$N_SAMPLES
# disable SBATCH --array=0-1

# Adapted from LaunchParallelJobs_carla.sh

F_HOME="/home/ulg/thermlab/fstraet"
LAUNCH_DIR=$(pwd)

BASE_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
DATASET_NAME=$(python -c "from config import DATASET_NAME; print(DATASET_NAME)")

# CUR_DIR=${SIM_DIRS[$SLURM_ARRAY_TASK_ID]}

# Load Python 3.9 and environment
module load Python/3.9.6-GCCcore-11.2.0
source $F_HOME/Dispa-SET/.env/bin/activate

export GAMSPATH=$F_HOME/gams37.1_linux_x64_64_sfx


echo "Job ID: $SLURM_JOBID"
echo "Job dir: $SLURM_SUBMIT_DIR"
echo "Running simulation $SLURM_ARRAY_TASK_ID"

# Prepare simulation files
srun python sampling.py --prepare-one $SLURM_ARRAY_TASK_ID

DIRS=($BASE_DIR/sim-${SLURM_ARRAY_TASK_ID}_*)
CUR_DIR=${DIRS[0]}

# Run the GAMS simulation
cd $CUR_DIR
echo "File prepared, starting simulation..."
#                                                          from `seff`, one can see the memory used is typically around 4.5
srun $GAMSPATH/gams UCM_h.gms --threads=4 --asyncThreads=4 --workSpace=4800 > $BASE_DIR/logs/gamsrun-$SLURM_ARRAY_TASK_ID.log
cd $LAUNCH_DIR

# Fetch the results
echo "Simulation ran, reading results..."
srun python read_results.py --single $CUR_DIR 

# do some cleaning...
srun rm -rf $CUR_DIR/
# srun pwd > "gamsrun$SLURM_SUBMIT_DIR.log"

echo "Simulation $SLURM_ARRAY_TASK_ID is done (job id $SLURM_JOBID)" >> $BASE_DIR/logs/finished.txt
echo "Job ID $SLURM_JOBID n°$SLURM_ARRAY_TASK_ID is finished"

