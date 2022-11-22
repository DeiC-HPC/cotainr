#!/usr/bin/env bash
#SBATCH --job-name=pytorch_gputest_example
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --output="pytorch_gputest_example_%j.txt"
#SBATCH --partition=eap
#SBATCH --time=00:05:00
#SBATCH --account=project_465000238

singularity exec lumi_pytorch_rocm_demo.sif python pytorch_gputest.py
