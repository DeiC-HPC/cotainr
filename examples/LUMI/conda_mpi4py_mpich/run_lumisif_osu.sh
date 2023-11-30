#!/bin/bash -e
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the OSU benchmarks with Numpy buffers
# using the official LUMI mpi4py container
#
#SBATCH --job-name=mpi4py-lumisif-osu
#SBATCH --nodes=3
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:10:00
#SBATCH --account=project_<your_project_id>

PROJECT_DIR=
OSU_PY_BENCHMARK_DIR=$PROJECT_DIR/osu-micro-benchmarks-7.0.1/python
RESULTS_DIR=$PROJECT_DIR/osu_results
CONTAINER=lumi-mpi4py-rocm-5.4.5-python-3.10-mpi4py-3.1.4.sif

# Single node runs
srun --nodes=1 --ntasks=2 \
    singularity exec \
    --bind=$PROJECT_DIR \
    --bind=/var/spool/slurmd \
    --bind=/opt/cray \
    --bind=/usr/lib64/libcxi.so.1 \
    --bind=/usr/lib64/libjansson.so.4 \
    $PROJECT_DIR/containers/$CONTAINER \
    /bin/bash -e -c "\$WITH_CONDA; python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=bw --buffer=numpy" \
    > $RESULTS_DIR/$SLURM_JOB_NAME-bw-single-$CONTAINER.txt
srun --nodes=1 --ntasks=2 \
    singularity exec \
    --bind=$PROJECT_DIR \
    --bind=/var/spool/slurmd \
    --bind=/opt/cray \
    --bind=/usr/lib64/libcxi.so.1 \
    --bind=/usr/lib64/libjansson.so.4 \
    $PROJECT_DIR/containers/$CONTAINER \
    /bin/bash -e -c "\$WITH_CONDA; python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=latency --buffer=numpy" \
    > $RESULTS_DIR/$SLURM_JOB_NAME-latency-single-$CONTAINER.txt
srun --nodes=1 --ntasks=3 \
    singularity exec \
    --bind=$PROJECT_DIR \
    --bind=/var/spool/slurmd \
    --bind=/opt/cray \
    --bind=/usr/lib64/libcxi.so.1 \
    --bind=/usr/lib64/libjansson.so.4 \
    $PROJECT_DIR/containers/$CONTAINER \
    /bin/bash -e -c "\$WITH_CONDA; python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=allgather --buffer=numpy" \
    > $RESULTS_DIR/$SLURM_JOB_NAME-allgather-single-$CONTAINER.txt

# Multi node runs
srun --nodes=2 --ntasks=2 --tasks-per-node=1 \
    singularity exec \
    --bind=$PROJECT_DIR \
    --bind=/var/spool/slurmd \
    --bind=/opt/cray \
    --bind=/usr/lib64/libcxi.so.1 \
    --bind=/usr/lib64/libjansson.so.4 \
    $PROJECT_DIR/containers/$CONTAINER \
    /bin/bash -e -c "\$WITH_CONDA; python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=bw --buffer=numpy" \
    > $RESULTS_DIR/$SLURM_JOB_NAME-bw-multi-$CONTAINER.txt
srun --nodes=2 --ntasks=2 --tasks-per-node=1 \
    singularity exec \
    --bind=$PROJECT_DIR \
    --bind=/var/spool/slurmd \
    --bind=/opt/cray \
    --bind=/usr/lib64/libcxi.so.1 \
    --bind=/usr/lib64/libjansson.so.4 \
    $PROJECT_DIR/containers/$CONTAINER \
    /bin/bash -e -c "\$WITH_CONDA; python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=latency --buffer=numpy" \
    > $RESULTS_DIR/$SLURM_JOB_NAME-latency-multi-$CONTAINER.txt
srun --nodes=3 --ntasks=3 --tasks-per-node=1 \
    singularity exec \
    --bind=$PROJECT_DIR \
    --bind=/var/spool/slurmd \
    --bind=/opt/cray \
    --bind=/usr/lib64/libcxi.so.1 \
    --bind=/usr/lib64/libjansson.so.4 \
    $PROJECT_DIR/containers/$CONTAINER \
    /bin/bash -e -c "\$WITH_CONDA; python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=allgather --buffer=numpy" \
    > $RESULTS_DIR/$SLURM_JOB_NAME-allgather-multi-$CONTAINER.txt
