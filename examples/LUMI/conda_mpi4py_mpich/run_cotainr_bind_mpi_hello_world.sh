#!/usr/bin/env bash
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the MPI hello world script
# using a cotainr container including a generic MPICH, bind mounting the host MPI.
#
#SBATCH --job-name=mpi4py_mpi_hello_world_cotainr_bind
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:10:00
#SBATCH --account=project_<your_project_id>

PROJECT_DIR=
CONTAINERS=(\
    "cotainr-mpich3-conda-mpi4py.sif" \
    "cotainr-mpich3-pip-mpi4py.sif" \
    "cotainr-mpich4-conda-mpi4py.sif" \
    "cotainr-mpich4-pip-mpi4py.sif")

export MPIR_CVAR_DEBUG_SUMMARY=1
export FI_LOG_LEVEL=Info

source lumi-singularity-bindings.sh  # or use the LUMI singularity-bindings module

for container in ${CONTAINERS[@]}; do
    echo "=============== Run using $container ==============="
    srun singularity exec \
        --bind=$PROJECT_DIR \
        $PROJECT_DIR/containers/$container \
        python3 $PROJECT_DIR/mpi_hello_world.py
done
