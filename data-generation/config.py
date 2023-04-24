import os

# Wether or not we build test simulations
TESTING = True

# Latin Hypercube parameters
CRITERION = "maximin"
N_SAMPLES = 2

START_DATE = (2022, 1, 1, 0, 0, 0)
STOP_DATE = (2022, 12, 31, 0, 0, 0)

WRITE_POINTS_TO_CSV = True
SAMPLES_CSV_NAME = "samples.csv"

# Where simulation will actually be written
SIMULATIONS_DIR = "simulations" + os.sep + "test"
# Where to write reference simulation
REFERENCE_SIMULATION_DIR = SIMULATIONS_DIR + os.sep + "reference"
REFERENCE_INFO_FILE = SIMULATIONS_DIR + os.sep + "reference-info.json"
# Where to write the sample point in the simulation directory
SAMPLE_CSV_NAME = "sample.csv"

# Where to write the final data with simulation outputs:
DATASET_NAME = "dataset.csv"