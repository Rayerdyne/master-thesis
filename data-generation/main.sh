#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --job-name=Main-simulation-script
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/main-%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=64 # MB
#SBATCH --partition=batch

# High-level script to submit all the jobs required to create a dataset, as configured in
# `config.py` file.
#
# 1- Prepare the header line in the future dataset, and various log files
# 2- Runs the reference simulation
# 3- Runs the sampling
# 4- Starts the first series (NB: series automatically submit the next one)
#
# Usage: sbatch main.sh

N_SAMPLES=$(python -c "from config import N_SAMPLES; print(N_SAMPLES)")
SIM_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
SIM_NAME=$(python -c "from config import SIMULATIONS_NAME; print(SIMULATIONS_NAME)")
DATASET_NAME=$(python -c "from config import DATASET_NAME; print(DATASET_NAME)")
echo "Making a $N_SAMPLES simulation"

# Write header in dataset
mkdir -p $SIM_DIR
mkdir -p $SIM_NAME
rm -rf $SIM_DIR/sim*
echo "CapacityRatio,ShareFlex,ShareStorage,ShareWind,SharePV,rNTC,Cost_[E/MWh],Congestion_[h],PeakLoad_[MW],MaxCurtailment_[MW],MaxLoadShedding_[MW],Demand_[TWh],NetImports_[TWh],Curtailment_[TWh],Shedding_[TWh],LostLoad_[TWh],TotalRESGeneration_[TWh],CurtailmentToRESGeneration_[%],TotalGeneration_[TWh],ShareResGeneration_[%],CF_gas,CF_nuc,CF_wat,CF_win,CF_sun,GAMS_error" > $SIM_DIR/$DATASET_NAME
mkdir -p slurm-outputs/$SIM_NAME/
mkdir -p slurm-outputs/$SIM_NAME/lst_files/
touch slurm-outputs/$SIM_NAME/finished.txt

# srun python reference.py
# thus avoid allocating resources for this job
sbatch --wait --output=slurm-outputs/$SIM_NAME/reference_%A.log launch-reference-job.sh

srun --mem-per-cpu=1000 python sampling.py --sample-only

## Jobs on slurm
# Due to the limitation of the number of jobs in the queue (500), one cannot launch them all at a time
# So this master job will launch them 200 at a time and wait for them

echo "Done. Now calling launch-job-series.sh 0"
./launch-job-series.sh 0
