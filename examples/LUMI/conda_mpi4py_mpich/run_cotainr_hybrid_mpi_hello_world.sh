#!/usr/bin/env bash
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the MPI hello world script
# using a cotainr container including a generic MPICH, using the container MPI.
#
#SBATCH --job-name=mpi4py_mpi_hello_world_cotainr_hybrid
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:30:00
#SBATCH --account=project_<your_project_id>

PROJECT_DIR=
CONTAINER=$PROJECT_DIR/lumi_mpi4py_mpich_demo.sif

export MPIR_CVAR_DEBUG_SUMMARY=1
export FI_LOG_LEVEL=Info

srun --mpi=pmi2 singularity exec --bind=$PROJECT_DIR $CONTAINER python $PROJECT_DIR/mpi_hello_world.py
