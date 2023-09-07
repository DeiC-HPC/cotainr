.. _conda_environments:

Conda Environments
==================
Adding a `conda environment <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_ to a container may be easily done using `cotainr`.

.. admonition:: Make sure you have the rights to use the packages in your conda environment
    :class: warning

    When adding a conda environment, it is the responsibility of the user of `cotainr` to make sure they have the necessary rights to use the conda channels/repositories and packages specified in the conda environment, e.g. if `using the default Anaconda repositories <https://www.anaconda.com/blog/anaconda-commercial-edition-faq>`_.

As an example, consider the following `conda environment file <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment>`_, `my_conda_env.yml`:

.. admonition:: Base image requirement
    :class: sidebar note

    In order to include a conda environment in your container, you must use a base image in which `bash <https://www.gnu.org/software/bash/>`_ is installed.

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

    $ singularity exec my_conda_env_container.sif python3 --version
    Python 3.11.0
    $ singularity exec my_conda_env_container.sif python3 -c "import numpy; print(numpy.__version__)"
    1.23.5

.. admonition:: You must accept the Miniforge license to add a conda environment
  :class: note

  Bootstrapping of the conda environment in the container is done using `Miniforge <https://github.com/conda-forge/miniforge>`_. As part of the bootstrap process, you must accept the `Miniforge license terms <https://github.com/conda-forge/miniforge/blob/main/LICENSE>`_. This can be done either by accepting them during the container build process, or by specifying the :code:`--accept-licenses` option when invoking :code:`cotainr build`.


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
      - pip
      - pip:
        - scipy==1.9.3

allows for installing SciPy via pip.
