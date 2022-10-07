# Simple test script that checks for the availability of GPUs in PyTorch (CUDA or ROCm)
# See https://pytorch.org/get-started/locally/#linux-verification

import torch
print(torch.cuda.is_available())
