"""
Contains the code for the hyperparameter tuning and the model training.

@author: François Straet
"""

import os, sys

import pandas as pd
import numpy as np

import keras_tuner as kt
import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Normalization
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from config import *
from model import build_model
from view import displays

# Make experiments reproducible
os.environ["PYTHONHASHSEED"] = "0"
tf.random.set_seed(0)
SK_RANDOM_STATE = 2
TUNER_SEED = 1

def trick_distr(mean: np.ndarray, var: np.ndarray):
    """
    Returns a fake dataset with given mean and variance

    :mean:      the desired mean
    :var:       the desired variance
    """
    return np.row_stack([mean - var, mean + var])

def inverse_normalization(norm: Normalization, dim: int) -> Normalization:
    """
    Builds a normalizer that makes the inverse normalization of the given normalizer, 
    without using the invert parameter.

    :norm:      the normalization layer to invert
    :dim:       the number of dimensions
    """
    n0 = norm(np.zeros(dim))
    n1 = norm(np.ones(dim))
    var = 1 / (n1 - n0)
    mu = -n0 * var
    
    denorm = Normalization(axis=-1)
    denorm.adapt(trick_distr(-(mu/var), 1/var))
    return denorm

def scale_data(train, test, val, get_denormalizer=False, minmax=False):
    """
    Adapts a tensorflow normalizer to the train set, and applies it to the
    train, test and validation sets, and returns an inverse normalizer if 
    `get_denormalizer` is set to true (else the normalizer)

    :train:             Training data
    :test:              Testing data
    :val:               Validation data
    :get_denormalizer:  If true, also return the normalization layer with its inverse
    """
    # print("train.shape", train.shape)
    # print("test shape", test.shape)
    # print("val shape", val.shape)
    if minmax:
        min = tf.math.reduce_min(train, axis=0)
        max = tf.math.reduce_max(train, axis=0)
        scale_factor = max - min
        train = (train-min) / scale_factor
        test = (test-min) / scale_factor
        val = (val-min) / scale_factor
        return train, test, val, Normalization(axis=-1).adapt(train)
    else:
        #                         last axis
        normalizer = Normalization(axis=-1)
        normalizer.adapt(train)
        if get_denormalizer:
            return normalizer(train), normalizer(test), normalizer(val), normalizer, inverse_normalization(normalizer, train.shape[1])
        else:
            return normalizer(train), normalizer(test), normalizer(val), normalizer


