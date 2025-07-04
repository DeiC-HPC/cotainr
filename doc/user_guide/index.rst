.. _section_user_guide:

User Guide
==========

The User Guide covers a basic introduction to `cotainr` (this page) along with separate in-depth pages describing :ref:`typical uses of cotainr <use_cases>`. See the :ref:`Getting Started <section_getting_started>` guide for information about installing `cotainr`.

.. _why_cotainr:

Why would I want to use `cotainr`?
----------------------------------
The two main reasons to use `cotainr` are:

1. It runs entirely in :ref:`user space <cotainr_technical_motivation>`, i.e. you don't need root/sudo privileges (or `fake them <https://apptainer.org/docs/user/1.0/fakeroot.html>`_) to use `cotainr`.
2. It makes it a lot easier to build `SingularityCE`_/`Apptainer`_ containers for certain :ref:`HPC use cases <use_cases>`.

In order to achieve this, the scope of `cotainr` is deliberately limited - focus is on making it easy to build reasonably performant containers for :ref:`common HPC use cases <use_cases>`. If you need a general purpose solution for building containers that achieve the absolute maximum performance, you should stick with `Apptainer`_/`SingularityCE`_ instead of `cotainr`.

.. _cotainr_dependencies:

Dependencies
------------
Since `cotainr` is a tool, written in `Python`_, for building `SingularityCE`_/`Apptainer`_ containers, you need the following to be able to use `cotainr`:

..
  MARK_PYTHON_VERSION: Update this to reflect the minimum supported Python version.
  MARK_APPTAINER_VERSION: Update this to reflect the minimum supported SingularityCE/Apptainer version.

- A Linux OS [1]_
- `Python`_ >=3.9 [2]_
- `SingularityCE`_ >=3.9.2 or `Apptainer`_ >=1.3.4 [3]_
- A CPU architecture that is either `x86_64 <https://en.wikipedia.org/wiki/X86-64>`_ or `ARM64/AArch64 <https://en.wikipedia.org/wiki/AArch64>`_

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

    $ cotainr build my_container.sif --base-image=docker://ubuntu:24.04

which would create the container `my_container.sif` based on the official `Ubuntu 24.04 DockerHub image <https://hub.docker.com/_/ubuntu>`_.
The same could be achieved with:

.. code-block:: console

    $ cotainr build my_container.sif --system some-system

if the system :code:`some-system` was defined to use the same docker image.
These predefined systems can be listed with the :code:`cotainr info` command, and are defined in the :ref:`system.json <systems>` file which is typically managed by system administrators who install `cotainr` on their HPC system.

Not specifying any further options to :code:`cotainr build` than above, provides no more than what can be achieved with a :code:`singularity pull`.
In order to add software and files to the container, you need to use the options available with :code:`cotainr build`.
To list all options, run:

.. code-block:: console

    $ cotainr build --help

Also, take a look at the :ref:`list of use cases <use_cases>` for further inspiration to building containers using `cotainr`.

.. _hpc_systems_information:

System information
~~~~~~~~~~~~~~~~~~
To make sure that everything is in your environment for using `cotainr`, you can run the :code:`cotainr info` subcommand.
This will provide you information about the system and also providing you with names of predefined systems.

..
  MARK_PYTHON_VERSION: Update this to reflect the minimum supported Python version.
  MARK_APPTAINER_VERSION: Update this to reflect the minimum supported SingularityCE version.

.. code-block:: console

    $ cotainr info
    Dependency report
    -------------------------------------------------------------------------------
        - Running python 3.11.7 >= 3.9.0, OK
        - Found singularity-ce 4.1.3-150500.10.7 >= 3.9.2, OK

    System info
    -------------------------------------------------------------------------------
    Available system configurations:
        - lumi-g
        - lumi-c


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
.. _SingularityCE: https://sylabs.io/singularity/
.. _test matrix.json file: https://github.com/DeiC-HPC/cotainr/blob/main/.github/workflows/matrix.json

.. rubric:: Footnotes
.. [1] Since `SingularityCE`_/`Apptainer`_ `only runs on Linux <https://apptainer.org/docs/admin/main/installation.html#installation-on-linux>`_
.. [2] See the `test matrix.json file`_ for the exact `Python`_ versions that we actively test with `cotainr`.
.. [3] See the `test matrix.json file`_ for the exact `SingularityCE`_/`Apptainer`_ versions that we actively test with `cotainr`.
