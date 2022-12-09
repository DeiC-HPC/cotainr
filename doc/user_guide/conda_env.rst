.. _conda_environments:

Conda Environments
==================
Adding a `conda environment <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_ to a container may be easily done using `cotainr`.

As an example, consider the following `conda environment file <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment>`_, `my_conda_env.yml`:

.. code-block:: yaml
    :caption: my_conda_env.yml
    
    channels:
      - conda-forge
    dependencies:
      - python=3.11.0
      - numpy=1.23.5

A container based on the official `Ubuntu 22.04 DockerHub image <https://hub.docker.com/_/ubuntu>`_, containing this conda environment, may be built using:

.. code-block:: console

    $ cotainr build my_conda_env_container.sif --base-image=docker://ubuntu:22.04 --conda-env=my_conda_env.yml

The conda environment is automatically activated when the container is run, allowing for directly using the Python and NumPy versions installed in the conda environment, e.g.

.. code-block:: console

    $ singularity exec my_conda_env_container.sif python --version
    Python 3.11.0
    $ singularity exec my_conda_env_container.sif python -c "import numpy; print(numpy.__version__)"
    1.23.5


Pip packages
------------
`cotainr` does not support creating a container directly from a `pip requirements.txt <https://pip.pypa.io/en/stable/user_guide/#requirements-files>`_ file. However, `pip packages may be included in a conda environment <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#using-pip-in-an-environment>`_, e.g. updating `my_conda_env.yml` to

.. code-block:: yaml
    :caption: my_conda_env.yml
    
    channels:
      - conda-forge
    dependencies:
      - python=3.11.0
      - numpy=1.23.5
      - pip:
        - scipy==1.9.3

allows for installing SciPy via pip.
