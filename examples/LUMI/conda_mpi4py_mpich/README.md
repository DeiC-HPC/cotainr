# Conda mpi4py MPICH example

This is an example of a container that includes a MPICH compatible mpi4py Conda environment for use with the CPU nodes on LUMI. It also includes scripts for benchmarking a container created by cotainr against alternatives to running [mpi4py](https://mpi4py.readthedocs.io/en/stable/) on LUMI.

**WARNING: These mpi4py examples have been created to showcase the use of the mpi4py container built using `cotainr`. They may or may not provide optimal performance on LUMI. Please consult official LUMI channels for guidance on performance optimizing code for LUMI.**

## TL;DR - How should I build a mpi4py MPICH container for LUMI using cotainr?

Install MPICH v3 using conda and install mpi4py using pip, e.g. on LUMI:

```bash
module load LUMI
module load cotainr
cotainr build lumi-mpi4py-mpich-demo.sif --system=lumi-c --conda-env py310_mpich3_pip_mpi4py.yml
```

with `py310_mpich3_pip_mpi4py.yml` from the `./containers` folder updated to your needs.

When running the container, remember to add the `--mpi=pmi2` option to `srun` when using the MPICH installed by conda, or, alternatively, bind mount the host Cray-MPICH in the container, **NOT** specifying `--mpi-pmi2` but using the default `cray_shasta` instead.

## Test/benchmark examples using mpi4py

Included in this example is a set of scripts that may be used to test and evaluate the following approaches to running mpi4py on LUMI-C:

- **cotainr-hybrid-mpich3-conda**: A cotainr singularity container built from the `./containers/py310_mpich3_pip_mpi4py.yml` conda environment, using the MPICH v3 installed by conda and mpi4py installed by conda.
- **cotainr-hybrid-mpich4-conda**: A cotainr singularity container built from the `./containers/py310_mpich4_pip_mpi4py.yml` conda environment, using the MPICH v4 installed by conda and mpi4py installed by conda.
- **cotainr-bind-mpich3-conda**: A cotainr singularity container built from the `./containers/py310_mpich3_pip_mpi4py.yml` conda environment, bind mounting the host MPICH in the container at runtime and using the mpi4py installed by conda.
- **cotainr-bind-mpich4-conda**: A cotainr singularity container built from the `./containers/py310_mpich4_pip_mpi4py.yml` conda environment, bind mounting the host MPICH in the container at runtime and using the mpi4py installed by conda.
- **cotainr-hybrid-mpich3-pip**: A cotainr singularity container built from the `./containers/py310_mpich3_pip_mpi4py.yml` conda environment, using the MPICH v3 installed by conda and mpi4py installed by pip.
- **cotainr-hybrid-mpich4-pip**: A cotainr singularity container built from the `./containers/py310_mpich4_pip_mpi4py.yml` conda environment, using the MPICH v4 installed by conda and mpi4py installed by pip.
- **cotainr-bind-mpich3-pip**: A cotainr singularity container built from the `./containers/py310_mpich3_pip_mpi4py.yml` conda environment, bind mounting the host MPICH in the container at runtime and using the mpi4py installed by pip.
- **cotainr-bind-mpich4-pip**: A cotainr singularity container built from the `./containers/py310_mpich4_pip_mpi4py.yml` conda environment, bind mounting the host MPICH in the container at runtime and using the mpi4py installed by pip.
- **cray-python**: The cray-python/3.10.10 module on LUMI.
- **lumi-sif**: The official LUMI mpi4py singularity container (found under /appl/local/containers/sif-images/lumi-mpi4py-rocm-5.4.5-python-3.10-mpi4py-3.1.4.sif)

The cotainr containers may be built on LUMI by copying the `./containers` folder to LUMI and running the `./containers/build_containers.sh` script.

## Running the mpi4py MPI hello world examples on LUMI

Copy everything in this example to LUMI and make sure you have built the containers as specified above. Update the `--account=project_<your_project_id>` SBATCH directive and `RPOJECT_DIR` in the `run_*_mpi_hello_world.sh` SLURM batch scripts. The `PROJECT_DIR` should point to the folder, you copied all files in this example to. Then submit one or more of the SLURM batch scripts.

### Lessons learned from these MPI hello world examples

Submitting all the `run_*_mpi_hello_world.sh` SLURM batch scripts and studying the output files, one becomes clear that:

- You can't use the host MPICH with an mpi4py installed by conda. [Conda packages sets RPATH](https://github.com/conda/conda-build/blob/main/docs/source/resources/compiler-tools.rst#anaconda-compilers-implicitly-add-rpath-pointing-to-the-conda-environment), preventing you from overriding shared objects via `LD_LIBRARY_PATH`. Installing mpi4py via pip allows you to escape the conda sandbox and use the `LD_LIBRARY_PATH` trick to use the host MPICH.
- When using the MPICH installed by conda, you must specify `--mpi=pmi2` to `srun`. Similarly, you must use `--mpi=cray_shasta` (the default on LUMI) when using the host MPICH. Otherwise, the MPI ranks will not be able to see each other, i.e. in the hello world example, they all report "I am rank 0 of 1".
- When using the MPICH provided by conda, it falls back to using sockets for communication between nodes, instead of the cray-libfabric cxi provider.
- It appears that both v3 and v4 versions of MPICH installed via conda are [ABI compatible](https://www.mpich.org/abi/) with the Cray-MPICH v8.1.27 on LUMI, though officially it is probably only v3 that is supported.

## Running the mpi4py OSU benchmarks on LUMI

Copy everything in this example to LUMI and make sure you have built the containers as specified above. Update the `--account=project_<your_project_id>` SBATCH directive and `RPOJECT_DIR` in the `run_*_osu.sh` SLURM batch scripts. The `PROJECT_DIR` should point to the folder, you copied all files in this example to. In your `PROJECT_DIR`, download and extract the OSU v7.3 tarball:

```bash
wget http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.3.tar.gz
tar -xvf osu-micro-benchmarks-7.3.tar.gz osu-micro-benchmarks-7.3/python/
```

Then submit one or more of the SLURM batch scripts.

The Jupyter notebook `./lumi_mpi4py_osu_results.ipynb` provides a presentation of the results from one such run of the mpi4py OSU benchmarks on LUMI. The `py312_jupyter.yml` conda environment may be used to run the notebook. It was created from the package specification "jupyterlab pandas python=3.12 seaborn".

### Notes about the test setup

- Not all test methods use the same versions of MPICH, mpi4py, and numpy. This may influence the results. Ideally, one should benchmark the test methods using the same versions, but that is unfortunately not practically possible at this point.
- It is still not clear what the "correct" way to bind mount the host MPICH in the container is. Here we use the `LD_LIBRARY_PATH` and singularity binds given in the `lumi-singularity-bindings.sh` file. They seem to work, but adjustments may be needed...

## Various link providing more background info

- OSU Python benchmarks
  - http://nowlab.cse.ohio-state.edu/static/media/talks/slide/Alnaasan-OMB-Py-osu-booth.pdf
- Singularity containers and MPI
  - https://apptainer.org/docs/user/latest/mpi.html#apptainer-and-mpi-applications
  - https://carpentries-incubator.github.io/singularity-introduction/08-singularity-mpi/index.html
- mpi4py singularity containers
  - https://pawseysc.github.io/containers-astro-python-workshop/3.hpc/index.html
- MPICH
  - https://github.com/pmodels/mpich/discussions/5957
- LUMI container documentation
  - https://docs.lumi-supercomputer.eu/software/containers/singularity/
  - https://docs.lumi-supercomputer.eu/runjobs/scheduled-jobs/container-jobs/
- Cray MPICH ABI compatibility
  - https://www.mpich.org/abi/
  - https://cpe.ext.hpe.com/docs/mpt/mpich/intro_mpi.html#using-mpich-abi-compatibility
  - https://github.com/PE-Cray/whitepapers/raw/master/mpt/ABI_Compat_white_paper_ex.doc
  - https://github.com/pmodels/mpich/blob/main/doc/wiki/testing/MPICH_ABI_Tests.md
- RPATH and LD_LIBRARY_PATH (in connection with conda packages)
  - https://www.hpc.dtu.dk/?page_id=1180
  - https://en.wikipedia.org/wiki/Rpath
  - https://bnikolic.co.uk/blog/linux-ld-debug.html
  - https://stackoverflow.com/questions/47682750/why-changing-ld-library-path-has-no-effect-in-ubuntu
  - https://stackoverflow.com/questions/13769141/can-i-change-rpath-in-an-already-compiled-binary
  - https://github.com/conda/conda-build/blob/main/docs/source/resources/compiler-tools.rst#anaconda-compilers-implicitly-add-rpath-pointing-to-the-conda-environment
  - https://github.com/conda/conda-build/blob/main/docs/source/resources/use-shared-libraries.rst
