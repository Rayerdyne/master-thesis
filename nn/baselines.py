import sys

import numpy as np

import tensorflow as tf
from tensorflow.keras.callbacks import ReduceLROnPlateau
from sklearn.metrics import mean_squared_error

from config import *
from model import build_model_with_shape
from train import fetch_data
from view import plot_loss

"""
Trains some neural networks with predefined architectures, to ease comparisons and provide
easier baselines to work with.
"""

architectures = [
    # [(200, "relu", 0.0), (200, "relu", 0.0), (100, "relu", 0.0)],
    # [(200, "relu", 0.3), (200, "relu", 0.3), (100, "relu", 0.3)],
    # [(300, "relu", 0.0), (300, "relu", 0.0), (200, "relu", 0.0)],
    # [(300, "relu", 0.3), (300, "relu", 0.3), (200, "relu", 0.3)],
    # [(400, "relu", 0.0), (400, "relu", 0.0), (200, "tanh", 0.0)],
    # [(400, "relu", 0.2), (400, "relu", 0.2), (200, "tanh", 0.2)],
    # [(70, "relu", 0.5), (70, "relu", 0.5)],
    # [(100, "relu", 0.4), (100, "relu", 0.4)],
    # [(100, "relu", 0.5), (100, "relu", 0.5)],
    # [(100, "relu", 0.6), (100, "relu", 0.6)],
    # [(100, "relu", 0.7), (100, "relu", 0.7)],
    # [(80, "relu", 0.7), (80, "relu", 0.7)],
    # [(150, "relu", 0.6), (100, "relu", 0.6)],
    # [(250, "relu", 0.4), (125, "relu", 0.4)],
    # [(200, "relu", 0.5), (125, "relu", 0.5)],
    # [(200, "relu", 0.5), (125, "tanh", 0.5)],
    # [(200, "relu", 0.4), (125, "tanh", 0.4)],
    # [(200, "relu", 0.4), (100, "tanh", 0.4)],
    # [(180, "relu", 0.4), (100, "tanh", 0.4)],
            [(180, "relu", 0.4), (100, "tanh", 0.4)],
    # [(180, "relu", 0.4), (100, "tanh", 0.4)],
    # [(150, "relu", 0.45), (100, "tanh", 0.45)],
    # [(150, "relu", 0.5), (100, "tanh", 0.5)],
    # [(150, "relu", 0.4), (80, "tanh", 0.4)],
    # [(220, "relu", 0.5), (125, "relu", 0.5)],
    # [(250, "relu", 0.5), (125, "relu", 0.5)],
    # [(250, "tanh", 0.4), (125, "tanh", 0.4)],
    # [(200, "relu", 0.5), (150, "relu", 0.5), (100, "relu", 0.4)],
    # [(120, "relu", 0.4), (120, "relu", 0.4), (120, "relu", 0.4), (120, "relu", 0.4), (80, "relu", 0.4)],
    # [(50, "relu", 0.3), (50, "relu", 0.3), (50, "relu", 0.3), (50, "relu", 0.3)],
    # [(50, "relu", 0.4), (50, "relu", 0.4), (50, "relu", 0.4), (50, "relu", 0.4)],
    # [(50, "relu", 0.2), (50, "relu", 0.2), (50, "relu", 0.2)],
    # [(50, "relu", 0.2), (50, "relu", 0.2), (50, "relu", 0.2), (50, "relu", 0.2)],
    # [(50, "relu", 0.3), (50, "relu", 0.3), (50, "relu", 0.3)],
    # [(50, "relu", 0.4), (50, "relu", 0.4), (50, "relu", 0.4)],
    # [(150, "relu", 0.5), (150, "relu", 0.5), (150, "relu", 0.5)],
    # [(150, "relu", 0.5), (100, "relu", 0.5), (100, "relu", 0.5)],
    # [(150, "relu", 0.5), (150, "relu", 0.5), (100, "relu", 0.5)],
    # [(200, "relu", 0.5), (200, "relu", 0.5), (150, "relu", 0.5)],
    # [(190, "relu", 0.5), (190, "relu", 0.5), (140, "relu", 0.5)],
    # [(200, "relu", 0.5), (200, "relu", 0.5), (150, "relu", 0.5), (30, "relu", 0.3)],
    # [(200, "relu", 0.5), (200, "relu", 0.5), (150, "relu", 0.5), (50, "relu", 0.3)],
    # [(200, "relu", 0.5), (200, "relu", 0.5), (200, "relu", 0.5)],
    # [(150, "relu", 0.5), (150, "relu", 0.5), (150, "relu", 0.5), (150, "relu", 0.5)],
]

def eval_arch(layers_list, x_train, y_train, x_test, y_test, normalizers, save_path=None):
    print(f"------- Arch {layers_list} -------")
    model = build_model_with_shape(layers_list, "adam", 1e-3)

    reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.1, patience=EARLY_STOPPING_PATIENCE, min_lr=1e-9, verbose=1)
    history = model.fit(x=x_train, y=y_train,
                        validation_data=(x_test, y_test),
                        batch_size=BATCH_SIZE, epochs=200,
                        # batch_size=BATCH_SIZE, epochs=N_EPOCHS,
                        callbacks=[reduce_lr], verbose=1)
    
    epoch_losses = history.history["val_loss"]
    best_epoch = epoch_losses.index(min(epoch_losses))
    print(f"Best epoch: {best_epoch} / {N_EPOCHS}, with {epoch_losses[best_epoch]}")

    y_pred = model(x_test)
    loss = mean_squared_error(y_test, y_pred)
    plot_loss(history, f"logs/loss-baseline-{layers_list}.png")

    if save_path is not None:
        norm_model = tf.keras.Sequential()
        norm_model.add(normalizers[0])
        norm_model.add(model)
        norm_model.add(normalizers[1])
        norm_model.compile(optimizer="adam", loss="MSE", metrics=["mae", "mse"])
        norm_model.save(save_path, save_format="tf")
    return loss


def main():
    print("==== Loading data ====")
    x_train, y_train, x_test, y_test, x_val, y_val, normalizers = fetch_data(DATASET_PATH, TRAIN_SET_RATIO, TEST_SET_RATIO, VALIDATION_SET_RATIO)
    x_train2 = np.concatenate([x_train, x_val])
    y_train2 = np.concatenate([y_train, y_val])


    save_path = "models/baseline-model"
    if len(sys.argv) >= 3 and sys.argv[1] == "--save-one":
        idx = int(sys.argv[2])
        if idx >= len(architectures):
            print(f"Index {idx} exceeds number of available architectures ({len(architectures)})")
            return
        layers_list = architectures[idx]
        loss = eval_arch(layers_list, x_train2, y_train2, x_test, y_test, normalizers, save_path)
        print("Loss: ", loss)
        return

    losses = []
    for layers_list in architectures:
        loss = eval_arch(layers_list, x_train2, y_train2, x_test, y_test, normalizers)
        losses.append(loss)
        print("sklean measured mse: ", loss)

    
    with open("logs/baselines-results.txt", "a") as f:
        for loss, arch in zip(losses, architectures):
            s = f"Arch {arch} ->   {loss}"
            print(s)
            f.write(s + "\n")

if __name__ == "__main__":
    main()