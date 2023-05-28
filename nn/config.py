import os

TUNER = "bayesian"
TUNER_MAX_TRIALS = 16
TUNER_EXEC_PER_TRIAL = 3

MODEL_NAME = "testmodel"
MODEL_OUTPUT_PATH = "models" + os.sep + MODEL_NAME
LOGS_OUTPUT_PATH = "logs" + os.sep + f"{MODEL_NAME}_{TUNER}"
LOGS_MODEL_CKPT = "model-cp.ckpt"

DATASET_PATH = "data" + os.sep + "dataset-MILP.csv"
TRAIN_SET_RATIO = 0.7 
VALIDATION_SET_RATIO = 0.1 
TEST_SET_RATIO = 0.2 

N_EPOCHS = 20
N_TUNER_EPOCHS = 5
BATCH_SIZE = 32
EARLY_STOPPING_PATIENCE = 5


# NB: the order here determines the order in the model !
FEATURES_NAMES = ["CapacityRatio", "ShareFlex", "ShareStorage", "ShareWind", "SharePV", "rNTC"]
N_INPUT_FEATURES = len(FEATURES_NAMES)
OUTPUT_NAMES = ["Curtailment_[TWh]", "MaxLoadShedding_[MW]"]
N_OUTPUTS = len(OUTPUT_NAMES)
