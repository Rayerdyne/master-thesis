# -*- coding: utf-8 -*-
"""
Defines samples points on the input space for the expensive simulation to be run on.

Options:
- --sample-only: only draw samples and write sample to their folder
- --prepare-one <dir>: only create files for the directory *dir* containing a sample

@author: François Straet
"""

import json, os, sys, pathlib

import numpy as np
import pandas as pd

from pyDOE import lhs

sys.path.append(os.path.abspath(".." + os.sep + ".."  + os.sep + "Dispa-SET"))

import dispaset as ds

from config import *
from reference import ReferenceInfo, build_reference

try:
    sample_only = (sys.argv[1] == "--sample-only")
    prepare_one = (sys.argv[1] == "--prepare-one" and sys.argv[2])
except IndexError:
    sample_only = False
    prepare_one = False

# from Carla's work
capacity_ratio_range = (0.5, 1.8)
share_flex_range     = (0.01, 0.99)
share_storate_range  = (0, 0.5)
share_wind_range     = (0, 0.5)
share_pv_range       = (0.2, 0.5)
rntc_range           = (0, 0.7)    

ranges = [capacity_ratio_range, share_flex_range,
          share_storate_range,  share_wind_range,
          share_pv_range,       rntc_range]

ranges_name = ["Capacity ratio", "Share flexible",
               "Share storage",  "Share wind",
               "Share PV",       "rNTC"]

N_DIMS = len(ranges)

def main():
    if prepare_one:
        cur_folder = sys.argv[2]
        print(f"Preparing files in {cur_folder}")
        sample_path = cur_folder + os.sep + SAMPLE_CSV_NAME
        sample = pd.read_csv(sample_path, index_col=0).squeeze("columns")
        prepare_simulation_files(sample, cur_folder)
        return

    print(f"Writing {'samples' if sample_only else 'simulations'} in {SIMULATIONS_DIR}")

    print(f"Generating samples in ranges {ranges}")
    # samples is numpy array
    samples = lhs(N_DIMS, samples=N_SAMPLES, criterion=CRITERION)

    # scale sample on [0,1] interval to actual ranges
    for i, interval in enumerate(ranges):
        min = interval[0]
        max = interval[1]
        samples[:,i] *= max - min
        samples[:,i] += min
    
    if WRITE_POINTS_TO_CSV or sample_only:
        df = pd.DataFrame(samples, columns=ranges_name)

        out_name = SIMULATIONS_DIR + os.sep + SAMPLES_CSV_NAME
        print(f"Output samples to file: {out_name}")

        df.to_csv(out_name, index_label="Index")
    
    build_simulations(samples, sample_only)
    print(f"Simulations successfully written in {SIMULATIONS_DIR}")

def format_folder_name(index, sample):
    """
    Produces a nicely formatted folder name
    
    - `index`: the index of the sample
    - `sample`: a python list containing all the values
    """
    return f"sim-{index}_" + "-".join([f"{x:.2f}" for x in sample])
    # return f"sim-{i}_" + np.array2string(sample, separator="-", formatter={'float_kind': lambda x: f"{x:.2f}" })[1:-1]


def build_simulations(samples, sample_only=False):
    """
    Builds the simulations, or only writes samples, based on the samples array

    - `samples`: np.ndarray, all the samples
    - `sample_only`: bool, if true, only write the samples files.
    """
    nb = len(samples)
    for i, sample in enumerate(samples):
        print(f"Simulation {i} / {nb}, {sample}")
        
        cur_folder = SIMULATIONS_DIR + os.sep + format_folder_name(i, sample.tolist())
        
        if not sample_only:
            prepare_simulation_files(sample, cur_folder)
        else:
            # if we did not prepare simulation files, we need to create the folder
            pathlib.Path(cur_folder).mkdir(parents=True, exist_ok=True)

        # Needed because the directory name is rounded
        coordinates = pd.Series(sample, index=["CapacityRatio", "ShareFlex", "ShareStorage", "ShareWind", "SharePV", "rNTC"])
        coordinates.name = "LHS-sample"
        coordinates.to_csv(cur_folder + os.sep + SAMPLE_CSV_NAME)

def prepare_simulation_files(sample, cur_folder):
    """
    Creates the files needed for the simulation to be run
    """
    if not os.path.exists(REFERENCE_INFO_FILE):
        build_reference(REFERENCE_INFO_FILE)

    refinfo = ReferenceInfo.deserialize(REFERENCE_INFO_FILE)
    peak_load, flex_units, slow_units, CF_wton, CF_pv = refinfo.tolist()
    capacity_ratio, share_flex, share_sto, share_wind, share_pv, rNTC = sample

    # in the first iteration, we load the input data from the original simulation directory:
    data = ds.adjust_capacity(REFERENCE_SIMULATION_DIR, ('BATS','OTH'), singleunit=True, 
                                value=peak_load*share_sto)
    
    # then we use the dispa-set fuction to adjust the installed capacities:
    data = ds.adjust_flexibility(data, flex_units, slow_units, share_flex, singleunit=True)
    #SimData = ds.adjust_capacity(SimData,('COMC','GAS'),singleunit=True,value=load_max*cap*flex)
    #SimData = ds.adjust_capacity(SimData,('STUR','NUC'),singleunit=True,value=load_max*cap*(1-flex))
    
    # dispa-set function to adjust the ntc:
    data = ds.adjust_ntc(data, value=rNTC)
    
    # For wind and PV, the units should be lumped into a single unit:
    data = ds.adjust_capacity(data, ('WTON','WIN'),
                            value=peak_load*capacity_ratio*share_wind/CF_wton, singleunit=True)
    
    # In this last iteration, the new gdx file is written to the simulation folder:
    data = ds.adjust_capacity(data, ('PHOT','SUN'),
                            value=peak_load*capacity_ratio*share_pv/CF_pv, singleunit=True,
                            write_gdx=True, dest_path=cur_folder)

if __name__ == "__main__":
    main()
