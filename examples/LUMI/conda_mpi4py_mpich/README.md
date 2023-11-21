# Conda mpi4py MPICH example

This is an example of a container that includes a MPICH compatible mpi4py Conda environment for use with the CPU nodes on LUMI. It also includes scripts for benchmarking a container created by cotainr against alternatives to running mpi4py on LUMI.

## Building the container

On LUMI, the container may be built using:

```bash
module load LUMI
module load cotainr
cotainr build lumi_mpi4py_mpich_demo.sif --system=lumi-c --conda-env py310_mpi4py_mpich.yml
```

## Running the PyTorch examples on LUMI using the built container

Copy everything to LUMI, update the `--account=project_<your_project_id>` SBATCH directive in the SLURM batch scripts, and submit one of the SLURM batch scripts:

- 

**WARNING: These mpi4py examples have been created to showcase the use of the mpi4py container built using `cotainr`. They may or may not provide optimal performance on LUMI. Please consult official LUMI channels for guidance on performance optimizing code for LUMI.**



TODO:
- Ideally, update the conda numpy package to 1.26.1, though it may be a problem: https://github.com/conda-forge/numpy-feedstock/pull/302


wget http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.0.1.tar.gz
tar -xvf osu-micro-benchmarks-7.0.1.tar.gz osu-micro-benchmarks-7.0.1/python/


http://nowlab.cse.ohio-state.edu/static/media/talks/slide/Alnaasan-OMB-Py-osu-booth.pdf
https://pawseysc.github.io/containers-astro-python-workshop/3.hpc/index.html