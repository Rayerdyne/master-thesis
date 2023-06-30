import numpy as np

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
    [(70, "relu", 0.5), (70, "relu", 0.5)],
    [(100, "relu", 0.4), (100, "relu", 0.4)],
    [(100, "relu", 0.5), (100, "relu", 0.5)],
    [(100, "relu", 0.6), (100, "relu", 0.6)],
    [(250, "relu", 0.4), (125, "relu", 0.4)],
    [(250, "tanh", 0.4), (125, "tanh", 0.4)],
    [(200, "relu", 0.4), (150, "relu", 0.4), (100, "relu", 0.4)],
    [(120, "relu", 0.4), (120, "relu", 0.4), (120, "relu", 0.4), (120, "relu", 0.4), (80, "relu", 0.4)],
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

def main():
    print("==== Loading data ====")
    x_train, y_train, x_test, y_test, x_val, y_val, normalizers = fetch_data(DATASET_PATH, TRAIN_SET_RATIO, TEST_SET_RATIO, VALIDATION_SET_RATIO)
    x_train2 = np.concatenate([x_train, x_val])
    y_train2 = np.concatenate([y_train, y_val])


    losses = []
    for i, layers_list in enumerate(architectures):
        print(f"------- Arch {layers_list} -------")
        model = build_model_with_shape(layers_list, "adam", 1e-3)

        reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.1, patience=EARLY_STOPPING_PATIENCE, min_lr=1e-9, verbose=1)
        history = model.fit(x=x_train2, y=y_train2,
                            validation_data=(x_test, y_test),
                            batch_size=BATCH_SIZE, epochs=N_EPOCHS,
                            callbacks=[reduce_lr], verbose=1)
        
        epoch_losses = history.history["val_loss"]
        best_epoch = epoch_losses.index(min(epoch_losses))
        print(f"Best epoch: {best_epoch} / {N_EPOCHS}, with {epoch_losses[best_epoch]}")

        y_pred = model(x_test)
        loss = mean_squared_error(y_test, y_pred)
        losses.append(loss)
        print("sklean measured mse: ", loss)

        plot_loss(history, f"logs/loss-baseline-{i}")
    
    with open("logs/baselines-results.txt", "a") as f:
        for loss, arch in zip(losses, architectures):
            s = f"Arch {arch} ->   {loss}"
            print(s)
            f.write(s + "\n")

if __name__ == "__main__":
    main()