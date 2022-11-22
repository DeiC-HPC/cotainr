# Conda PyTorch ROCm example

This is an example of a container that includes the full ROCm stack and a ROCm PyTorch compatible Conda environment for use with the GPU nodes on LUMI.

## Building the container

The container may be built using:

```bash
cotainr build lumi.sif --base-image docker://rocm/dev-ubuntu-22.04:5.3.2-complete --conda-env py39_pytorch_rocm.yml
```

## Running the examples

Copy everything to LUMI and submit one of the SLURM batch scripts:

- `run_gputest.sh`: Run a simple GPU test.
- `run_multigpu_torchrun.sh`: Run an example of training a neural network.

## Notes about the PyTorch ROCm example setup

The `py39_pytorch_rocm.yml` file was created via:

```bash
$ conda create -n py39_pytorch_rocm python=3.9 certifi charset-normalizer numpy pillow requests typing-extensions urllib3
$ conda activate py39_pytorch_rocm
$ pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/rocm5.2
$ conda env export --override-channels -c conda-forge -n py39_pytorch_rocm | sed "/^  - pip:/a\ \ \ \ - --extra-index-url https://download.pytorch.org/whl/rocm5.2" | grep -v "prefix" > py39_pytorch_rocm.yml
```
