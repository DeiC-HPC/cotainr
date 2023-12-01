#!/bin/bash -e
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the OSU benchmarks with Numpy buffers
# using the LUMI cray-python module
#
#SBATCH --job-name=mpi4py-cray-python-osu
#SBATCH --nodes=3
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:10:00
#SBATCH --account=project_<your_project_id>

module load cray-python/3.10.10

PROJECT_DIR=
OSU_PY_BENCHMARK_DIR=$PROJECT_DIR/osu-micro-benchmarks-7.3/python
RESULTS_DIR=$PROJECT_DIR/osu_results

set -x
mkdir -p $RESULTS_DIR

# Single node runs
srun --nodes=1 --ntasks=2 \
    python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=bw --buffer=numpy \
    > $RESULTS_DIR/$SLURM_JOB_NAME-bw-single.txt
srun --nodes=1 --ntasks=2 \
    python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=latency --buffer=numpy \
    > $RESULTS_DIR/$SLURM_JOB_NAME-latency-single.txt
srun --nodes=1 --ntasks=3 \
    python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=allgather --buffer=numpy \
    > $RESULTS_DIR/$SLURM_JOB_NAME-allgather-single.txt

# Multi node runs
srun --nodes=2 --ntasks=2 --tasks-per-node=1 \
    python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=bw --buffer=numpy \
    > $RESULTS_DIR/$SLURM_JOB_NAME-bw-multi.txt
srun --nodes=2 --ntasks=2 --tasks-per-node=1 \
    python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=latency --buffer=numpy \
    > $RESULTS_DIR/$SLURM_JOB_NAME-latency-multi.txt
srun --nodes=3 --ntasks=3 --tasks-per-node=1 \
    python3 $OSU_PY_BENCHMARK_DIR/run.py --benchmark=allgather --buffer=numpy \
    > $RESULTS_DIR/$SLURM_JOB_NAME-allgather-multi.txt
