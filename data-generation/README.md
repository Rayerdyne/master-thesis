# Data generation notes

Exploring other sampling techniques (cf [here](https://scikit-optimize.github.io/stable/auto_examples/sampler/initial-sampling-method.html)), it looks like Latin Hypercube Sampling (LHS) is still performant. Alternatives are:

- Sobol sequences, said to have good low-discrepancy properties for higher dimensions input space. In this case the dimension will not be so high (±6)
- Halton sequences looked good too, however it is possible to observe correlation at the beginning of the sequence
- Hammersly sequences, same as Halton with one dimension sampled in grid

With `pyDOE`, the criterion for the LHS optimisation is to be choosen among (from [here](https://pythonhosted.org/pyDOE/randomized.html#latin-hypercube-lhs)):

- center
- maximin
- certermaximin
- correlation

I think the best option is maximin, as it has better coverage of the input space. Having slight correlation should not be an issue in our use case. 

## Files

- `config.py` holds the data about the simulation to be set up and run, most importantly:
    - the number of simulations (points on the LHS)
    - the output folder for the simulations
    - and the names of other files

    The other files make reference to this one (`python -c "import x; print(x)"`) to set their variables.
- `main.sh` sbatch-able script that starts all the jobs for a complete set of simulations, configured in `config.py`.
- `reference.py` runs the reference simulation and writes necessary info to `$SIMULATION_FOLDER/reference-info.json`
- `sampling.py` runs the LHS, and scales it to the input ranges, and prepares the GAMS file for the simulation
- `launch-simulation-jobs.sh` starts jobs to do the simulations. 
    1. Prepares the file (`sampling.py --prepare-one $CUR_DIR`)
    1. Run the simulation (call to GAMS)
    1. to be run, then one to call `read_results.py --single` to fetch its results. Finally, removes large simulations files to avoid exceeding the storage limit.
- `read_results.py` fetches the outputs of the GAMS run. If called with no arguments, fetches all the results from each simulation, if called with `--single folder` only fetches the results in that folder.
