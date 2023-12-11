# sfantao PyTorch example

This is an example of containers that include a ROCm compatible PyTorch Conda environment for use with the GPU nodes on LUMI. It is based on the MNIST example given in the 10/2023 LUMI training "Tools in Action - An example with Pytorch" (https://lumi-supercomputer.github.io/LUMI-training-materials/4day-20231003/extra_4_10_Best_Practices_GPU_Optimization/). It also includes scripts for benchmarking containers created by cotainr against alternatives to running PyTorch on LUMI.

## Building the containers

On LUMI, the containers may be built using:

```bash
module load LUMI
module load cotainr
cotainr build lumi-sfantao-pytorch-lumi-base.sif --base-image=/appl/local/containers/sif-images/lumi-rocm-rocm-5.5.1.sif --conda-env=py311_rocm542_pytorch.yml
cotainr build lumi-sfantao-pytorch-rocm-docker-base.sif --system=lumi-g --conda-env=py311_rocm542_pytorch.yml
```

## Running the PyTorch examples on LUMI using the built container

Copy everything to LUMI, update the `--account=project_<your_project_id>` SBATCH directive in the SLURM batch scripts as well as the PROJECT_DIR to the directory, you copied everything to on LUMI, and submit *one* of the SLURM batch scripts:

- `run_cotainr_docker_base_mnist_example.sh`: Run the MNIST example using a cotainr container based on an official ROCm docker image (docker://rocm/dev-ubuntu-22.04:5.6.1-complete).
- `run_cotainr_lumisif_base_mnist_example.sh`: Run the MNIST example using a cotainr container based on the official LUMI PyTorch container (/appl/local/containers/sif-images/lumi-rocm-rocm-5.5.1.sif)
- `run_lumisif_mnist_example.sh`: Run the NMIST example using the offical LUMI PyTorch container (/appl/local/containers/sif-images/lumi-rocm-rocm-5.5.1.sif)

**WARNING: These PyTorch examples have been created to showcase the use of the PyTorch container built using `cotainr`. They may or may not provide optimal performance on LUMI. Please consult official LUMI channels for guidance on performance optimizing code for LUMI.**

## MNIST Test/benchmark results

Running the above SLURM batch scripts and looking through the output files, you get something like:

| Approach | NCCL INFO NET/* | GPU training time |
| -------- | ----------------- | ----------------- |
| `run_cotainr_docker_base_mnist_example.sh` | Using network Socket | 0:00:16 |
| `run_cotainr_lumisif_base_mnist_example.sh` | Using aws-ofi-rccl 1.4.0 / Selected Provider is cxi | 0:00:20 |
| `run_lumisif_mnist_example.sh` | Using aws-ofi-rccl 1.4.0 / Selected Provider is cxi | 0:00:21 |

## Notes

- The `lumi-sfantao-pytorch-rocm-docker-base.sif` container is based on the official LUMI PyTorch container since (as of writing) the PyTorch container is the only container that includes both a ROCm stack and the aws-ofi-rccl plugin. By using this container as a base image we end up with two Python/PyTorch environments in the container - both the one provided with the base image and the one added by cotainr.
- Only submit one of the above SLURM batch scripts at a time since they overwrite the run-script.sh, etc.
- The --gpus-per-task flag is not working correctly on LUMI - see #5 under https://lumi-supercomputer.github.io/LUMI-training-materials/1day-20230921/notes_20230921/#running-jobs
- When relying on sockets for NCCL communication, it seems that it sometimes randomly crashes with an error like (this needs more debugging on its own):

```python
Traceback (most recent call last):
  File "/workdir/mnist/mnist_DDP.py", line 261, in <module>
    run(modelpath=args.modelpath, gpu=args.gpu)
  File "/workdir/mnist/mnist_DDP.py", line 205, in run
    average_gradients(model)
  File "/workdir/mnist/mnist_DDP.py", line 170, in average_gradients
    group = dist.new_group([0])
            ^^^^^^^^^^^^^^^^^^^
  File "/opt/conda/envs/conda_container_env/lib/python3.11/site-packages/torch/distributed/distributed_c10d.py", line 3544, in new_group
    _store_based_barrier(global_rank, default_store, timeout)
  File "/opt/conda/envs/conda_container_env/lib/python3.11/site-packages/torch/distributed/distributed_c10d.py", line 456, in _store_based_barrier
    worker_count = store.add(store_key, 0)
                   ^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Connection reset by peer
```