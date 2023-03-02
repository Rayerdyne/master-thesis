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

- `sampling.py` runs the LHS, and scales it to the input ranges
- `split-samples.sh` splits the csv containing the samples into one sample per file (for simulations on the cluster)