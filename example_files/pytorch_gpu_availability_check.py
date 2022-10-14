# Simple test script that checks for the availability of GPUs in PyTorch (CUDA or ROCm)
# See https://pytorch.org/get-started/locally/#linux-verification

import torch
print(torch.cuda.is_available())
if torch.cuda.is_available():
    print(f"Number of GPUs: {torch.cuda.device_count()}, GPU 0 name: {torch.cuda.get_device_name(0)}")
