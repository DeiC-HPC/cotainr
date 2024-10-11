# Conda PyTorch ROCm example

This is an example of a container that includes a ROCm compatible PyTorch Conda environment for use with the GPU nodes on LUMI. It uses the official PyTorch ROCm pip wheels from <https://download.pytorch.org/whl/rocm5.4.2/>.

## Building the container

On LUMI, the container may be built using:

```bash
module load LUMI
module load cotainr
cotainr build lumi_pytorch_rocm_demo.sif --system=lumi-g --conda-env minimal_pytorch.yml
```

## Running the PyTorch examples on LUMI using the built container

Copy everything to LUMI, update the `--account=project_<your_project_id>` SBATCH directive in the SLURM batch scripts, and submit one of the SLURM batch scripts:

- `run_singlegpu_gputest.sh`: Run a simple GPU test on a single GPU.
- `run_multigpu_torchrun.sh`: Run an example of training a neural network on all GPUs on a single compute node.

**WARNING: These PyTorch examples have been created to showcase the use of the ROCm PyTorch container built using `cotainr`. They may or may not provide optimal performance on LUMI. Please consult official LUMI channels for guidance on performance optimizing code for LUMI.**
