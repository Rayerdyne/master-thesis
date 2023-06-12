"""
Holds the `build_model` function that builds the model, hence contains its description.

@author: François Straet
"""

import numpy as np

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam, RMSprop
from keras_tuner import HyperParameter

from config import N_INPUT_FEATURES, N_OUTPUTS

def build_model(hp: HyperParameter):
    # Input layer
    input = layers.Input(shape=(N_INPUT_FEATURES,), name=f"dispaset_{N_INPUT_FEATURES}_ins")

    # x = layers.Concatenate()([input, tf.math.exp(input), tf.math.log(input+0.00001)])
    x = layers.Concatenate()([input, tf.math.exp(input), tf.math.log(tf.math.abs(input) + 0.0001)])

    # Tune the number of hidden layers.
    for i in range(hp.Int("num_layers", 6, 10)):
        activation = hp.Choice("activation" + str(i+1), ["relu", "leakyrelu", "tanh"])
        if activation == "leakyrelu":
            activation = tf.keras.layers.LeakyReLU(alpha=0.01)
        x = layers.Dense(units=hp.Int('units_' + str(i + 1), min_value=32, max_value=128, step=32),
                               activation=activation)(x)
                            #    activation="relu"))

        x = layers.Dropout(hp.Float('Dropout_value' + str(i + 1), min_value=0.25, max_value=0.75, step=0.1))(x)

    output = layers.Dense(N_OUTPUTS, name="dispaset_approx", activation=None)(x)

    # hp_lr = hp.Float("lr", min_value=1e-4, max_value=1e-2, sampling="log")
    hp_lr = 1e-3
    # hp_optimizer = hp.Choice('optimizer', values=['rmsprop', 'adam'])
    hp_optimizer = "adam"

    if hp_optimizer == 'rmsprop':
        optimizer = RMSprop(learning_rate=hp_lr)
    elif hp_optimizer == 'adam':
        optimizer = Adam(learning_rate=hp_lr)
    else:
        raise ValueError("unexpected optimizer name")

    model = tf.keras.Model(inputs=input, outputs=output)
    model.compile(
        optimizer=optimizer,
        loss="mse",  # Carla used 'mae'
        metrics=["mae", "mse"], )
    
    return model

def build_model2(hp: HyperParameter):
    model = tf.keras.Sequential()

    # Input layer
    model.add(layers.Input(shape=(N_INPUT_FEATURES,), name=f"dispaset_{N_INPUT_FEATURES}_ins"))

    # Tune the number of hidden layers.
    for i in range(hp.Int("num_layers", 2, 2)):
        model.add(layers.Dense(units=hp.Int('units_' + str(i + 1), min_value=16, max_value=256, step=16),
                               activation=hp.Choice("activation" + str(i + 1), ["relu", "tanh"])))
                            #    activation="relu"))

        model.add(layers.Dropout(hp.Float('Dropout_value' + str(i + 1), min_value=0.25, max_value=0.75, step=0.1)))

    model.add(layers.Dense(N_OUTPUTS, name="dispaset_approx", activation=None))

    # hp_lr = hp.Float("lr", min_value=1e-4, max_value=1e-2, sampling="log")
    hp_lr = 1e-3
    # hp_optimizer = hp.Choice('optimizer', values=['rmsprop', 'adam'])
    hp_optimizer = "adam"

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