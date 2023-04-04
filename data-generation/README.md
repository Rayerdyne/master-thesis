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
- `sampling.py` runs the LHS, and scales it to the input ranges
- `config.py` stores variable that are accessed by different scripts
- `read_results.py` fetches the ouptput of the execution of the model and output it in csv format
- `utils_francois.py` holds the test version of my `adjust_capacity` function
- `launch-simulation-jobs.sh`, and do it on slurm