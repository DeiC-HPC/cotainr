import numpy as np

N = 2048
rng = np.random.default_rng(seed=6021)
A = rng.normal(size=(N, N))
B = rng.normal(size=(N, N))
C = A @ B

print(C.mean())
