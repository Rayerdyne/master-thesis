import os

import pandas as pd
import numpy as np

import keras_tuner as kt
import tensorflow as tf
from keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.utils import plot_model
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Normalization

from config import *
from model import build_model
from view import displays

# Make experiments reproducible
os.environ["PYTHONHASHSEED"] = "0"
tf.random.set_seed(0)
SK_RANDOM_STATE = 1
TUNER_SEED = 1

def scale_data(train, test, val, get_denormalizer=False):
    """
    Adapts a tensorflow normalizer to the train set, and applies it to the
    train, test and validation sets, and returns an inverse normalizer if 
    `get_denormalizer` is set to true (else none)
    """
    #                         last axis
    normalizer = Normalization(axis=-1)
    normalizer.adapt(train)
    if get_denormalizer:
        denormalizer = Normalization(axis=-1, invert=True)
        denormalizer.adapt(train)
        return normalizer(train), normalizer(test), normalizer(val), denormalizer
    else:
        return normalizer(train), normalizer(test), normalizer(val)


def fetch_data(dataset_path, train_ratio, test_ratio, validation_ratio, val_dataset_path=None):
    """
    Fetches the data in `dataset_path`, splits it in train/test/validation sets
    and scales the sets w.r.t. the test set.

    Also returns the normalizer object that served for normalizing (in order to
    add the inverse transformation at the end of the network)

    NB: Splits depend on the `SK_RANDOM_STATE` seed
    """
    data = pd.read_csv(dataset_path)
    data_x = data.loc[:,FEATURES_NAMES]
    data_y = data.loc[:,OUTPUT_NAMES]

    # all_x.describe()
    # all_y.describe()

    if val_dataset_path is None:
        r = test_ratio / (test_ratio + validation_ratio)
        # x_train2, x_test, y_train2, y_test = train_test_split(data_x, data_y, test_size=test_ratio, random_state=SK_RANDOM_STATE)
        x_val2, x_train, y_val2, y_train = train_test_split(data_x, data_y, test_size=train_ratio, random_state=SK_RANDOM_STATE)
    else:
        val_data = pd.read_csv(val_dataset_path)
        x_val2 = val_data.loc[:,FEATURES_NAMES]
        y_val2 = val_data.loc[:,OUTPUT_NAMES]
        x_train = data_x.to_numpy()
        y_train = data_y.to_numpy()

    x_val, x_test, y_val, y_test   = train_test_split(x_val2, y_val2, test_size=r, random_state=SK_RANDOM_STATE)


    x_train, x_test, x_val = scale_data(x_train, x_test, x_val)
    y_train, y_test, y_val, denormalizer = scale_data(y_train, y_test, y_val, get_denormalizer=True)
    
    return x_train, y_train, x_test, y_test, x_val, y_val, denormalizer

def get_tuner(tuner, callbacks):
    """
    Builds a tuner given its name, the normalizer to be inversed as the last step,
    with default configuration from config.py
    """
    args = {
        "objective": "val_loss",
        "overwrite": True,
        "seed": TUNER_SEED,
        "directory": LOGS_OUTPUT_PATH,
        "project_name": f"tuner_{tuner}" 
    }
    if tuner == "bayesian":
        factory = kt.BayesianOptimization
        args["max_trials"] = TUNER_MAX_TRIALS
        args["executions_per_trial"] = TUNER_EXEC_PER_TRIAL
    elif tuner == "random":
        factory = kt.RandomSearch
        args["max_trials"] = TUNER_MAX_TRIALS
        args["executions_per_trial"] = TUNER_EXEC_PER_TRIAL
    elif tuner == "hyperband":
        factory = kt.Hyperband
        args["max_epochs"] = N_TUNER_EPOCHS + 15
        callbacks.append(EarlyStopping(monitor="val_loss", patience=EARLY_STOPPING_PATIENCE))
    else:
        raise ValueError(f"Unknown tuner name {tuner}")
    
    return factory(build_model, **args), callbacks



def main():
    print("==== Loading data ====")
    x_train, y_train, x_test, y_test, x_val, y_val, normalizers = fetch_data(DATASET_PATH, TRAIN_SET_RATIO, TEST_SET_RATIO, VALIDATION_SET_RATIO)

    tensorboard = TensorBoard(LOGS_OUTPUT_PATH, histogram_freq=1)
    reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.1, patience=EARLY_STOPPING_PATIENCE, min_lr=1e-6, verbose=1)
    callbacks = [tensorboard]

    print("==== Tuning ====")
    tuner: kt.Tuner
    tuner, callbacks = get_tuner(TUNER, callbacks)
    tuner.search(x=x_train, y=y_train, 
                 validation_data=(x_val, y_val),
                 batch_size=BATCH_SIZE,
                 callbacks=callbacks,
                 epochs=N_TUNER_EPOCHS)
    
    best_model = tuner.get_best_models(num_models=1)[0]

    print("==== Best model summary ====")
    print(best_model.summary())
    print(tuner.results_summary(num_trials=1))
    plot_model(best_model, to_file=LOGS_OUTPUT_PATH + os.sep + "ANN_regression.png", show_shapes=True, 
               show_layer_names=True, rankdir='LR', expand_nested=False, dpi=96)
    
    best_hp = tuner.get_best_hyperparameters(num_trials=1)[0]
    print(best_hp.values)

    print("==== Training ====")
    model_path = LOGS_OUTPUT_PATH + os.sep + LOGS_MODEL_CKPT
    checkpoint = ModelCheckpoint(filepath=model_path,
                                 monitor="val_loss", verbose=1,
                                 save_best_only=True, mode="min")
    
    model = tuner.hypermodel.build(best_hp)
    x_train2 = np.concatenate([x_train, x_val])
    y_train2 = np.concatenate([y_train, y_val])

    history = model.fit(x=x_train2, y=y_train2,
                        validation_data=(x_test, y_test),
                        batch_size=BATCH_SIZE, epochs=N_EPOCHS,
                        callbacks=[checkpoint], verbose=1)
    
    epoch_losses = history.history["val_loss"]
    best_epoch = epoch_losses.index(min(epoch_losses))
    print(f"Best epoch: {best_epoch} / {N_EPOCHS}")

    print("==== Some displays ====")
    displays(model_path, x_train, y_train, x_test, y_test, history)

    norm_model = tf.keras.Sequential()
    norm_model.add(normalizers[0])
    norm_model.add(model)
    norm_model.add(normalizers[1])
    norm_model.save(MODEL_OUTPUT_PATH, save_format="tf")


if __name__ == "__main__":
    main()