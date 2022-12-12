---
marp: true
headingDivider: 2
---

# PyTorch on LUMI-G

DeiC

# LUMI-G status as of 2022-12-13

- Pilot phase extended to January 9th, 2023 (**pilot** SLURM partition - not billed)
- Early access platform (EAP) still accessible to all users (**eap** SLURM partition - not billed)
- Access for regular usage coming *soon* (**gpu?** SLURM partition)
- Hardware triage and fixing almost complete
- A lot of known issues with the software stack (update expected early January)
- A lot of known configuration issues
- HPE acceptance tests still on-going

## General issues

- "Random" network failures (when using multiple nodes)
- "Random" filesystem hangs
- Occasional problems with login nodes
- Some SLURM resource requests result in strange errors
- CPU core #0 reserved for "low noise mode" on LUMI-G nodes

## Specific PyTorch related issues and workarounds

- GPU interface initialization errors (set `NCCL_SOCKET_IFNAME=hsn0,hsn1,hsn2,hsn3` manually)
- GPU NUMA region binding is wrong (use `srun --cpu-bind=map_cpu=1,8,16,24,32,40,48,56 --gpu-bind=map_gpu:4,5,2,3,6,7,0,1` for best performance)
- Official PyTorch pip wheel does not include compiled MIOpen kernels (`gfx90a6e.kdb`) - just accept the extra compilation time for now...

# Getting started with PyTorch on LUMI-G

- Use **`cotainr`** to build a Singularity container based on a **conda environment** which includes the official **PyTorch ROCm pip wheel** (and any other conda/pip packages, you need).
- Use **`torchrun`** to launch PyTorch.
- See the cotainr examples for a basic **SLURM script for a PyTorch Singularity container on LUMI-G** as well as an example using **`DistributedDataParallel** for training on multiple GPUs.

## Additional PyTorch related notes

- Generally, spawn one Python process per GPU (handled by `torchrun`), potentially each with multiple threads for data loading
- Use `rocm-smi` to check GPU utilization in an interactive session on the node:
  - Get an interactive session using: `srun --jobid=<pytorch_job_id> --interactive --pty $SHELL`
- Using multiple nodes for training *should* also work:
  - The `aws-ofi-rccl` plugin is needed
  - Other workarounds *may* be needed
  - Contact DeiC and/or LUST for more info if needed

## Storing and loading data on LUMI

- Performance of the Lustre filesystem on LUMI plummets (for all users) when you load large datasets consisting of many small files
- No "solution" yet - on the DeiC HPC 2023 roadmap
- Possible solutions/workarounds:
  - Just load from `/scratch` as you would normally do - but beware that it might be a bottleneck
  - Copy data to node local in-memory `/tmp` - but remember to allocate enough memory for it and manually clean-up when done
  - Use a single file "storage format" on `/scratch` (e.g. Tarball, Zarr ZipStore/..., or HDF5)

# Getting started on LUMI

- Getting Started guide on LUMI documentation: https://docs.lumi-supercomputer.eu/
- Take note of storage option: https://docs.lumi-supercomputer.eu/runjobs/lumi_env/storing-data/
- Running container jobs: https://docs.lumi-supercomputer.eu/runjobs/scheduled-jobs/container-jobs/
- LUMI-G documentation:
  - https://docs.lumi-supercomputer.eu/hardware/compute/eap/
  - https://docs.lumi-supercomputer.eu/hardware/compute/lumig/

## LUMI User Support Team

Don't hesitate to ask for help if things don't work: https://lumi-supercomputer.eu/user-support/need-help/
