.. _systems:

Predefining systems
===================

To make `cotainr` easier to use, you can predefine systems.
This currently means specifying a base image for a part of your HPC system.
This can be done make a json file called `systems.json` in the project root folder.

Why should I do this?
---------------------

If it is not trivial for the users to get MPI or GPU access working in containers on your system, then a predefined base image with support for this will help your users tremendously.


File format
-----------

The file format is relatively simple. For each system you give them a name and then add a base image for them.
The base image path can be one of the support targets for `apptainer build <https://apptainer.org/docs/user/latest/build_a_container.html#overview>`_.

.. code-block:: json

    {
      "system-name": {
        "base-image": "docker://ubuntu:22.04"
      },
      "another-system-name": {
        "base-image": "/path/to/file/on/system"
      }
    }