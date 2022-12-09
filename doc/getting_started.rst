.. _section_getting_started:

Getting Started
===============

|

.. grid:: 1
    :gutter: 4

    .. grid-item-card:: Using `cotainr` on HPC systems

        On some HPC systems, `cotainr` is already installed!

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


    .. grid-item-card:: Getting the `cotainr` source code
        :class-card: sd-rounded-0 sd-shadow-sm

        All releases of `cotainr` are available on GitHub: https://github.com/DeiC-HPC/cotainr/releases

        .. dropdown:: Installation instructions
            :animate: fade-in
            :color: secondary

            Download and unpack the source code. Then add the :code:`cotainr/bin` directory to your :code:`PATH` to get access to the :ref:`cotainr command line interface <command_line_interface>`.
