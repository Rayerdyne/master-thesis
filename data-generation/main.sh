#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=BEGIN,END
#SBATCH --job-name=Main-simulation-script
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/main-%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10 # MB
#SBATCH --partition=batch

N_SAMPLES=$(python -c "from config import N_SAMPLES; print(N_SAMPLES)")
SIM_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
DATASET_NAME=$(python -c "from config import DATASET_NAME; print(DATASET_NAME)")
echo "Making a $N_SAMPLES simulation"

# srun python reference.py
# thus avoid allocating resources for this job
sbatch --wait launch-reference-job.sh

srun python sampling.py --sample-only

# Write header in dataset
rm -rf $SIM_DIR/sim*
echo "CapacityRatio,ShareFlex,ShareStorage,ShareWind,SharePV,rNTC,Cost_[E/MWh],Congestion_[h],PeakLoad_[MW],MaxCurtailment_[MW],MaxLoadShedding_[MW],Demand_[TWh],NetImports_[TWh],Curtailment_[TWh],Shedding_[TWh],LostLoad_[TWh],CF_gas,CF_nuc,CF_wat,CF_win,CF_sun" > $SIM_DIR/$DATASET_NAME
mkdir -p $SIM_DIR/logs/
touch $SIM_DIR/logs/finished.txt



## Jobs on slurm
# Due to the limitation of the number of jobs in the queue (500), one cannot launch them all at a time
# So this master job will launch them 200 at a time and wait for them

echo "Done. Now use launch-job-series.sh"
# inc=200
# max=$((N_SAMPLES-1))
# for (( i=0 ; i <= $max ; i += $inc ));
# do
#     a=$(( $i + $inc - 1))
#     up=$(( $a < $max ? $a : $max))
#     echo "Starting jobs range [$i-$up]"
#     #                           v-- ensures max 100 jobs simultaneously
#     sbatch --wait --array=$i-$up%100 --output=$SIM_DIR/logs/res_%A_%a.txt launch-simulation-jobs.sh
# done

