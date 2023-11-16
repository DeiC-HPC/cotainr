#!/usr/bin/env bash
#
# A LUMI SLURM batch script for the LUMI Dedalus shear_flow.py example from
# https://github.com/DeiC-HPC/cotainr
#
#SBATCH --job-name=dedalus_shear_flow
#SBATCH --nodes=4
#SBATCH --tasks-per-node=128
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --time=00:30:00
#SBATCH --account=project_<your_project_id>

srun singularity exec lumi_dedalus_demo.sif python3 shear_flow.py
