import numpy as np
import tensorflow as tf

def main():
    model = tf.keras.Sequential()
    model.add(tf.keras.Input(shape=(4,), name="groub"))
    model.add(tf.keras.layers.Dense(units=4))
    model.add(tf.keras.layers.Dense(units=2))

    optimizer = tf.keras.optimizers.Adam()
    model.compile(optimizer=optimizer, loss="mse")

    x = np.array([[1, 1, 1, 1], [1, 2, 3, 4], [0, 0, 0, 0]])
    out = model(x)
    print("out", out)

    # model.add(tf.keras.layers.Dense(units=3))
    norm = tf.keras.layers.Normalization()
    norm.adapt(np.array([[-1, -1, -1, -1], [0, 0, 0, 0], [1, 1, 1, 1]]))

    norm2 = tf.keras.layers.Normalization()
    norm2.adapt(np.array([[-1, -1], [0, 0], [1, 1]]))


    model.add(norm2)

    model2 = tf.keras.Sequential()
    model2.add(tf.keras.Input(shape=(4,), name="groub"))
    model2.add(norm)
    model2.add(model)
    model2.add(norm2)
    # model2.compile(optimizer=optimizer, loss="mse")
    

    print(model2(x))
    model2.save("coucou.modelcool.tf", save_format="tf")



if __name__ == "__main__":
    main()