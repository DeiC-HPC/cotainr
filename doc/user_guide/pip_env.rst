.. _pip_environments:

Pip Environments
================

`cotainr` can set up a container to include a Python virtualenv, into which packages are installed using `pip <https://pip.pypa.io/en/stable/>`_.
This is done by specifying a `pip requirements.txt file <https://pip.pypa.io/en/stable/user_guide/#requirements-files>`_ when building the container.

When using a requirements file, the base image must contain an usable ``python3`` and ``bash``.

For instance, given a requirements file

.. code-block:: text
    :caption: requirements.txt

    numpy~=2.0

you can build a Python 3.12 container with Numpy 2.x installed with:

.. code-block:: console

    $ cotainr build my_fresh_numpy.sif --base-image=docker://python:3.12-slim --requirements-txt=requirements.txt

The virtualenv (located at ``/opt/venv``) is automatically activated when the container is run, allowing for directly using the packages installed.

.. code-block:: console

    $ singularity exec my_fresh_numpy.sif python3 --version
    Python 3.12.3
    $ singularity exec my_fresh_numpy.sif python3 -c "import numpy; print(numpy.__version__)"
    2.xx
