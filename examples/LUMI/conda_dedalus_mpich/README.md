# Conda Dedalus MPICH example

This is an example of a container that includes a MPICH compatible [Dedalus](https://dedalus-project.readthedocs.io/) 3.0.0a0 (the beta version of Dedalus v3) Conda environment for use with the CPU nodes on LUMI. It is based on converting the ["Full-stack conda installation" install approach](https://dedalus-project.readthedocs.io/en/latest/pages/installation.html#full-stack-conda-installation-recommended) to a conda environment file.

## Building the container

The closest conda environment yaml file approximation to the conda/pip commands in the ["Full-stack conda installation" install approach](https://dedalus-project.readthedocs.io/en/latest/pages/installation.html#full-stack-conda-installation-recommended) is probably what's shown in `py311_dedalus_basic.yml`. Unfornutately there are a couple of issues with this environment specification:

- It doesn't include all needed dependencies as conda packages. Specifically, it doesn't specify `xarray` and `numexpr` as dependencies which means that they get installed (along with all their dependencies) by pip. In order to have conda resolve all dependencies `xarray` and `numexpr` should be added as conda packages.
- It doesn't pin minimum/maximum versions of dependencies. The [Dedalus setup.py file](https://github.com/DedalusProject/dedalus/blob/acc37823dc0c5886ac027e5978bde76ac08d8376/setup.py#L188) suggests that some dependencies needs to be pinned to minimum/maximum versions.
- It doesn't specify the MPI flavor to use. On LUMI, the MPI flavor must be MPICH. Thus, `mpi=*=mpich` should be added as conda dependency.
- It requires that you set the environment variable `CC=mpicc` during installation of the Dedalus v3 pip package as it needs to compile some parts of Dedalus for the MPI implementation used. This requirement is particularly tricky to implement given how `conda env create` works. If you export `CC=mpicc` before calling `conda env create`, it gets overwritten by the [conda activation scripts for the gcc conda-forge compiler](https://anaconda.org/conda-forge/gcc_linux-64) (which get installed by the c-compiler conda meta package) once the conda dependencies have been installed, just before the pip packages are installed (`conda env create` code path for pip requirements conda env activation: [execute](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda_env/cli/main_create.py#L106) [installer.install](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda_env/cli/main_create.py#L164C28-L164C42) -> [_pip_install_via_requirements](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda_env/installers/pip.py#L78) -> [pip_subprocess](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda_env/installers/pip.py#L56) -> [any_subprocess](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda_env/pip_util.py#L30) -> [wrap_subprocess_call](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda/gateways/subprocess.py#L39) -> [conda activate](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda/utils.py#L473)
). If you add it under `variables` in the conda environment yaml file, it doesn't work either as [these are only added to the environment as the last step](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda_env/cli/main_create.py#L184) - after the pip packages have been installed. However, a possible workaround is to install a conda package which sets `CC=mpicc` in [an environment activate.d script](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#macos-and-linux) ([it seems that the name of the relevant activation script needs to alphabetically sort later than "activate-gcc_linux-64.sh"...](https://github.com/conda/conda/blob/7f54d73f43cdf325fb7e7cac64f6a1de4a44b4d7/conda/activate.py#L759)). An example of such a conda package is the `envvar-cc-mpicc` package which should then be added as a local package dependency. This package is based on the structure proposed in https://stackoverflow.com/a/46833531.

Implementing all of these changes to `py311_dedalus_basic.yml` results in `py311_dedalus.yml`. Note that `file:///mnt` is specified as a channel, which is where the local `envvar-cc-mpicc` conda package should be available (we bind mount this in the cotainr build command below).

On LUMI, the container may be built using:

```bash
module load LUMI
module load cotainr
SINGULARITY_BIND=~/conda_dedalus_mpich/local_conda_channel:/mnt cotainr build lumi_dedalus_demo.sif --system=lumi-c --conda-env py311_dedalus.yml
```

assuming you have copied this "conda_dedalus_mpich" example folder to your home folder on LUMI.

### Creating the local conda channel

The `envvar-cc-mpicc` package must be built from the conda recipe in the "envvar-cc-mpicc" folder and exposed via a conda channel. The result is already added to this repository as the "local_conda_channel" folder which may be used as-is when building the container. For reference, the "local_conda_channel" is created by:

1. Build the `envvar-cc-mpicc` package by activating a conda environment in which the "conda-build" package is installed and run `conda build envvar-cc-mpicc --output-folder=local_conda_channel`.
2. Activate a conda environment in which the "conda-index" package is installed and run `python -m conda_index ./local_conda_channel/`.

## Running the Dedalus examples on LUMI using the built container

Download the `shear_flow.py` example from https://github.com/DedalusProject/dedalus/tree/master/examples/ivp_2d_shear_flow to your "conda_dedalus_mpich" folder on LUMI, e.g. using `wget https://raw.githubusercontent.com/DedalusProject/dedalus/master/examples/ivp_2d_shear_flow/shear_flow.py`. Then update the `--account=project_<your_project_id>` SBATCH directive in the `run_dedalus_shear_flow.sh` SLURM batch, and submit it.

**NOTE: This shear_flow.py run fails due to a h5py/HDF5 error that needs further debugging on its own...**

**WARNING: This Dedalus example has been created to showcase the use of the Dedalus MPICH container built using `cotainr`. They may or may not provide optimal performance on LUMI. Please consult official LUMI channels for guidance on performance optimizing code for LUMI.**
