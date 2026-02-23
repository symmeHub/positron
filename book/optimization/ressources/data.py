import numpy as np


def gen_data(A=0.1, T=0.90, y0=1.0):
    x = np.linspace(0, 40, 300)
    # non-linera function with some noise
    y = (y0 + A * x) * (1 - np.exp(-x / T)) + np.random.normal(0, 0.05, x.shape)
    return x, y
