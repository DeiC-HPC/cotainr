# Record of the PyTorch ROCm example setup

## Create and export the conda environment (on laptop)
conda create -n py39_pytorch_rocm python=3.9 certifi charset-normalizer numpy pillow requests typing-extensions urllib3
conda activate py39_pytorch_rocm
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/rocm5.1.1
conda env export --override-channels -c conda-forge -n py39_pytorch_rocm | sed "/^  - pip:/a\ \ \ \ - --extra-index-url https://download.pytorch.org/whl/rocm5.1.1" | grep -v "prefix" > example_files/py39_pytorch_rocm.yml

[//]: # (PyTorch installed via pip as suggested in the official documentation: https://pytorch.org/get-started/locally/#start-locally)
[//]: # (In the above we modify the conda env file to include the pip --extra-index-url, based on https://stackoverflow.com/a/73288251, otherwise pip fails when installing the exported environment)

## Create container which includes the conda environment (on laptop)
 python3 builder/cli.py build py39_pytorch_rocm.sif --base-image=docker://ubuntu:22.04 --conda-env=example_files/py39_pytorch_rocm.yml
 
## Move everything to raxos for testing
scp example_files/pytorch_gpu_availability_check.py raxos:~/pytorch_singularity_test/
scp py39_pytorch_rocm.sif raxos:~/pytorch_singularity_test/


## Run the GPU availability check test script
chrso@raxos:~/pytorch_singularity_test$ singularity exec py39_pytorch_rocm.sif python pytorch_gpu_availability_check.py
True

chrso@raxos:~/pytorch_singularity_test$ singularity exec --rocm py39_pytorch_rocm.sif python pytorch_gpu_availability_check.py
Traceback (most recent call last):
  File "/home/chrso/pytorch_singularity_test/pytorch_gpu_availability_check.py", line 4, in <module>
    import torch
  File "/opt/conda/envs/conda_container_env/lib/python3.9/site-packages/torch/__init__.py", line 202, in <module>
    from torch._C import *  # noqa: F403
ImportError: librocm_smi64.so.5: cannot open shared object file: No such file or directory


## Running on LUMI
`rocm/dev-ubuntu-20.04` packages work, if you choose the `complete` versions:
`python3 builder/cli.py build py39_pytorch_rocm5.3-complete.sif --base-image=docker://rocm/dev-ubuntu-20.04:5.3-complete --conda-env=example_files/py39_pytorch_rocm.yml`

You cannot run with the `--rocm` flag on LUMI. It gives errors.

Slurm script for test:
```bash
#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output="output_%j.txt"
#SBATCH --partition=pilot
#SBATCH --time=00:05:00
#SBATCH --account=project_462000008

#module load PrgEnv-amd

#echo "HOST"
#ls -la /dev/dri
#echo "CONTAINER"
#singularity exec py39_pytorch_rocm.sif ls -la /dev/dri
#singularity exec py39_pytorch_rocm.sif python pytorch_gpu_availability_check.py 
#rocm-smi
#rocminfo
singularity exec py39_pytorch_rocm5.3-complete.sif python pytorch_gputest.py
#singularity exec py39_pytorch_rocm5.3-complete.sif python pytorch_multigpu.py
```

gpu test output
```
True
Number of GPUs: 8, GPU 0 name:
```

`rocm-smi` output:
```
======================= ROCm System Management Interface =======================
================================= Concise Info =================================
GPU  Temp   AvgPwr  SCLK    MCLK     Fan  Perf  PwrCap  VRAM%  GPU%
0    45.0c  92.0W   800Mhz  1600Mhz  0%   auto  560.0W    0%   0%
1    44.0c  N/A     800Mhz  1600Mhz  0%   auto  0.0W      0%   0%
2    45.0c  89.0W   800Mhz  1600Mhz  0%   auto  560.0W    0%   0%
3    44.0c  N/A     800Mhz  1600Mhz  0%   auto  0.0W      0%   0%
4    45.0c  88.0W   800Mhz  1600Mhz  0%   auto  560.0W    0%   0%
5    45.0c  N/A     800Mhz  1600Mhz  0%   auto  0.0W      0%   0%
6    42.0c  89.0W   800Mhz  1600Mhz  0%   auto  560.0W    0%   0%
7    42.0c  N/A     800Mhz  1600Mhz  0%   auto  0.0W      0%   0%
================================================================================
============================= End of ROCm SMI Log ==============================
```
