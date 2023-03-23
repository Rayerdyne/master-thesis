# -*- coding: utf-8 -*-
"""
Reads the outputs of the simulations.

Copied from the Read_batch_simulation.py script from Carla's work.

@author: François Straet
"""

import os, sys

import pandas as pd

sys.path.append(os.path.abspath(".." + os.sep + ".."  + os.sep + "Dispa-SET"))

import dispaset as ds

from config import SIMULATIONS_FOLDER, SIMULATIONS_SUBFOLDER, SAMPLE_CSV_NAME

def get_simulation_dirs(path):
    """
    Returns a list of all the subdirectories of `path` that contain the results
    of a simulation
    """
    paths = os.listdir(path)
    paths = list(filter(lambda x: os.path.isfile(path + os.sep + "Results.gdx"), paths))
    paths = list(filter(lambda x: not os.path.isfile(path + os.sep + "debug.gdx"), paths))
    paths.remove("reference")

def read_data(path, inputs, results, data, i):
    """
    Reads the data related to one simulation and add it to a DataFrame

    :path:       path to the simulation directory to be read
    :inputs:     the inputs dict of the simulation
    :results:    the results dict of the simulation
    :data:       the DataFrame to be filled
    :i:          the row of the DataFrame to write at
    """
    fuel_power = ds.aggregate_by_fuel(results["OutputPower"], inputs, SpecifyFuels=None)
    capacities = ds.plot_zone_capacities(inputs, results, plot=False)

    zone_results = ds.get_result_analysis(inputs, results)

    lost_load = 0
    for key in ["LostLoad_MaxPower", "LostLoad_MinPower", "LostLoad_2D", "LostLoad_2U", "LostLoad_3U", "LostLoad_RampDown", "LostLoad_RampUp"]:
        if key in results:
            lost_load += results[key].sum().sum()
    
    # read pd.Series from csv
    sample = pd.read_csv(SIMULATIONS_SUBFOLDER + os.sep + SAMPLE_CSV_NAME).squeeze("columns")

    data.loc[i, :] = sample

    data.loc[i, "Cost_[E/MWh]"] = zone_results["Cost_kwh"]
    data.loc[i, "Congestion_[h]"] = sum(zone_results["Congestion"].values())

    data.loc[i, "PeakLoad_[MW]"] = zone_results["PeakLoad"]

    data.loc[i,'MaxCurtailment_[MW]'] = zone_results['MaxCurtailment']
    data.loc[i,'MaxLoadShedding_[MW]'] = zone_results['MaxShedLoad']
    
    data.loc[i,'Demand_[TWh]'] = zone_results['TotalLoad']/1E6
    data.loc[i,'NetImports_[TWh]']= zone_results['NetImports']/1E6
    
    data.loc[i,'Curtailment_[TWh]'] = zone_results['Curtailment']
    data.loc[i,'Shedding_[TWh]'] = zone_results['ShedLoad']
    
    data.loc[i,'LostLoad_[TWh]'] = lost_load / 1E6

    cf = {}
    for fuel in ["GAS", "NUC", "WAT", "WIN", "SUN"]:
        cf[fuel] = fuel_power[fuel].sum() / (capacities["PowerCapacity"][fuel].sum() * 8760)
        keyname = "CF_" + fuel.lower()
        data.loc[i, keyname] = cf[fuel]



def main():
    if len(sys.argv) >= 3:
        output_file = SIMULATIONS_SUBFOLDER + os.sep + sys.argv[2]

    if len(sys.argv) >= 2:
        SIMULATIONS_SUBFOLDER = SIMULATIONS_FOLDER + os.sep + sys.argv[1]
        print(f"Found subfolder name {sys.argv[1]}")
    else:
        print("No subfolder name given as argument, using default value")
    
    print(f"Reading simulations in {SIMULATIONS_SUBFOLDER}")

    paths = get_simulation_dirs(SIMULATIONS_SUBFOLDER)
    n = len(paths)
    data = pd.DataFrame(index=range(n))

    for i, path in enumerate(paths):
        current = SIMULATIONS_SUBFOLDER + os.sep + path
        inputs, results = ds.get_sim_resuts(path=current, cache=True)

        data = read_data(path, inputs, results, data, i)
    
    data.fillna(0, inplace=True)
    data.to_csv(output_file, index=False)
    print(f"Wrote {output_file}")
        

if __name__ == "__main__":
    main()