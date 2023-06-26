#!/bin/bash
#
#SBATCH --mail-user=f.straet@student.uliege.be
#SBATCH --mail-type=END
#SBATCH --job-name=runningreference
#SBATCH --time=1-05:00:00 # days-hh:mm:ss
#
#SBATCH --output=slurm-outputs/res_icref_%A.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10000 # megabytes 
#SBATCH --partition=batch
#

# export GAMSPATH=~/gams37.1_linux_x64_64_sfx
export GAMSPATH=~/gams42.5_linux_x64_64_sfx

cd simulations/LP-test/reference

# make sure the 'threads' option set in input file will not take precedence...
sed -i "/^Option threads=/d" UCM_h.gms
$GAMSPATH/gams UCM_h.gms threads=1 workSpace=10000 > ~/work/data-generation/slurm-outputs/ic-ref-gamsrun-$SLURM_JOBID.log
