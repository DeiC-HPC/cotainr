#!/bin/bash -e
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the MPI hello world script
# using the LUMI cray-python module
#
#SBATCH --job-name=mpi4py_mpi_hello_world_cray-python
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:05:00
#SBATCH --account=project_<your_project_id>

module load cray-python

PROJECT_DIR=

export MPIR_CVAR_DEBUG_SUMMARY=1
export FI_LOG_LEVEL=Info

srun python3 $PROJECT_DIR/mpi_hello_world.py
