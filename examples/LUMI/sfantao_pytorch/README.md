# sfantao PyTorch example

This is an example of containers that include a ROCm compatible PyTorch Conda environment for use with the GPU nodes on LUMI. It is based on the MNIST example given in the 10/2023 LUMI training "Tools in Action - An example with Pytorch" (https://lumi-supercomputer.github.io/LUMI-training-materials/4day-20231003/extra_4_10_Best_Practices_GPU_Optimization/). It also includes scripts for benchmarking containers created by cotainr against alternatives to running PyTorch on LUMI.

## Building the containers

On LUMI, the containers may be built using:

```bash
module load LUMI
module load cotainr
cotainr build lumi-sfantao-pytorch-lumi-base.sif --base-image=/appl/local/containers/sif-images/lumi-rocm-rocm-5.5.1.sif --conda-env=py311_rocm542_pytorch.yml
cotainr build lumi-sfantao-pytorch-rocm_docker-base.sif --system=lumi-g --conda-env=py311_rocm542_pytorch.yml
```

## Running the PyTorch examples on LUMI using the built container

Copy everything to LUMI, update the `--account=project_<your_project_id>` SBATCH directive in the SLURM batch scripts, and submit one of the SLURM batch scripts:

- 

**WARNING: These PyTorch examples have been created to showcase the use of the PyTorch container built using `cotainr`. They may or may not provide optimal performance on LUMI. Please consult official LUMI channels for guidance on performance optimizing code for LUMI.**


--gpus-per-task not working - see #5 under https://lumi-supercomputer.github.io/LUMI-training-materials/1day-20230921/notes_20230921/#running-jobs

- cotainr build lumi-sfantao-pytorch-lumi-base.sif --base-image=/appl/local/containers/sif-images/lumi-rocm-rocm-5.5.1.sif --conda-env=py311_rocm542_pytorch.yml --accept-licenses -vvv --log-to-file