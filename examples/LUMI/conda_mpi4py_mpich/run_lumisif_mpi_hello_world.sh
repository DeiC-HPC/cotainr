#!/usr/bin/env bash
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the MPI hello world script
# using the official LUMI mpi4py container
#
#SBATCH --job-name=mpi4py_mpi_hello_world_lumisif
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:05:00
#SBATCH --account=project_<your_project_id>

PROJECT_DIR=
CONTAINER=$PROJECT_DIR/containers/lumi-mpi4py-rocm-5.4.5-python-3.10-mpi4py-3.1.4.sif

rm -rf $PROJECT_DIR/run-script.sh 
cat > $PROJECT_DIR/run-script.sh << EOF
#!/bin/bash -e

# Start conda environment inside the container
\$WITH_CONDA

# Run application
python $PROJECT_DIR/mpi_hello_world.py

EOF
chmod +x $PROJECT_DIR/run-script.sh

export MPIR_CVAR_DEBUG_SUMMARY=1
export FI_LOG_LEVEL=Info

srun singularity exec \
    --bind=$PROJECT_DIR \
    --bind=/var/spool/slurmd \
    --bind=/opt/cray \
    --bind=/usr/lib64/libcxi.so.1 \
    --bind=/usr/lib64/libjansson.so.4 \
    $CONTAINER $PROJECT_DIR/run-script.sh
