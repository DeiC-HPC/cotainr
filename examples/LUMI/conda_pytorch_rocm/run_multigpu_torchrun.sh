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
#SBATCH --partition=small-g
#SBATCH --time=00:30:00
#SBATCH --account=project_<your_project_id>

export MIOPEN_USER_DB_PATH=/tmp/${USER}-miopen-cache-${SLURM_JOB_ID}
export MIOPEN_CUSTOM_CACHE_DIR=${MIOPEN_USER_DB_PATH}

srun singularity exec lumi_pytorch_rocm_demo.sif torchrun --standalone --nnodes=1 --nproc_per_node=gpu pytorch_multigpu_torchrun.py --total_epochs=10 --save_every=5
