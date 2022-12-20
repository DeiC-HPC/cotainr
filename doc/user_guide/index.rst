.. _section_user_guide:

User Guide
==========

The User Guide covers a basic introduction to `cotainr` (this page) along with separate in-depth pages describing :ref:`typical uses of cotainr <use_cases>`. See the :ref:`Getting Started <section_getting_started>` guide for information about installing `cotainr`.

.. _why_cotainr:

Why would I want to use `cotainr`?
----------------------------------
The two main reasons to use `cotainr` are:

1. It runs entirely in :ref:`user space <cotainr_technical_motivation>`, i.e. you don't need root/sudo priviledges (or `fake them <https://apptainer.org/docs/user/1.0/fakeroot.html>`_) to use `cotainr`.
2. It makes it a lot easier to build `Singularity`_/`Apptainer`_ containers for certain :ref:`HPC use cases <use_cases>`.

In order to achieve this, the scope of `cotainr` is deliberately limited - focus is on making it easy to build reasonably performant containers for :ref:`common HPC use cases <use_cases>`. If you need a general purpose solution for building containers that achieve the absolute maximum performance, you should stick with `Apptainer`_/`Singularity`_ instead of `cotainr`.

.. _cotainr_dependencies:

Dependencies
------------
Since `cotainr` is a tool, written in `Python`_, for building `Singularity`_/`Apptainer`_ containers, you need the following to be able to use `cotainr`:

- A Linux OS (since `Singularity`_/`Apptainer`_ `only runs on Linux <https://apptainer.org/docs/admin/main/installation.html#installation-on-linux>`_)
- `Python`_ >=3.8
- `Singularity`_ >=3.7.4 or `Apptainer`_ >=1.0.0

Additionally, some features provided by `cotainr` may impose requirements on the base images you use when building containers, e.g. when including a :ref:`conda environment <conda_environments>` the base container must have `bash <https://www.gnu.org/software/bash/>`_ installed in it.

.. _command_line_interface:

Command line interface
----------------------
The primary way to use `cotainr` is via its command line interface. The `cotainr` command provides a :code:`--help` option that may be used to display all its options:

.. code-block:: console

    $ cotainr --help


Building a container
~~~~~~~~~~~~~~~~~~~~
Containers are built using the :code:`cotainr build` subcommand, e.g.

.. code-block:: console

    $ cotainr build my_container.sif --base-image=docker://ubuntu:22.04

which would create the container `my_container.sif` based on the official `Ubuntu 22.04 DockerHub image <https://hub.docker.com/_/ubuntu>`_. Not specifying any further options to :code:`cotainr build` than above, provides no more than what can be achieved with a :code:`singularity pull`. In order to add software and files to the container, you need to use the options available with :code:`cotainr build`. To list all options, run:

.. code-block:: console

    $ cotainr build --help

Also, take a look at the :ref:`list of use cases <use_cases>` for further inspiration to building containers using `cotainr`.

.. _hpc_systems_information:

TODO: Decsribe the idea in the :code:`--system` flag.


Python interface
~~~~~~~~~~~~~~~~
Power users may consider using the :ref:`cotainr Python API <section_api_reference>` as an alternative to the command line interface.


.. _use_cases:

Use cases
---------
Typical use cases, that `cotainr` makes very easy to handle, include:

- :ref:`Creating a container based on a Conda environment <conda_environments>`

..
    Toc for the use case pages
.. toctree::
    :maxdepth: 1
    :hidden:

    conda_env


Examples
--------
Further examples of using `cotainr` are included with the source code, https://github.com/DeiC-HPC/cotainr/tree/main/examples:

- `Building a ROCm compatible PyTorch container for use on LUMI <https://github.com/DeiC-HPC/cotainr/tree/main/examples/LUMI/conda_pytorch_rocm>`_


.. _Apptainer: https://apptainer.org/
.. _Python: https://www.python.org/
.. _Singularity: https://sylabs.io/singularity/