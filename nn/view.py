"""
Contains the different tools used for visualizing the results of the training and the
model.

The main function plots a 3d mesh of a chosen output as a function of 2 chosen inputs.
The value of the other parameter can be set with sliders.

Usage:
    python view.py --surface <in1> <in2> <out>
    Where arguments are indexes (refer to the features and outputs lists in `config.py`)
"""

import os, sys

import matplotlib.pyplot as plt
import numpy as np

from matplotlib import cm
from matplotlib.widgets import Slider, Button
from sklearn.metrics import mean_absolute_error, mean_squared_error

from tensorflow.keras.models import load_model

from config import BATCH_SIZE, LOGS_MODEL_CKPT, LOGS_OUTPUT_PATH, OUTPUT_NAMES, N_INPUT_FEATURES, SHOW_PLOTS

# See ../data-generation/sampling.py
capacity_ratio_range = (0.5, 1.8)
share_flex_range     = (0.01, 0.99)
share_storate_range  = (0, 0.5)
share_wind_range     = (0, 0.5)
share_pv_range       = (0, 0.5)
rntc_range           = (0, 0.7)    

ranges = [capacity_ratio_range, share_flex_range,
          share_storate_range,  share_wind_range,
          share_pv_range,       rntc_range]

ranges_name = ["Capacity ratio", "Share flexible",
               "Share storage",  "Share wind",
               "Share PV",       "rNTC"]


def plot_loss(H, path):
    # plot the training history loss
    plt.style.use("ggplot")
    fig, ax = plt.subplots()
    ax.set_ylim([0, 0.2])
    ax.plot(H.history['loss'], label='Training Loss')
    ax.plot(H.history['val_loss'], label='Validation Loss')
    ax.set_title("Training Loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel('Loss function')
    ax.legend()
    fig.savefig(path)
    if SHOW_PLOTS:
        plt.show()
    return

def plot_graph(y_test, y_pred, name, path, output_idx=0):
    if output_idx >= y_test.shape[1]:
        raise IndexError(f"Index {output_idx} out of range (0 to {y_test.shape[0]-1})")

    fig, ax = plt.subplots()
    ax.scatter(range(len(y_test[:,output_idx])), y_test[:,output_idx], color='blue', label="Truth")
    ax.scatter(range(len(y_pred[:,output_idx])), y_pred[:,output_idx], color='red', label="Prediction")
    ax.legend()
    ax.title(name)
    ax.xlabel("Observation")
    ax.ylabel("Value")
    fig.savefig(path)
    if SHOW_PLOTS:
        plt.show()
    return

def plot_surface(X, Y, Z, xlabel, ylabel, zlabel):
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    surface = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    ax.set_zlim(-1.01, 1.01)
    # ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter("{x:.02f}")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    fig.colorbar(surface, shrink=0.5, aspect=5)

    if SHOW_PLOTS:
        plt.show()
    plt.show()

def displays(model_path, x_test, y_test, history=None):
    model = load_model(model_path)

    y_test_pred = model.predict(x_test, batch_size=BATCH_SIZE)
    print("Prediction against truth:")
    print(y_test_pred[:5])
    print(y_test[:5])

    # Metrics...
    print(type(model))
    loss, mae, mse = model.evaluate(x_test, y_test, batch_size=BATCH_SIZE)
    max_difference = np.max(np.abs(y_test - y_test_pred))
    print(f"---- Metrics for {model_path} ----")
    print(f"Loss {loss:.5f}")
    print(f"MAE {mae:.5f}")
    print(f"MSE {mse:.5f}")
    print(f"Maxdif {max_difference:.5f}")

    plot_graph(y_test, y_test_pred, "Test", LOGS_OUTPUT_PATH + os.sep + "test.png")
    if history:
        plot_loss(history, LOGS_OUTPUT_PATH + os.sep + "losses-history.png")

def compute_surface(model, X, Y, i_sliders, in1, in2, out):
    oldshape = X.shape

    input = np.zeros([X.size, N_INPUT_FEATURES])
    input[:,in1] = X.reshape(-1)
    input[:,in2] = Y.reshape(-1)
    
    for i, slider in i_sliders:
        input[:,i] = slider.val * np.ones(X.size)
    
    output = model(input).numpy()

    return output[:,out].reshape(oldshape)

N_POINTS = 200
def view_surface(model, args):
    if len(args) < 3:
        raise TypeError(f"Not enough argument given to the script (has {len(sys.argv)-1}, needs 4)")
    
    in1 = int(args[0])
    in2 = int(args[1])
    out = int(args[2])

    range1 = ranges[in1]
    range2 = ranges[in2]
    x = np.linspace(range1[0], range1[1], N_POINTS)
    y = np.linspace(range2[0], range2[1], N_POINTS)
    X, Y = np.meshgrid(x, y)
    
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    # initialize shit
    surface = ax.plot_surface(X, Y, np.zeros(X.shape))

    fig.subplots_adjust(bottom=0.4, top=1)
    ax.set_xlabel(ranges_name[in1])
    ax.set_ylabel(ranges_name[in2])
    ax.set_zlabel(OUTPUT_NAMES[out])
    ax.set_title(OUTPUT_NAMES[out] + " vs " + ranges_name[in1] + " (x) and " + ranges_name[in2] + " (y)")

    i_sliders = []
    counter = 0
    for i, (interval, name) in enumerate(zip(ranges, ranges_name)):
        if i not in [in1, in2]:
            axes = fig.add_axes([0.25, 0.25 - counter * 0.05,  0.65, 0.03])
            i_sliders.append((i, Slider(
                ax=axes,
                label=name,
                valmin=interval[0],
                valmax=interval[1],
                valinit=np.mean([interval[0], interval[1]])
            )))
            counter += 1

    def update(_event):
        ax.cla()
        ax.set_xlabel(ranges_name[in1])
        ax.set_ylabel(ranges_name[in2])
        ax.set_zlabel(OUTPUT_NAMES[out])
        ax.set_title(OUTPUT_NAMES[out] + " vs " + ranges_name[in1] + " (x) and " + ranges_name[in2] + " (y)")
        surface = ax.plot_surface(X, Y, compute_surface(model, X, Y, i_sliders, in1, in2, out),
                                  cmap=cm.coolwarm, linewidth=0, antialiased=False)
        
        if len(fig.axes) >= 7:
            fig.delaxes(fig.axes[-1])
        cax = fig.add_axes([0.7, 0.45, 0.04, 0.5])
        fig.colorbar(surface, cax=cax, shrink=0.5)
        fig.canvas.draw_idle()
    
    b_axes = fig.add_axes([0.8, 0.03, 0.1, 0.02])
    button = Button(b_axes, "Update", hovercolor="0.975")
    button.on_clicked(update)

    update(None)
    plt.show()


CMD_DICT = {
    "--surface": view_surface
}

def main():
    if len(sys.argv) < 3:
        print("Need model path as first argument, and command")
        return

    path = sys.argv[1]
    # model = load_model(LOGS_OUTPUT_PATH + os.sep + LOGS_MODEL_CKPT)
    model = load_model(path)
    model.compile(optimizer="adam", loss="MSE")

    command = sys.argv[2]
    if command not in CMD_DICT:
        raise ValueError(f"Command {command} not found")
    
    action = CMD_DICT[command]
    action(model, sys.argv[3:])


if __name__ == "__main__":
    main()

    