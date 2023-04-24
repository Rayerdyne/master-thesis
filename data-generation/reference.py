# -*- coding: utf-8 -*-
"""
Makes the reference simulation

@author F. Straet
"""

import json, os, sys

sys.path.append(os.path.abspath(".." + os.sep + ".."  + os.sep + "Dispa-SET"))

import dispaset as ds
import pandas as pd


from config import REFERENCE_INFO_FILE, REFERENCE_SIMULATION_DIR, START_DATE, STOP_DATE

class ReferenceInfo(object):
    def __init__(self, data):
        self.__dict__ = data

    @classmethod 
    def from_values(cls, peak_load, flex_units, slow_units, CF_wton, CF_pv, ref_values):
        return cls({
            "peak_load": peak_load,
            "flex_units": flex_units,
            "slow_units": slow_units,
            "CF_wton": CF_wton,
            "CF_pv": CF_pv,
            "ref_values": ref_values
        })

    @classmethod
    def deserialize(cls, path):
        with open(path, "r") as f:
            d = json.load(f)
            d["flex_units"] = pd.Index(d["flex_units"])
            d["slow_units"] = pd.Index(d["slow_units"])
            return cls(d)
    
    def serialize(self, path):
        with open(path, "w") as f:
            json.dump({
                "peak_load": self.peak_load,
                "flex_units": self.flex_units.tolist(),
                "slow_units": self.slow_units.tolist(),
                "CF_wton": self.CF_wton,
                "CF_pv": self.CF_pv,
                "ref_values": self.ref_values
            }, f, indent=4)
    
    def tolist(self):
        return [self.peak_load, self.flex_units, self.slow_units, self.CF_wton, self.CF_pv]

def build_reference(refinfo_path):
    """
    Builds the reference simulation (configuration from config.py) and writes
    the info in `refinfo_path`
    """
    config = ds.load_config_excel("ConfigFiles" + os.sep + "ConfigTest_Francois.xlsx")
    config["SimulationDirectory"] = REFERENCE_SIMULATION_DIR 

    config["StartDate"] = START_DATE
    config["StopDate"] = STOP_DATE


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

    refinfo = ReferenceInfo.from_values(peak_load, flex_units, slow_units, CF_wton, CF_pv, ref)
    refinfo.serialize(refinfo_path)

if __name__ == "__main__":
    print("Building reference simulation")
    build_reference(REFERENCE_INFO_FILE)
