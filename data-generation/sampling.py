# -*- coding: utf-8 -*-
"""
Defines samples points on the input space for the expensive simulation to be run on.

@author: François Straet
"""

import os, sys

import numpy as np
import pandas as pd

from pyDOE import lhs

sys.path.append(os.path.abspath(".." + os.sep + ".."  + os.sep + "Dispa-SET"))

import dispaset as ds

from config import *

config = ds.load_config_excel("ConfigFiles" + os.sep + "ConfigTest_Francois.xlsx")
config["SimulationDirectory"] = REFERENCE_SIMULATION_FOLDER 

if TESTING:
    config["StartDate"] = (2022, 1, 1, 0, 0, 0)
    config["StopDate"] = (2022, 12, 31, 0, 0, 0)


# Build base simulation directory
print("#-#-#-#-#-#-# Build simulation")
sim_data = ds.build_simulation(config)
print("#-#-#-#-#-#-# Build simulation end")

# Extract some significant values from the config:
peak_load = sim_data["parameters"]["Demand"]["val"][0].sum(axis=0).max()

availability_factors = sim_data["parameters"]["AvailabilityFactor"]["val"].mean(axis=1)
af_df = pd.DataFrame(availability_factors, index=sim_data["sets"]["au"], columns=["availability_factor_avg"])

CF_pv = af_df.filter(like="PHOT", axis=0).mean().loc["availability_factor_avg"]
CF_wton_list0 = af_df.filter(like="WindOn", axis=0)
CF_wton_list1 = af_df.filter(like="WTON", axis=0)
CF_wton_list = pd.concat([CF_wton_list0, CF_wton_list1])
CF_wton = CF_wton_list.mean().loc["availability_factor_avg"]

units = sim_data["units"]
flex_units = units[ units.Fuel.isin( ['GAS','HRD','OIL','BIO','LIG','PEA','NUC','GEO'] ) & (units.PartLoadMin < 0.5) & (units.TimeUpMinimum <5)  & (units.RampUpRate > 0.01)  ].index
slow_units = units[ units.Fuel.isin( ['GAS','HRD','OIL','BIO','LIG','PEA','NUC','GEO'] ) & ((units.PartLoadMin >= 0.5) | (units.TimeUpMinimum >=5)  | (units.RampUpRate <= 0.01)   )  ].index
sto_units  = units[ units.Fuel.isin( ['OTH'] ) ].index
wind_units = units[ units.Fuel.isin( ['WIN'] ) ].index 
pv_units   = units[ units.Technology == 'PHOT'].index   
hror_units = units[ units.Technology == 'HROR'].index   
coal_units = units[units.Fuel.isin(["HRD"])].index
variable_costs = sim_data["parameters"]["CostVariable"]["val"]
for u in coal_units:
    idx = coal_units.get_loc(u)
    variable_cost = variable_costs[idx].mean()
    print(f"Variable cost for {u} (idx: {idx}): {variable_cost}")

ref = {}
ref['overcapacity'] = (units.PowerCapacity[flex_units].sum() + units.PowerCapacity[slow_units].sum() + units.PowerCapacity[sto_units].sum()) / peak_load
ref['share_flex'] =   units.PowerCapacity[flex_units].sum() / (units.PowerCapacity[flex_units].sum() + units.PowerCapacity[slow_units].sum())
ref['share_sto'] =    units.PowerCapacity[sto_units].sum() / peak_load
ref['share_wind'] =   units.PowerCapacity[wind_units].sum() / peak_load * CF_wton
ref['share_pv'] =     units.PowerCapacity[pv_units].sum() / peak_load * CF_pv


# Computing rNTCs
h_mean = sim_data['parameters']['FlowMaximum']['val'].mean(axis=1)
NTC = pd.DataFrame(h_mean, index=sim_data['sets']['l'], columns=['FlowMax_hmean']).groupby(level=0).sum()

countries = sim_data['sets']['n']
max_load = sim_data['parameters']['Demand']['val'][0].max(axis=1)
    
peak_load_df = pd.DataFrame(max_load, index=countries, columns=['max_load'])
    
for c in countries:
    ntc = 0
    for l in NTC.index:
        if c in l: 
            ntc += NTC.loc[l,'FlowMax_hmean']
    peak_load_df.loc[c,'rNTC'] = ntc / 2 / peak_load_df.loc[c,'max_load']

peak_load_df['weigthed'] = peak_load_df['max_load'] * peak_load_df['rNTC'] / peak_load_df['max_load'].sum()

ref['rNTC'] = peak_load_df['weigthed'].sum()     



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
    print(f"Writing simulations in {SIMULATIONS_SUBFOLDER}")

    print(f"Reference simulation: {ref}")
    print(f"CF pv: {CF_pv}, CF wton: {CF_wton}, peak_load: {peak_load}")
    print(f"Generating samples in ranges {ranges}")
    # samples is numpy array
    samples = lhs(N_DIMS, samples=N_SAMPLES, criterion=CRITERION)

    # scale sample on [0,1] interval to actual ranges
    for i, interval in enumerate(ranges):
        min = interval[0]
        max = interval[1]
        samples[:,i] *= max - min
        samples[:,i] += min
    
    if WRITE_POINTS_TO_CSV:
        df = pd.DataFrame(samples, columns=ranges_name)

        try:
            out_name = sys.argv[1]
        except IndexError:
            out_name = CSV_OUT_NAME

        print(f"Output samples to file: {out_name}")

        df.to_csv(out_name, index_label="Index")
    
    build_simulations(samples)
    print(f"Simulations successfully written in {SIMULATIONS_SUBFOLDER}")


def build_simulations(samples):
    nb = len(samples)
    for i, sample in enumerate(samples):
        print(f"Simulation {i} / {nb}, {sample}")
        capacity_ratio, share_flex, share_sto, share_wind, share_pv, rNTC = sample
        
        name = f"sim-{i}_" + np.array2string(sample, separator="-", formatter={'float_kind': lambda x: f"{x:.2f}" })[1:-1]
        cur_folder = SIMULATIONS_SUBFOLDER + os.sep + name
        
        # in the first iteration, we load the input data from the original simulation directory:
        data = ds.adjust_capacity(REFERENCE_SIMULATION_FOLDER, ('BATS','OTH'), singleunit=True, 
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

        # Needed because the directory name is rounded
        coordinates = pd.Series(sample, index=["CapacityRatio", "ShareFlex", "ShareStorage", "ShareWind", "SharePV", "rNTC"])
        coordinates.name = "LHS-sample"
        coordinates.to_csv(cur_folder + os.sep + SAMPLE_CSV_NAME)
        

if __name__ == "__main__":
    main()
