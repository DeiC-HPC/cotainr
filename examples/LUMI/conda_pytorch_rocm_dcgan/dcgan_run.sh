#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --output="output_%j.txt"
#SBATCH --partition=pilot
#SBATCH --time=00:10:00
#SBATCH --account=project_462000008

# 1 GPU
singularity exec py39_pytorch_rocm5.3-complete.sif python pytorch_dcgan.py --dataset=mnist --workers=8 --dataroot=data --ngf=128 --ndf=128 --niter=1 --cuda --ngpu=1 --manualSeed=6021 --outf=checkpoints

# 8 GPUs
# https://rt.lumi-supercomputer.eu/Ticket/Display.html?id=853
#export NCCL_SOCKET_IFNAME=hsn0,hsn1,hsn2,hsn3
#export NCCL_NET_GDR_LEVEL=3
#singularity exec py39_pytorch_rocm5.3-complete.sif python pytorch_dcgan.py --dataset=mnist --workers=8 --dataroot=data --ngf=256 --ndf=256 --niter=1 --cuda --ngpu=8 --manualSeed=6021 --outf=checkpoints
