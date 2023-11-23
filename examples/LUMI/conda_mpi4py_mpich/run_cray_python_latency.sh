#!/usr/bin/env bash
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the OSU latency benchmark with Numpy buffers
# using the LUMI cray-python module
#
#SBATCH --job-name=mpi4py_osu_latency_cray-python
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:10:00
#SBATCH --account=project_<your_project_id>

module load cray-python

PROJECT_DIR=
OSU_PY_BENCHMARK_DIR=$PROJECT_DIR/osu-micro-benchmarks-7.0.1/python/

for i in {1..5}
do
echo "====================== OSU BW test run $i ======================"
srun python $OSU_PY_BENCHMARK_DIR/run.py --benchmark=latency --buffer=numpy
sleep 1
done
