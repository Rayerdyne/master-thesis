import os, sys
import numpy as np
import pandas as pd

from config import REFERENCE_SIMULATION_DIR

sys.path.append(os.path.abspath(".." + os.sep + ".."  + os.sep + "Dispa-SET"))

import dispaset as ds

rng = pd.date_range('2019-7-01', '2019-7-07', freq='H')

inputs, results = ds.get_sim_results(REFERENCE_SIMULATION_DIR)

ds.plot_zone(inputs, results, z="BE", path="plots/BE.png")
ds.plot_zone(inputs, results, z="DE", path="plots/DE.png")
ds.plot_zone(inputs, results, z="FR", path="plots/FR.png")

ds.plot_zone(inputs, results, z="BE", rng=rng, path="plots/dispatch-BE-short.png")
ds.plot_zone(inputs, results, z="DE", rng=rng, path="plots/dispatch-DE-short.png")

ds.plot_energy_zone_fuel(inputs, results, ds.get_indicators_powerplant(inputs, results), path="plots/energy_zone_fuel")

cap = ds.plot_zone_capacities(inputs, results, path="plots/zone-capacities.png")

# ds.plot_line_congestion_map(inputs, results, path="plots/line-congestion-map.png")
# ds.plot_line_congestion_map(inputs, results, terrain=True, margin=3, figsize=(9, 7), edge_width=3.5, bublesize=100, path="plots/line-congestion-map-carla.png")

pft, pft_prct = ds.plot_power_flow_tracing_matrix(inputs, results, cmap="magma_r", figsize=(15, 10), path="plot/flow-tracing-matrix.png")