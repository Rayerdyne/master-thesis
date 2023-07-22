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
    """
    Function building the model for hyper-parameter tuning

    :hp:    the set of hyper-parameters
    """

    layers = []
    for i in range(hp.Int("num_layers", 2, 6)):
        nb = hp.Int('units_' + str(i + 1), min_value=32, max_value=256, step=32)
        activation = hp.Choice("activation" + str(i+1), ["relu", "leakyrelu", "tanh"])
        if activation == "leakyrelu":
            activation = tf.keras.layers.LeakyReLU(alpha=0.01)
        
        dropout = hp.Float('Dropout_value' + str(i + 1), min_value=0.25, max_value=0.75, step=0.05)
        layers.append((nb, activation, dropout))
    
    # optim = hp.Choice('optimizer', values=['rmsprop', 'adam'])
    optim = "adam"

    # lr = hp.Float("lr", min_value=1e-4, max_value=1e-2, sampling="log")
    lr = 1e-3

    return build_model_with_shape(layers, optim, lr)


def build_model_with_shape(layers_list, optim, lr):
    """
    Builds a model with a given shape (a list of (n_neurons, activation, dropout) tuples) and
    optimizer and learning rate.

    :layers:    a list of `(n, a, d)` tuples where `n` is the number of neurons in the layer, `a`
                is the activation function and `d` the dropout value.
    :optim:     the optimizer to be used
    :lr:        the learning rate
    """
    # Input layer
    model = tf.keras.Sequential()
    model.add(layers.Input(shape=(N_INPUT_FEATURES,), name=f"dispaset_{N_INPUT_FEATURES}_ins"))

    for layer in layers_list:
        nb, activation, dropout = layer
        model.add(layers.Dense(units=nb, activation=activation))
        model.add(layers.Dropout(dropout))
    
    model.add(layers.Dense(N_OUTPUTS, name="dispaset_approx", activation=None))

    if optim == 'rmsprop':
        optimizer = RMSprop(learning_rate=lr)
    elif optim == 'adam':
        optimizer = Adam(learning_rate=lr)
    else:
        raise ValueError("unexpected optimizer name")

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

def build_model3(hp: HyperParameter):
    # Input layer
    input = layers.Input(shape=(N_INPUT_FEATURES,), name=f"dispaset_{N_INPUT_FEATURES}_ins")

    # x = layers.Concatenate()([input, tf.math.exp(input), tf.math.log(input+0.00001)])
    x = layers.Concatenate()([input, tf.math.exp(input), tf.math.log(tf.math.abs(input) + 0.0001)])

    # Tune the number of hidden layers.
    for i in range(hp.Int("num_layers", 2, 10)):
        activation = hp.Choice("activation" + str(i+1), ["relu", "leakyrelu", "tanh"])
        if activation == "leakyrelu":
            activation = tf.keras.layers.LeakyReLU(alpha=0.01)
        x = layers.Dense(units=hp.Int('units_' + str(i + 1), min_value=32, max_value=256, step=32),
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