def fetch_data(dataset_path, train_ratio, test_ratio, validation_ratio, val_dataset_path=None, minmax=False):
    """
    Fetches the data in `dataset_path`, splits it in train/test/validation sets
    and scales the sets w.r.t. the test set.

    Also returns the normalizer object that served for normalizing (in order to
    add the inverse transformation at the end of the network)

    NB: Splits depend on the `SK_RANDOM_STATE` seed

    :dataset_path:          Path to primary dataset
    :train_ratio:           Proportion of the dataset to be used for training
    :test_ratio:            Proportion of the dataset to be used for testing
    :val_ratio:             Proportion of the dataset to be used for validation
    :val_dataset_path:      If present, use dataset at this location for testing and 
                            validation. Split according to rescaled ratios.
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


    print("Before")
    print("xtrain mean", tf.math.reduce_mean(x_train, axis=0))
    print("ytrain mean", tf.math.reduce_mean(y_train, axis=0))
    x_train, x_test, x_val, normalizer_x, denormalizer_x = scale_data(x_train, x_test, x_val, get_denormalizer=True, minmax=minmax)
    y_train, y_test, y_val, normalizer_y, denormalizer_y = scale_data(y_train, y_test, y_val, get_denormalizer=True, minmax=minmax)
    print("After")
    print("xtrain mean", tf.math.reduce_mean(x_train, axis=0))
    print("ytrain mean", tf.math.reduce_mean(y_train, axis=0))

    print("test")
    print(x_train[:5])
    print(denormalizer_x(normalizer_x(x_train[:5])))
    print(y_train[:5])
    print(denormalizer_y(normalizer_y(y_train[:5])))
    
    return x_train, y_train, x_test, y_test, x_val, y_val, (normalizer_x, denormalizer_y)

def get_tuner(tuner, callbacks):
    """
    Builds a tuner given its name, the normalizer to be inversed as the last step,
    with default configuration from config.py

    :tuner:         The name of the tuner to be used, in 
                    ["bayesian", "random", "hyperband"]
    :callbacks:     The list of callbacks for the model training
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

    model_path = LOGS_OUTPUT_PATH + os.sep + LOGS_MODEL_CKPT
    if len(sys.argv) >= 2 and sys.argv[1] == "--test-fetch":
        return
    elif len(sys.argv) < 2 or sys.argv[1] != "--redo-displays":
        print("==== Tuning ====")
        tensorboard = TensorBoard(LOGS_OUTPUT_PATH, histogram_freq=1)
        tuner_callbacks = [tensorboard]
        tuner: kt.Tuner
        tuner, tuner_callbacks = get_tuner(TUNER, tuner_callbacks)
        tuner.search(x=x_train, y=y_train, 
                    validation_data=(x_val, y_val),
                    batch_size=BATCH_SIZE,
                    callbacks=tuner_callbacks,
                    epochs=N_TUNER_EPOCHS)
        
        best_model = tuner.get_best_models(num_models=1)[0]

        best_hp = tuner.get_best_hyperparameters(num_trials=1)[0]

        print("==== Training ====")
        checkpoint = ModelCheckpoint(filepath=model_path,
                                    monitor="val_loss", verbose=1,
                                    save_best_only=True, mode="min")
        
        model = tuner.hypermodel.build(best_hp)
        x_train2 = np.concatenate([x_train, x_val])
        y_train2 = np.concatenate([y_train, y_val])

        reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.1, patience=EARLY_STOPPING_PATIENCE, min_lr=1e-9, verbose=1)
        history = model.fit(x=x_train2, y=y_train2,
                            validation_data=(x_test, y_test),
                            batch_size=BATCH_SIZE, epochs=N_EPOCHS,
                            callbacks=[checkpoint, reduce_lr], verbose=1)
        
        epoch_losses = history.history["val_loss"]
        best_epoch = epoch_losses.index(min(epoch_losses))
        print(f"Best epoch: {best_epoch} / {N_EPOCHS}")

        y_pred = model(x_test)
        loss = mean_squared_error(y_test, y_pred)
        print("sklean measured mse: ", loss)

        print("==== Best model summary ====")
        print(best_model.summary())
        print(tuner.results_summary(num_trials=1))
        # plot_model(best_model, to_file=LOGS_OUTPUT_PATH + os.sep + "ANN_regression.png", show_shapes=True, 
        #         show_layer_names=True, rankdir='LR', expand_nested=False, dpi=96)
        print(best_hp.values)

        norm_model = tf.keras.Sequential()
        norm_model.add(normalizers[0])
        norm_model.add(model)
        norm_model.add(normalizers[1])
        norm_model.compile(optimizer="adam", loss="MSE", metrics=["mae", "mse"])
        norm_model.save(MODEL_OUTPUT_PATH, save_format="tf")
    else:
        history = None
    
    print("==== Some displays ====")
    displays(model_path, x_test, y_test, history)

    
    data = pd.read_csv(DATASET_PATH)
    x_test_u = data.loc[:,FEATURES_NAMES].to_numpy()
    y_test_u = data.loc[:,OUTPUT_NAMES].to_numpy()
    displays(MODEL_OUTPUT_PATH, x_test_u, y_test_u)
    
    # from keras.models import load_model
    # model = load_model(MODEL_OUTPUT_PATH)

    # normalizer = model.layers[0]
    # denormalizer = model.layers[2]

    # print("norm", normalizer(np.array([1.15084746, 0.52775953, 0.25220339, 0.25861229, 0.34929025, 0.35087394])))
    # print("denorm", denormalizer(np.array([1352.55465844, 4573.64407764])))

    # print("==== Scaling In ====")
    # print("Raw: ", x_test_u[:5])
    # print("Scaled: ", normalizer(x_test_u[:5]))

    # print("==== Scaling Out ====")
    # print("Raw: ", y_test_u[:5])
    # print("Scaled: ", denormalizer(np.zeros([5, 2])))

if __name__ == "__main__":
    main()