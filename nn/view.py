import os, sys

import matplotlib.pyplot as plt
import numpy as np

from keras.models import load_model
from matplotlib import cm
from matplotlib.widgets import Slider, Button
from sklearn.metrics import mean_absolute_error, mean_squared_error

from config import BATCH_SIZE, LOGS_MODEL_CKPT, LOGS_OUTPUT_PATH, OUTPUT_NAMES, N_INPUT_FEATURES

# See ../data-generation/sampling.py
capacity_ratio_range = (0.5, 1.8)
share_flex_range     = (0.01, 0.99)
share_storate_range  = (0, 0.5)
share_wind_range     = (0, 0.5)
share_pv_range       = (0.2, 0.5)
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
    plt.figure()
    plt.plot(H.history['loss'], label='Training Loss')
    plt.plot(H.history['val_loss'], label='Validation Loss')
    plt.title("Training Loss")
    plt.xlabel("Epoch")
    plt.ylabel('Loss function')
    plt.legend()
    plt.savefig(path)
    plt.show()
    return

def plot_graph(y_test, y_pred, name, path, output_idx=0):
    if output_idx >= y_test.shape[1]:
        raise IndexError(f"Index {output_idx} out of range (0 to {y_test.shape[0]-1})")

    plt.scatter(range(len(y_test[:,output_idx])), y_test[:,output_idx], color='blue', label="Truth")
    plt.scatter(range(len(y_pred[:,output_idx])), y_pred[:,output_idx], color='red', label="Prediction")
    plt.legend()
    plt.title(name)
    plt.xlabel("Observation")
    plt.ylabel("Value")
    plt.savefig(path)
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

    plt.show()

def displays(model_path, x_train, y_train, x_test, y_test, history):
    model = load_model(model_path)
    y_test_pred = model.predict(x_test, batch_size=BATCH_SIZE)
    print("Prediction against truth:")
    print(y_test_pred[:5])
    print(y_test[:5])

    # Metrics...
    loss, mae, mse = model.evaluate(x_test, y_test, batch_size=BATCH_SIZE)
    max_difference = np.max(np.abs(y_test - y_test_pred))
    print("---- Metrics ----")
    print(f"Loss (scaled) {loss:.5f}")
    print(f"MAE (scaled) {mae:.5f}")
    print(f"MSE (scaled) {mse:.5f}")
    print(f"Maxdif (scaled) {max_difference:.5f}")

    plot_graph(y_test, y_test_pred, "Test", LOGS_OUTPUT_PATH + os.sep + "test.png")
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
def view_surface(model):
    if len(sys.argv) < 5:
        raise TypeError(f"Not enough argument given to the script (has {len(sys.argv)-1}, needs 4)")
    
    in1 = int(sys.argv[2])
    in2 = int(sys.argv[3])
    out = int(sys.argv[4])

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

    fig.colorbar(surface, shrink=0.5, aspect=5)

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
        surface = ax.plot_surface(X, Y, compute_surface(model, X, Y, i_sliders, in1, in2, out))
        fig.canvas.draw_idle()
    
    b_axes = fig.add_axes([0.8, 0.03, 0.1, 0.03])
    button = Button(b_axes, "Update", hovercolor="0.975")
    button.on_clicked(update)

    update(None)
    plt.show()


CMD_DICT = {
    "--surface": view_surface
}

def main():
    model = load_model(LOGS_OUTPUT_PATH + os.sep + LOGS_MODEL_CKPT)

    command = sys.argv[1]
    if command not in CMD_DICT:
        raise ValueError(f"Command {command} not found")
    
    action = CMD_DICT[command]
    action(model)


if __name__ == "__main__":
    main()

    