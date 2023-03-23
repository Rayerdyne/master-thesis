# Wether or not we build test simulations
TESTING = True

# Latin Hypercube parameters
CRITERION = "maximin"
N_SAMPLES = 10

WRITE_POINTS_TO_CSV = False
CSV_OUT_NAME = "samples.csv"

# Base directory for the simulation
SIMULATIONS_FOLDER = "simulations"
# Where simulation will actually be written
SIMULATIONS_SUBFOLDER = SIMULATIONS_FOLDER + os.sep + "test-Matijs"
# Where to write reference simulation
REFERENCE_SIMULATION_FOLDER = SIMULATIONS_SUBFOLDER + os.sep + "reference"
# Where to write the sample point in the simulation directory
SAMPLE_CSV_NAME = "sample.csv"