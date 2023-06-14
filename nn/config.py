"""
Configuration file containing high-level specification of the choice to be made for the
surrogate model. Note that the model architecture still lies in `model.py`.

@author: François Straet
"""

import os

TUNER = "bayesian"
TUNER_MAX_TRIALS = 64
TUNER_EXEC_PER_TRIAL = 5

MODEL_NAME = "go-model-go"
MODEL_OUTPUT_PATH = "models" + os.sep + MODEL_NAME
LOGS_OUTPUT_PATH = "logs" + os.sep + f"{MODEL_NAME}_{TUNER}"
LOGS_MODEL_CKPT = "model-cp.ckpt"

DATASET_PATH = "data" + os.sep + "dataset-carla.csv"
TRAIN_SET_RATIO = 0.7 
VALIDATION_SET_RATIO = 0.1 
TEST_SET_RATIO = 0.2 

N_EPOCHS = 200
N_TUNER_EPOCHS = 75
BATCH_SIZE = 32
EARLY_STOPPING_PATIENCE = 5


# NB: the order here determines the order in the model !
FEATURES_NAMES = ["CapacityRatio", "ShareFlex", "ShareStorage", "ShareWind", "SharePV", "rNTC"]
N_INPUT_FEATURES = len(FEATURES_NAMES)
OUTPUT_NAMES = ["Curtailment_[TWh]", "MaxLoadShedding_[MW]"]
# OUTPUT_NAMES = ["Curtailment_[TWh]"]
N_OUTPUTS = len(OUTPUT_NAMES)

SHOW_PLOTS = False