"""
Holds the `build_model` function that builds the model, hence contains its description.

@author: François Straet
"""

import numpy as np

from tensorflow import keras
from keras import layers
from keras_tuner import HyperParameter
from keras.optimizers import Adam, RMSprop

from config import N_INPUT_FEATURES, N_OUTPUTS

def build_model(hp: HyperParameter):
    model = keras.Sequential()

    # Input layer
    model.add(layers.Input(shape=(N_INPUT_FEATURES,), name=f"dispaset_{N_INPUT_FEATURES}-ins"))

    # Tune the number of hidden layers.
    for i in range(hp.Int("num_layers", 2, 5)):
        model.add(layers.Dense(units=hp.Int('units_' + str(i + 1), min_value=32, max_value=512, step=32),
                               activation=hp.Choice("activation" + str(i + 1), ["relu", "tanh"])))

        model.add(layers.Dropout(hp.Float('Dropout_value' + str(i + 1), min_value=0.25, max_value=0.75, step=0.1)))

    model.add(layers.Dense(N_OUTPUTS, name="dispaset_approx"))

    hp_lr = hp.Float("lr", min_value=1e-4, max_value=1e-2, sampling="log")
    hp_optimizer = hp.Choice('optimizer', values=['rmsprop', 'adam'])

    if hp_optimizer == 'rmsprop':
        optimizer = RMSprop(learning_rate=hp_lr)
    elif hp_optimizer == 'adam':
        optimizer = Adam(learning_rate=hp_lr)
    else:
        raise ValueError("unexpected optimizer name")

    model.compile(
        optimizer=optimizer,
        loss="mse",  # Carla used 'mae'
        metrics=["mae", "mse"], )

    return model