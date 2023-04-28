import matplotlib.pyplot as plt
import numpy as np

from matplotlib import cm
from matplotlib.widgets import Slider, Button

from view import view_surface

def crab():
    x = np.arange(-5, 5, 0.25)
    y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(x, y)
    f0 = 1

    def f(X, Y, f):
        return np.sin(f * np.sqrt(X**2 + Y**2))

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    surface = ax.plot_surface(X, Y, f(X, Y, f0), cmap=cm.coolwarm, linewidth=0, antialiased=False)
    ax.set_zlim(-1.01, 1.01)
    # ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter("{x:.02f}")
    ax.set_xlabel("xlabel")
    ax.set_ylabel("ylabel")
    ax.set_zlabel("zlabel")

    fig.colorbar(surface, shrink=0.5, aspect=5)

    fig.subplots_adjust(bottom=0.3, top=1)
    #            tuple (left, bottom, width, height)
    axf = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    f_slider = Slider(
        ax=axf,
        label="f value",
        valmin=0.1,
        valmax=10,
        valinit=f0,
    )
    axt = fig.add_axes([0.25, 0.05, 0.65, 0.03])
    t_slider = Slider(
        ax=axt, label="truc", valmin=0, valmax=10, valinit=3
    )

    def update(val):
        ax.cla()
        surface = ax.plot_surface(X, Y, f(X, Y, t_slider.val))
        fig.canvas.draw_idle()

    f_slider.on_changed(update)
    t_slider.on_changed(update)

    resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
    button = Button(resetax, "Reset", hovercolor="0.975")

    def reset(event):
        f_slider.reset()

    button.on_clicked(reset)

    plt.show()

def main():
    view_surface(None)

if __name__ == "__main__":
    main()