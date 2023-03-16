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


## Runs of sampling.py

### ConfigFile: ConfigEU

NB: this config file looks outdated, there is no line: "this is the end of the config file, this should be line 325"

```
Traceback (most recent call last):
  File "/home/f/Unif/tfe/work/data-generation/sampling.py", line 45, in <module>
    sim_data = ds.build_simulation(config)
  File "/home/f/Unif/tfe/Dispa-SET/dispaset/preprocessing/preprocessing.py", line 46, in build_simulation
    SimData = build_single_run(config)
  File "/home/f/Unif/tfe/Dispa-SET/dispaset/preprocessing/build.py", line 132, in build_single_run
    CostCurtailment = NodeBasedTable('CostCurtailment', config, default=config['default']['CostCurtailment'])
KeyError: 'CostCurtailment'
```

### ConfigFile: ConfigTest_Matijs

Builds successfully, but with warnings and error in output creation:

```
[ERROR   ] (check_units): Non-null value(s) have been found for key PartLoadMin in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_units): Non-null value(s) have been found for key MinEfficiency in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_units): Non-null value(s) have been found for key StartUpTime in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_sto): The Storage capacity for unit DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (check_AvailabilityFactors): The Availability factor of unit ES_HROR_WAT for technology HROR should be between 0 and 1. There are 24 values above 1.0 and 0 below 0.0
[ERROR   ] (check_AvailabilityFactors): The Availability factor of unit SE_HROR_WAT for technology HROR should be between 0 and 1. There are 1632 values above 1.0 and 0 below 0.0
[ERROR   ] (check_sto): The Storage capacity for unit [81] - DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (check_sto): The Storage capacity for unit [81] - DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (build_single_run): In zone: NO there is insufficient conventional + renewable generation capacity of: 9939.360228868842. If NTC + storage is not sufficient ShedLoad in NO is likely to occour. Check the inputs!
[ERROR   ] (solve_high_level): The following error occured when trying to solve the model in gams: GAMS return code not 0 (3), check /tmp/tmpm1izlixz/_gams_py_gjo0.lst for more details
```

```
Traceback (most recent call last):
  File "/home/f/Unif/tfe/work/data-generation/sampling.py", line 45, in <module>
    sim_data = ds.build_simulation(config)
  File "/home/f/Unif/tfe/Dispa-SET/dispaset/preprocessing/preprocessing.py", line 54, in build_simulation
    new_profiles = mid_term_scheduling(config, mts_plot=mts_plot, TimeStep=MTSTimeStep)
  File "/home/f/Unif/tfe/Dispa-SET/dispaset/preprocessing/preprocessing.py", line 228, in mid_term_scheduling
    temp_results = gdx_to_dataframe(
  File "/home/f/Unif/tfe/Dispa-SET/dispaset/misc/gdx_handler.py", line 324, in gdx_to_dataframe
    out[symbol] = pd.DataFrame(columns=pd_index, index=out['OutputPower'].index)
KeyError: 'OutputPower'
```

### ConfigFile: ConfigTest_Matijs1

Errors:
```
[ERROR   ] (check_units): Non-null value(s) have been found for key PartLoadMin in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_units): Non-null value(s) have been found for key MinEfficiency in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_units): Non-null value(s) have been found for key StartUpTime in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_sto): The Storage capacity for unit DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (check_AvailabilityFactors): The Availability factor of unit ES_HROR_WAT for technology HROR should be between 0 and 1. There are 24 values above 1.0 and 0 below 0.0
[ERROR   ] (check_AvailabilityFactors): The Availability factor of unit SE_HROR_WAT for technology HROR should be between 0 and 1. There are 1632 values above 1.0 and 0 below 0.0
[ERROR   ] (check_sto): The Storage capacity for unit [81] - DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (check_sto): The Storage capacity for unit [81] - DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (build_single_run): In zone: NO there is insufficient conventional + renewable generation capacity of: 9939.360228868842. If NTC + storage is not sufficient ShedLoad in NO is likely to occour. Check the inputs!
[ERROR   ] (solve_high_level): The following error occured when trying to solve the model in gams: GAMS return code not 0 (3), check /tmp/tmpsd363sf8/_gams_py_gjo0.lst for more details
```

Fails with the same error than ConfigTest_Matijs

### ConfigFile: ConfigTest_Matijs2

Errors: 
```
[ERROR   ] (check_units): Non-null value(s) have been found for key PartLoadMin in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_units): Non-null value(s) have been found for key MinEfficiency in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_units): Non-null value(s) have been found for key StartUpTime in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_sto): The Storage capacity for unit DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (check_AvailabilityFactors): The Availability factor of unit ES_HROR_WAT for technology HROR should be between 0 and 1. There are 24 values above 1.0 and 0 below 0.0
[ERROR   ] (check_AvailabilityFactors): The Availability factor of unit SE_HROR_WAT for technology HROR should be between 0 and 1. There are 1632 values above 1.0 and 0 below 0.0
[ERROR   ] (check_sto): The Storage capacity for unit [81] - DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (check_sto): The Storage capacity for unit [81] - DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (build_single_run): In zone: NO there is insufficient conventional + renewable generation capacity of: 9939.360228868842. If NTC + storage is not sufficient ShedLoad in NO is likely to occour. Check the inputs!
[ERROR   ] (solve_high_level): The following error occured when trying to solve the model in gams: GAMS return code not 0 (3), check /tmp/tmpn5tc61vt/_gams_py_gjo0.lst for more details
```

Fails with the same error than ConfigTest_Matijs

### ConfigFile: ConfigTest_Matijs_MILP

Errors: 
```
[ERROR   ] (check_units): Non-null value(s) have been found for key PartLoadMin in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_units): Non-null value(s) have been found for key MinEfficiency in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_units): Non-null value(s) have been found for key StartUpTime in the power plant list. This cannot be modelled with the LP clustered formulation and will therefore not be considered.
[ERROR   ] (check_sto): The Storage capacity for unit DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (check_AvailabilityFactors): The Availability factor of unit ES_HROR_WAT for technology HROR should be between 0 and 1. There are 24 values above 1.0 and 0 below 0.0
[ERROR   ] (check_AvailabilityFactors): The Availability factor of unit SE_HROR_WAT for technology HROR should be between 0 and 1. There are 1632 values above 1.0 and 0 below 0.0
[ERROR   ] (check_sto): The Storage capacity for unit [81] - DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (check_sto): The Storage capacity for unit [81] - DE_HDAM_WAT is prohibitively high. More than one year at full power is required to discharge the reservoir
[ERROR   ] (build_single_run): In zone: NO there is insufficient conventional + renewable generation capacity of: 9939.360228868842. If NTC + storage is not sufficient ShedLoad in NO is likely to occour. Check the inputs!
[ERROR   ] (solve_high_level): The following error occured when trying to solve the model in gams: GAMS return code not 0 (3), check /tmp/tmpvhpvhm46/_gams_py_gjo0.lst for more details
```

Fails with same error than ConfigTest_Matijs