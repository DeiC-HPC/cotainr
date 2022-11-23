#!/usr/bin/env bash
#SBATCH --job-name=singlegpu_gputest_example
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=eap
#SBATCH --time=00:05:00
#SBATCH --account=project_465000238

srun singularity exec lumi_pytorch_rocm_demo.sif python pytorch_singlegpu_gputest.py
