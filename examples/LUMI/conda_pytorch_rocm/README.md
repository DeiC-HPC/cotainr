# Conda PyTorch ROCm example

This is an example of a container that includes the full ROCm stack and a ROCm compatible PyTorch Conda environment for use with the GPU nodes on LUMI. It uses an official AMD ROCm base image from <https://hub.docker.com/u/rocm> and the official PyTorch ROCm pip wheels from <https://download.pytorch.org/whl/rocm5.2/>.

## Building the container

The container may be built using:

```bash
cotainr build lumi_pytorch_rocm_demo.sif --base-image docker://rocm/dev-ubuntu-22.04:5.3.2-complete --conda-env py39_pytorch_rocm.yml
```

## Running the PyTorch examples on LUMI using the built container

Copy everything to LUMI and submit one of the SLURM batch scripts:

- `run_singlegpu_gputest.sh`: Run a simple GPU test on a single GPU.
- `run_multigpu_torchrun.sh`: Run an example of training a neural network on all GPUs on a single compute node.

**WARNING: These PyTorch examples have been created to showcase the use of the ROCm PyTorch container built using `cotainr`. They may or may not provide optimal performance on LUMI. Please consult official LUMI channels for guidance on performance optimizing code for LUMI.**

## Notes about the PyTorch ROCm example setup

The `py39_pytorch_rocm.yml` file was created via:

```bash
$ conda create -n py39_pytorch_rocm python=3.9 certifi charset-normalizer numpy pillow requests typing-extensions urllib3
$ conda activate py39_pytorch_rocm
$ pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/rocm5.2
$ conda env export --override-channels -c conda-forge -n py39_pytorch_rocm | sed "/^  - pip:/a\ \ \ \ - --extra-index-url https://download.pytorch.org/whl/rocm5.2" | grep -v "prefix" > py39_pytorch_rocm.yml
```
