.. _section_user_guide:

User Guide
==========
The primary way to use `cotainr` is via its command line interface. The `cotainr` command line provides a :code:`--help` option that may be used to display all its options:

.. code-block:: console

    $ cotainr --help


Building a container
--------------------
Containers are built using the :code:`cotainr build` subcommand, e.g.

.. code-block:: console

    $ cotainr build my_container.sif --base-image=docker://ubuntu:22.04

which would create the container `my_container.sif` based on the official `Ubuntu 22.04 DockerHub image <https://hub.docker.com/_/ubuntu>`_. Not specifying any further options to :code:`cotainr build` than above, provides no more than what can be achieved with a :code:`singularity pull`. In order to add software and files to the container, you need to use the options available with :code:`cotainr build`. To list all options, run:

.. code-block:: console

    $ cotainr build --help

Also, take a look at the :ref:`list of use cases <use_cases>` for further inspiration to building containers using `cotainr`.

.. _use_cases:

Use cases
---------
Typical use cases of `cotainr` include:

.. toctree::
    :maxdepth: 1

    conda_env


Examples
--------
Further examples of using `cotainr` are included with the source code: https://github.com/DeiC-HPC/cotainr/tree/main/examples


Python interface
----------------
Power users may consider using the :ref:`cotainr Python API <section_api_reference>` as an alternative to the command line interface.
