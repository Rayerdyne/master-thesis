# -*- coding: utf-8 -*-
"""
Defines samples points on the input space for the expensive simulation to be run on.

@author: François Straet
"""

import sys

import pandas as pd

from pyDOE import lhs

CRITERION = "maximin"
N_SAMPLES = 10

OUT_NAME = "samples.csv"

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
    print(f"Generating samples in ranges {ranges}")
    # samples is numpy array
    samples = lhs(N_DIMS, samples=N_SAMPLES, criterion=CRITERION)

    # scale sample on [0,1] interval to actual ranges
    for i, interval in enumerate(ranges):
        min = interval[0]
        max = interval[1]
        samples[:,i] *= max - min
        samples[:,i] += min
    
    df = pd.DataFrame(samples, columns=ranges_name)

    try:
        out_name = sys.argv[1]
    except IndexError:
        out_name = OUT_NAME

    print(f"Output samples to file: {out_name}")

    df.to_csv(out_name, index_label="Index")
        

if __name__ == "__main__":
    main()
