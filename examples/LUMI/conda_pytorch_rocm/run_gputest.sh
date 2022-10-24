#!/usr/bin/env bash
#SBATCH --job-name=pytorch_gputest_example
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --output="pytorch_dcgan_example_%j.txt"
#SBATCH --partition=pilot
#SBATCH --time=00:05:00
#SBATCH --account=project_462000008

singularity exec py39_pytorch_rocm5.3-complete.sif python pytorch_gputest.py
