import numpy as np
from env_var import env

nodelist = env("SLURM_JOB_NODELIST").as_string().required()
array_sum = np.array([1, 5, 7, 12, 17]).sum()

print(f"Hello from {nodelist}; The answer is {array_sum}!")
