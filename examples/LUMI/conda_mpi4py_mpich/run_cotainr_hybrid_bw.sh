#!/usr/bin/env bash
#
# A LUMI SLURM batch script for the LUMI mpi4py MPICH example from
# https://github.com/DeiC-HPC/cotainr
# This script runs the OSU latency benchmark with Numpy buffers
# using a cotainr container including a generic MPICH, using the container MPI.
#
#SBATCH --job-name=mpi4py_osu_bw_cotainr_hybrid
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small
#SBATCH --exclusive
#SBATCH --time=00:30:00
#SBATCH --account=project_<your_project_id>

PROJECT_DIR=
OSU_PY_BENCHMARK_DIR=$PROJECT_DIR/osu-micro-benchmarks-7.0.1/python/
CONTAINER=$PROJECT_DIR/lumi_mpi4py_mpich_demo.sif

for i in {1..5}
do
echo "====================== OSU BW test run $i ======================"
srun --mpi=pmi2 singularity exec --bind=$PROJECT_DIR $CONTAINER python $OSU_PY_BENCHMARK_DIR/run.py --benchmark=bw --buffer=numpy
sleep 1
done
