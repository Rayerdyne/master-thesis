import numpy as np
from tensorflow.keras.layers import Normalization

def trick_distr(mean: np.ndarray, var: np.ndarray):
    return np.row_stack([mean - var, mean + var])

def inverse_normalization(norm: Normalization, dim=4) -> Normalization:
    n0 = norm(np.zeros(dim))
    n1 = norm(np.ones(dim))
    var = 1 / (n1 - n0)
    mu = -n0 * var
    
    denorm = Normalization(axis=-1)
    denorm.adapt(trick_distr(-(mu/var), 1/var))
    return denorm

def main():
    norm = Normalization(axis=-1)
    mu = np.array([0, 0, 10, 10])
    var = np.array([1, 2, 1, 2])
    norm.adapt(trick_distr(mu, var))

    print(norm(np.array([[0, 0, 10, 10], [1, 2, 11, 12], [2, 4, 12, 14]])))

    denorm = inverse_normalization(norm)

    print(denorm(np.array([[0, 0, 0, 0], [1, 1, 1, 1], [2, 2, 2, 2]])))

    print(norm(denorm(np.array([[0, 0, 0, 0], [1, 1, 1, 1]]))))

if __name__ == "__main__":
    main()