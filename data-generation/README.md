# Data generation notes

## Sampling technique
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

- `Database/` folder containing all the Dispa-SET input data
- `Database/rescale.py` rescale some variable in the database
- `ConfigFiles/` folder containing the different Dispa-SET configuration files
- `simulations/` folder containing the simulations outputs

### Python code
- `config.py` holds the data about the simulation to be set up and run, most importantly:
    - the number of simulations (points on the LHS)
    - the output folder for the simulations
    - and the names of other files

    The other files make reference to this one (`python -c "import x; print(x)"`) to set their variables.
- `reference.py` runs the reference simulation and writes necessary info to `$SIMULATION_FOLDER/reference-info.json`
- `sampling.py` runs the LHS, and scales it to the input ranges, and prepares the GAMS file for the simulation
- `read_results.py` fetches the outputs of the GAMS run. If called with no arguments, fetches all the results from each simulation, if called with `--single folder` only fetches the results in that folder.

### Scripts
- `main.sh` sbatch-able script that prepares terrain for running simulations, configured in `config.py`. After executing it, you have to submit the actual simulation jobs with `launch-job-series.sh`
- `launch-job-series.sh` shell script. Adds a series of job to the queue, as it is not large enough to hold all the 
- `launch-simulation-jobs.sh` slurm script, starts jobs to do the simulations. 
    1. Prepares the file (`sampling.py --prepare-one $i`), where `$i` refers to an index in [0, $N_SAMPLES-1]
    1. Run the simulation (call to GAMS)
    1. to be run, then one to call `read_results.py --single` to fetch its results. Finally, removes large simulations files to avoid exceeding the storage limit.

    NB: Limits GAMS solver to 4 CPUs.
- `launch-reference-job.sh` slurm script. For resource efficiency reasons, to avoid having `main.sh` requiring significant resources on the cluster. Runs `reference.py`.
