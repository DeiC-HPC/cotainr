.. _section_getting_started:

Getting Started
===============

`cotainr` makes it easy to build `Singularity`_/`Apptainer`_ containers for certain :ref:`use cases <use_cases>`. If this is your first time learning about `cotainr`, we encourage you to read the :ref:`motivation for using cotainr <why_cotainr>`.

In order to get started using `cotainr`, first be sure your system have the necessary :ref:`Dependencies <cotainr_dependencies>` installed, then you can install `cotainr` directly using pip.

.. code-block:: console

    $ pip install cotainr

Alternatively, If you are using an HPC system, you may be in luck and find `cotainr` is already installed and refer to the following instructions. Please note that cotainr only supports x86_64 and ARM64/AArch64 architectures.

.. grid:: 1
    :gutter: 4

    .. grid-item-card:: Using `cotainr` on HPC systems where it is already installed

        On some HPC systems, `cotainr` is already installed. If your HPC system of choice is mentioned in the instructions list below, you may follow those instructions to get started using `cotainr` on that system.

        .. dropdown:: HPC systems instructions
            :animate: fade-in
            :color: secondary

            .. tab-set::

                .. tab-item:: LUMI

                    `cotainr` may be loaded as a module from the `CrayEnv software stack <https://docs.lumi-supercomputer.eu/runjobs/lumi_env/softwarestacks/#crayenv>`_. It includes :ref:`system information <hpc_systems_information>`.

                    For instance, building a container for LUMI-G:

                    .. code-block:: console

                        $ module load CrayEnv
                        $ module load cotainr
                        $ cotainr build my_container.sif --system=lumi-g <...>

                    More details may be found in the :ref:`section_user_guide`. For details about LUMI, see the `LUMI documentation <https://docs.lumi-supercomputer.eu/>`_.

.. _Apptainer: https://apptainer.org/
.. _Python: https://www.python.org/
.. _Singularity: https://sylabs.io/singularity/
