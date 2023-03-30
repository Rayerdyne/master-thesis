# -*- coding: utf-8 -*-
"""
Reads the outputs of the simulations.

Copied from the Read_batch_simulation.py script from Carla's work.

@author: François Straet
"""

import os, sys

import pandas as pd

from config import SIMULATIONS_FOLDER, SIMULATIONS_SUBFOLDER, SAMPLE_CSV_NAME

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

def read_data(path, inputs, results, data, i):
    """
    Reads the data related to one simulation and returns it as a row

    :path:       path to the simulation directory to be read
    :inputs:     the inputs dict of the simulation
    :results:    the results dict of the simulation
    """
    print(f"Reading data from path: {path} -> {SIMULATIONS_SUBFOLDER + os.sep + path}")
    fuel_power = ds.aggregate_by_fuel(results["OutputPower"], inputs, SpecifyFuels=None)
    capacities = ds.plot_zone_capacities(inputs, results, plot=False)

    zone_results = ds.get_result_analysis(inputs, results)

    lost_load = 0
    for key in ["LostLoad_MaxPower", "LostLoad_MinPower", "LostLoad_2D", "LostLoad_2U", "LostLoad_3U", "LostLoad_RampDown", "LostLoad_RampUp"]:
        if key in results:
            lost_load += results[key].sum().sum()
    
    # read pd.Series from csv
    # then add elements to the row
    row = pd.read_csv(SIMULATIONS_SUBFOLDER + os.sep + path + os.sep + SAMPLE_CSV_NAME, index_col=1).squeeze("columns")

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


def foo(path):
    row = pd.read_csv(SIMULATIONS_SUBFOLDER + os.sep + path + os.sep + SAMPLE_CSV_NAME, index_col=0).squeeze("columns")
    a = path[:3]
    b = path[3:6]
    c = path[6:9]
    row.loc["aa"] = a
    row.loc["bb"] = b
    row.loc["cc"] = c
    return row
    

def main():
    print(f"Reading simulations in {SIMULATIONS_SUBFOLDER}")

    paths = get_simulation_dirs(SIMULATIONS_SUBFOLDER)
    print(f"Paths found: {paths}")
    n = len(paths)
    
    for i, path in enumerate(paths):
        current = SIMULATIONS_SUBFOLDER + os.sep + path
        inputs, results = ds.get_sim_results(path=current, cache=True)

        row = read_data(path, inputs, results, data, i)
        if i == 0:
            data = pd.DataFrame(index=range(n), columns=row.index, dtype=float)
            
        data.loc[i,:] = row
    
    data.fillna(0, inplace=True)
    output_file = SIMULATIONS_SUBFOLDER + SAMPLE_CSV_NAME
    data.to_csv(output_file, index=False)
    print(f"Wrote {output_file}")
        

if __name__ == "__main__":
    main()
