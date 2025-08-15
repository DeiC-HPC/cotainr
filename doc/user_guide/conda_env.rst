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

A container based on the official `Ubuntu 24.04 DockerHub image <https://hub.docker.com/_/ubuntu>`_, containing this conda environment, may be built using:

.. code-block:: console

    $ cotainr build my_conda_env_container.sif --base-image=docker://ubuntu:24.04 --conda-env=my_conda_env.yml

The conda environment is automatically activated when the container is run, allowing for directly using the Python and NumPy versions installed in the conda environment, e.g.

.. code-block:: console

    $ singularity exec my_conda_env_container.sif python3 --version
    Python 3.11.0
    $ singularity exec my_conda_env_container.sif python3 -c "import numpy; print(numpy.__version__)"
    1.23.5

.. admonition:: You must accept the Miniforge license to add a conda environment
  :class: note

  Bootstrapping of the conda environment in the container is done using `Miniforge <https://github.com/conda-forge/miniforge>`_. As part of the bootstrap process, you must accept the `Miniforge license terms <https://github.com/conda-forge/miniforge/blob/main/LICENSE>`_. This can be done either by accepting them during the container build process, or by specifying the :code:`--accept-licenses` option when invoking :code:`cotainr build`.

.. admonition:: Iterate on the conda environment before building the container
  :class: tip

  If you are unsure about what needs to go into your `my_conda_env.yml` file for `conda` to correctly resolve your environment, you may want to iterate on the content of the `my_conda_env.yml` file by updating it and using :code:`conda env create --file my_conda_env.yml` to test that it resolves and installs correctly outside of the container. Only once it installs correctly, should you proceed to building the container with :code:`cotainr build`. That way you can potentially save a lot of time by not having to rebuild the container multiple times while iterating on your conda environment.

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


Editable Pip Packages from Git Repositories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In addition to installing pip packages from private repositories using SSH, as described below, you can also install packages directly from a Git repository using HTTPS. This is useful for including the latest development version of a package or a specific branch in your Conda environment.

To include an editable package from a Git repository using HTTPS, modify your `my_conda_env.yml` file as follows:

.. code-block:: yaml
    :caption: my_conda_env.yml

    channels:
      - conda-forge
    dependencies:
      - python=3.11.0
      - git
      - pip
      - pip:
        - "--editable=git+https://github.com/foo/bar.git@develop#egg=bar"

In this example:

- `git+https://github.com/foo/bar.git`: Specifies the Git repository URL from which the package should be installed.
- `@develop`: Indicates that the `develop` branch should be used. Replace `develop` with the desired branch name if different.
- `#egg=bar`: Specifies the package name, which is necessary for pip to correctly identify and install the package.

This approach allows you to work with the latest changes in a specific branch of a repository, ensuring that your environment is up-to-date with the latest development efforts.

By using HTTPS, you avoid the need for SSH keys, simplifying the setup process, especially in environments where SSH access is restricted or not available.


Pip packages from private repositories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Pip packages from a private GitHub repository are accessible using an ssh key. You can use this option by enabling `ssh-agent forwarding to GitHub <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/using-ssh-agent-forwarding>`_ on the host machine on which `cotainr` is used.

For example, with `my_conda_env.yml` containing the following:

.. code-block:: yaml
    :caption: my_conda_env.yml

    channels:
      - conda-forge
    dependencies:
      - python=3.11.0
      - git
      - openssh
      - pip
      - pip:
        - "--editable=git+ssh://git@github.com/foo/bar.git@SOMEHASHCODE#egg=baz"

where :code:`github.com:foo/bar.git` is a private repository.

The need for using `ssh-agent` is fundamentally `an apptainer limitation/feature <https://stackoverflow.com/questions/65252415/use-ssh-key-of-host-during-singularity-apptainer-build>`_ and not related to `cotainr` per se.
For this to work, the directory pointed to on the host by the :code:`SSH_AUTH_SOCK` environment variable must be bound to the container. If :code:`echo $SSH_AUTH_SOCK` already points to one of the directories bound by default, e.g. :code:`/tmp`, everything should work. Otherwise, another solution must be found, as `cotainr` does not expose directory binding from `apptainer`.
