#!/bin/bash
module load LUMI/23.03
module load cotainr
cotainr build cotainr-mpich3-conda-mpi4py.sif --system=lumi-c --conda-env py310_mpich3_conda_mpi4py.yml --accept-licenses
cotainr build cotainr-mpich3-pip-mpi4py.sif --system=lumi-c --conda-env py310_mpich3_pip_mpi4py.yml --accept-licenses
cotainr build cotainr-mpich4-conda-mpi4py.sif --system=lumi-c --conda-env py310_mpich4_conda_mpi4py.yml --accept-licenses
cotainr build cotainr-mpich4-pip-mpi4py.sif --system=lumi-c --conda-env py310_mpich4_pip_mpi4py.yml --accept-licenses
