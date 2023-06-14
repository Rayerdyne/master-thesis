# to be adapted
export GAMSPATH=~/gams42.5_linux_x64_64_sfx

cd ../../
echo "Using configuration files given in data-generation/config.py"
python reference.py

$GAMSPATH/gams UCM_h.gms threads=1 workSpace=25400 > reference-simulation.log
# NB: not on the cluster, then one can use more than 1 threads without perturbating the nodes!


# # To test "adjusted" simulation settings:
# python sampling.py --sample-only
# BASE_DIR=$(python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")

# # For each simulation:
# python sampling.py --prepare-one $simulation_idx

# DIRS=($BASE_DIR/sim-${simulation_idx}_*)
# CUR_DIR=${DIRS[0]}
# cd $CUR_DIR

# $GAMSPATH/gams UCM_h.gms threads=1 workSpace=25400 > gamsrun_$simulation_idx.log

# # Optionnally:
# python read_results.py --single $CUR_DIR