.. _section_getting_started:

Getting Started
===============

`cotainr` makes it easy to build `Singularity`_/`Apptainer`_ containers for certain :ref:`use cases <use_cases>`. If this is your first time learning about `cotainr`, we encourage you to read the :ref:`motivation for using cotainr <why_cotainr>`.

In order to get started using `cotainr`, you need to download and install the `cotainr` source code. Alternative, you may be in luck that you are using an HPC system on which `cotainr` is already installed.

.. grid:: 1
    :gutter: 4

    .. grid-item-card:: Getting the `cotainr` source code
        :class-card: sd-rounded-0 sd-shadow-sm

        All releases of `cotainr` are available on GitHub: https://github.com/DeiC-HPC/cotainr/releases

        .. dropdown:: Installation instructions
            :animate: fade-in
            :color: secondary

            `cotainr` only runs on Linux and requires that `Python`_ >=3.8 as well as `Singularity`_ >=3.7.4 [#]_ or `Apptainer`_ >=1.0.0 is installed on the system. More details about dependencies may be found in the :ref:`User Guide <cotainr_dependencies>`.

            To install `cotainr`, download and unpack the source code. Then add the :code:`cotainr/bin` directory to your :code:`PATH` to get access to the :ref:`cotainr command line interface <command_line_interface>`.

    .. grid-item-card:: Using `cotainr` on HPC systems where it is already installed

        On some HPC systems, `cotainr` is already installed. If your HPC system of choice is mentioned in the instructions list below, you may follow those instructions to get started using `cotainr` on that system.

        .. dropdown:: HPC systems instructions
            :animate: fade-in
            :color: secondary

            .. tab-set::

                .. tab-item:: LUMI

                    `cotainr` may be loaded as a module from the LUMI software stack. It includes :ref:`system information <hpc_systems_information>`.

                    For instance, building a container for LUMI-G:

                    .. code-block:: console

                        $ module load LUMI
                        $ module load cotainr
                        $ cotainr build my_container.sif --system=lumi-g <...>

                    More details may be found in the :ref:`section_user_guide`. For details about LUMI, see the `LUMI documentation <https://docs.lumi-supercomputer.eu/>`_.

.. _Apptainer: https://apptainer.org/
.. _Python: https://www.python.org/
.. _Singularity: https://sylabs.io/singularity/

.. rubric:: Footnotes
.. [#] As of version 3.8.0, Sylabs have changed the name of their version to SingularityCE. However, we only officially support their version from 3.9.1.