# -*- coding: utf-8 -*-
"""
Reads the outputs of the simulations.

Usage: 
    python read_results.py
            Reads all the results in the SIMULATION_DIR path 
    python read_results.py --single <path>
            Reads the results for one simulation directory, at <path>

Adapted from the Read_batch_simulation.py script from Carla's work.

@author: François Straet
"""

import os, re, sys

import pandas as pd

from config import DATASET_NAME, SIMULATIONS_DIR, SAMPLES_CSV_NAME

sys.path.append(os.path.abspath(".." + os.sep + ".."  + os.sep + "Dispa-SET"))

import dispaset as ds


def get_simulation_dirs(parent):
    """
    Returns a list of all the subdirectories of `path` that contain the results
    of a simulation
    """
    def is_valid_path(path):
        path = parent + os.sep + path
        b1 = os.path.isfile(path + os.sep + "Results.gdx")
        if not b1:
            print(f"Refusing {path} because no results")
        b2 = not os.path.isfile(path + os.sep + "debug.gdx")
        if not b2:
            print(f"Should be refusing {path} because debug")
        b3 = not path.endswith("reference")
        if not b3:
            print(f"Refusing {path} because reference")
        # return b1 and b2 and b3
        return b1 and b3

    paths = os.listdir(parent)
    return list(filter(is_valid_path, paths))

def read_data(path):
    """
    Reads the data related to one simulation and returns it as a row

    :path:       path to the simulation directory to be read
    """
    print(f"Reading data from path: {path}")
    inputs, results = ds.get_sim_results(path=path, cache=True)

    fuel_power = ds.aggregate_by_fuel(results["OutputPower"], inputs, SpecifyFuels=None)
    capacities = ds.plot_zone_capacities(inputs, results, plot=False)

    zone_results = ds.get_result_analysis(inputs, results)

    lost_load = 0
    for key in ["LostLoad_MaxPower", "LostLoad_MinPower", "LostLoad_2D", "LostLoad_2U", "LostLoad_3U", "LostLoad_RampDown", "LostLoad_RampUp"]:
        if key in results:
            lost_load += results[key].sum().sum()
    
    # read pd.Series from csv
    # then add elements to the row
    m = re.search("/sim-(\d+)_", path)
    # m[0]: entire match, m[1]: first group
    sample_index = int(m[1])
    samples = pd.read_csv(SIMULATIONS_DIR + os.sep + SAMPLES_CSV_NAME, index_col=0)

    row = samples.loc[sample_index,:]
    print(f"Read single index:  {sample_index}")

    row.loc["Cost_[E/MWh]"] = zone_results["Cost_kwh"]
    row.loc["Congestion_[h]"] = sum(zone_results["Congestion"].values())

    row.loc["PeakLoad_[MW]"] = zone_results["PeakLoad"]

    row.loc['MaxCurtailment_[MW]'] = zone_results['MaxCurtailment']
    row.loc['MaxLoadShedding_[MW]'] = zone_results['MaxShedLoad']
    
    row.loc['Demand_[TWh]'] = zone_results['TotalLoad']/1E6
    row.loc['NetImports_[TWh]']= zone_results['NetImports']/1E6
    
    row.loc['Curtailment_[TWh]'] = zone_results['Curtailment']
    row.loc['Shedding_[TWh]'] = zone_results['ShedLoad']
    row.loc['LostLoad_[TWh]'] = lost_load / 1E6

    cf = {}
    for fuel in ["GAS", "NUC", "WAT", "WIN", "SUN"]:
        cf[fuel] = fuel_power[fuel].sum() / (capacities["PowerCapacity"][fuel].sum() * 8760)
        keyname = "CF_" + fuel.lower()
        row.loc[keyname] = cf[fuel]

    return row


def read_all():
    """
    Reads all the simulation results in the parent directory SIMULATIONS_DIR.
    """
    print(f"Reading simulations in {SIMULATIONS_DIR}")

    dirs = get_simulation_dirs(SIMULATIONS_DIR)
    print(f"Directories found: {dirs}")
    n = len(dirs)
    
    for i, cur_dir in enumerate(dirs):
        path = SIMULATIONS_DIR + os.sep + cur_dir
        row = read_data(path)

        if i == 0:
            data = pd.DataFrame(index=range(n), columns=row.index, dtype=float)
            
        data.loc[i,:] = row
    
    data.fillna(0, inplace=True)
    output_file = SIMULATIONS_DIR + DATASET_NAME
    data.to_csv(output_file, index=False)
    print(f"Wrote {output_file}")

def read_single(path, gams_error=0):
    """
    Reads the results for a single simulation, located at given path, and outputs it.

    :path:       path to the simulation to be read
    :gams_error: 1 if not gams log ends with execution error status (division by zero), else 0
    """
    row = read_data(path)
    row["GAMS_error"] = gams_error
    # output via stdout
    # if there were header, it would be:
    # CapacityRatio,ShareFlex,ShareStorage,ShareWind,SharePV,rNTC,Cost_[E/MWh],Congestion_[h],PeakLoad_[MW],MaxCurtailment_[MW],MaxLoadShedding_[MW],Demand_[TWh],NetImports_[TWh],Curtailment_[TWh],Shedding_[TWh],LostLoad_[TWh],CF_gas,CF_nuc,CF_wat,CF_win,CF_sun,GAMS_error
    dataset_path = SIMULATIONS_DIR + os.sep + DATASET_NAME
    pd.DataFrame(row).T.to_csv(dataset_path, index=False, header=False, mode="a")


def main():
    try:
        #                                 v-- non empty strings truthy
        if sys.argv[1] == "--single" and sys.argv[2]:
            gams_error = sys.argv[3] if len(sys.argv) >= 4 else 0
            read_single(sys.argv[2], gams_error)
            return

    except IndexError:
        pass
    
    read_all()

if __name__ == "__main__":
    main()
