CC=mpicc overwritten by conda env activation - workaround: install envvar-cc-mpicc package containing activate.d scripts to seet CC=mpicc. This get activated before pip packages are installed when running conda env create which is why it needs to ba conda package. Report this as an issue on conda github issue tracker.

conda build envvar-cc-mpicc --output-folder=local_conda_channel (in env in which conda-build is installed)
python -m conda_index ./local_conda_channel/ (in env in which conda-index is installed)
PIP_LOG=pip.log conda env create -f py311_dedalus.yml

SINGULARITY_BIND=/home/chrso/gits/DeiC/cotainr/examples/LUMI/conda_dedalus_mpich/local_conda_channel:/mnt ../../../bin/cotainr build dedalus_example.sif --base-image=docker://ubuntu:22.04 --conda-env=py311_dedalus.yml -v --accept-licenses

TODO:

- Create full README.md
- Consider only using py310 for env
- Test container using Dedalus examples
- Report CC problem on conda issue tracker


https://dedalus-project.readthedocs.io/en/latest/pages/installation.html#full-stack-conda-installation-recommended
