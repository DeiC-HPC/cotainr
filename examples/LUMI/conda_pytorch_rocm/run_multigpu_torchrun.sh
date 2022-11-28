#!/usr/bin/env bash
#
# A LUMI SLURM batch script for the LUMI PyTorch multi GPU torchrun example from
# https://github.com/DeiC-HPC/cotainr
#
#SBATCH --job-name=multigpu_torchrun_example
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --gpus-per-task=8
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=eap
#SBATCH --time=00:30:00
#SBATCH --account=project_<your_project_id>

export NCCL_SOCKET_IFNAME=hsn0,hsn1,hsn2,hsn3

srun singularity exec lumi_pytorch_rocm_demo.sif torchrun --standalone --nnodes=1 --nproc_per_node=gpu pytorch_multigpu_torchrun.py --total_epochs=10 --save_every=5
