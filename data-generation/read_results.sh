#!/bin/bash

#SBATCH --job-name Read_results

cd ~/work/data-generation

# Load Python 3.9 and environment
module load Python/3.9.6-GCCcore-11.2.0
source ~/Dispa-SET/.env/bin/activate

python read_results.py
echo "Job finished"
