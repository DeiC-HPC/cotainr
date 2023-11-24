#!/bin/bash -e
# This is a modified version of the 08-mnist-example.sh from the 10/2023 LUMI training
# "Tools in Action - An example with Pytorch"
# https://lumi-supercomputer.github.io/LUMI-training-materials/4day-20231003/extra_4_10_Best_Practices_GPU_Optimization/
#
#SBATCH --job-name=lumisif_mnist_example
#SBATCH --nodes=4
#SBATCH --gpus-per-node=8
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=7
#SBATCH --output="output_%x_%j.txt"
#SBATCH --partition=small-g
#SBATCH --mem=480G
#SBATCH --time=00:10:00
#SBATCH --account=project_<your_project_id>

set -x

PROJECT_DIR=
CONTAINER=$PROJECT_DIR/lumi-pytorch-rocm-5.5.1-python-3.10-pytorch-v2.0.1.sif

# Utility script to detect the master node
rm -rf $PROJECT_DIR/get-master.py
cat > $PROJECT_DIR/get-master.py << EOF
import argparse
def get_parser():
    parser = argparse.ArgumentParser(description="Extract master node name from Slurm node list",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("nodelist", help="Slurm nodelist")
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    first_nodelist = args.nodelist.split(',')[0]

    if '[' in first_nodelist:
        a = first_nodelist.split('[')
        first_node = a[0] + a[1].split('-')[0]

    else:
        first_node = first_nodelist

    print(first_node)
EOF

rm -rf $PROJECT_DIR/run-script.sh 
cat > $PROJECT_DIR/run-script.sh << EOF
#!/bin/bash -e

# Make sure GPUs are up
if [ \$SLURM_LOCALID -eq 0 ] ; then
    rocm-smi
fi
sleep 2

export MIOPEN_USER_DB_PATH="/tmp/$(whoami)-miopen-cache-\$SLURM_NODEID"
export MIOPEN_CUSTOM_CACHE_DIR=\$MIOPEN_USER_DB_PATH

# Set MIOpen cache to a temporary folder.
if [ \$SLURM_LOCALID -eq 0 ] ; then
    rm -rf \$MIOPEN_USER_DB_PATH
    mkdir -p \$MIOPEN_USER_DB_PATH
fi
sleep 2
  
# Report affinity
echo "Rank \$SLURM_PROCID --> \$(taskset -p \$\$)"

# Start conda environment inside the container
\$WITH_CONDA

# Set interfaces to be used by RCCL.
export NCCL_SOCKET_IFNAME=hsn0,hsn1,hsn2,hsn3

# Set environment for the app
export MASTER_ADDR=\$(python /workdir/get-master.py "\$SLURM_NODELIST")
export MASTER_PORT=29500
export WORLD_SIZE=\$SLURM_NPROCS
export RANK=\$SLURM_PROCID
export ROCR_VISIBLE_DEVICES=\$SLURM_LOCALID

# Run app
cd /workdir/mnist
python -u mnist_DDP.py --gpu --modelpath /workdir/mnist/model

EOF
chmod +x $PROJECT_DIR/run-script.sh

c=fe
MYMASKS="0x${c}000000000000,0x${c}00000000000000,0x${c}0000,0x${c}000000,0x${c},0x${c}00,0x${c}00000000,0x${c}0000000000"

srun --cpu-bind=mask_cpu:$MYMASKS \
  singularity exec \
    -B /var/spool/slurmd \
    -B /opt/cray \
    -B /usr/lib64/libcxi.so.1 \
    -B /usr/lib64/libjansson.so.4 \
    -B $PROJECT_DIR:/workdir \
    $CONTAINER /workdir/run-script.sh
