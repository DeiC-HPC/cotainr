#!/bin/bash -e
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the OSU benchmarks with Numpy buffers
# using a cotainr container including a generic MPICH, using the container MPI.
#
#SBATCH --job-name=mpi4py-cotainr-hybrid-osu
#SBATCH --nodes=3
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:30:00
#SBATCH --account=project_<your_project_id>

PROJECT_DIR=
OSU_PY_BENCHMARK_DIR=$PROJECT_DIR/osu-micro-benchmarks-7.3/python
RESULTS_DIR=$PROJECT_DIR/osu_results
CONTAINERS=(\
    "cotainr-mpich3-pip-mpi4py.sif" \
    "cotainr-mpich4-pip-mpi4py.sif")

set -x
mkdir -p $RESULTS_DIR

for container in ${CONTAINERS[@]}; do
    # Single node runs
    srun --nodes=1 --ntasks=2 --mpi=pmi2 \
        singularity exec \
        --bind=$PROJECT_DIR \
        $PROJECT_DIR/containers/$container \
        python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=bw --buffer=numpy \
        > $RESULTS_DIR/$SLURM_JOB_NAME-bw-single-$container.txt
    srun --nodes=1 --ntasks=2 --mpi=pmi2 \
        singularity exec \
        --bind=$PROJECT_DIR \
        $PROJECT_DIR/containers/$container \
        python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=latency --buffer=numpy \
        > $RESULTS_DIR/$SLURM_JOB_NAME-latency-single-$container.txt
    srun --nodes=1 --ntasks=2 --mpi=pmi2 \
        singularity exec \
        --bind=$PROJECT_DIR \
        $PROJECT_DIR/containers/$container \
        python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=allgather --buffer=numpy \
        > $RESULTS_DIR/$SLURM_JOB_NAME-allgather-single-$container.txt

    # Multi node runs
    srun --nodes=2 --ntasks=2 --tasks-per-node=1 --mpi=pmi2 \
        singularity exec \
        --bind=$PROJECT_DIR \
        $PROJECT_DIR/containers/$container \
        python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=bw --buffer=numpy \
        > $RESULTS_DIR/$SLURM_JOB_NAME-bw-multi-$container.txt
    srun --nodes=2 --ntasks=2 --tasks-per-node=1 --mpi=pmi2 \
        singularity exec \
        --bind=$PROJECT_DIR \
        $PROJECT_DIR/containers/$container \
        python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=latency --buffer=numpy \
        > $RESULTS_DIR/$SLURM_JOB_NAME-latency-multi-$container.txt
    srun --nodes=3 --ntasks=3 --tasks-per-node=1 --mpi=pmi2 \
        singularity exec \
        --bind=$PROJECT_DIR \
        $PROJECT_DIR/containers/$container \
        python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=allgather --buffer=numpy \
        > $RESULTS_DIR/$SLURM_JOB_NAME-allgather-multi-$container.txt
done
