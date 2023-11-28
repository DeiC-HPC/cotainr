.. _cotainr_technical_motivation:

Technical motivation
====================
`Singularity`_/`Apptainer`_ are High Performance Computing (HPC) user space container technologies, i.e. you can run your container as a normal user without root privileges. However, `you still need root privileges to be able to build containers from singularity definition files <https://github.com/apptainer/singularity/issues/5941#issuecomment-821409323>`_ - or `fake such privileges <https://apptainer.org/docs/user/1.0/fakeroot.html>`_. Unfortunately, on some HPC systems such fakeroot functionality is disabled due to security concerns, thus, making it impossible to build containers from singularity definitions files *on* the HPC system. This is undesirable since not all users are able to build their containers elsewhere.

Despite not being able to build containers from definition files without root privileges, you are able to convert between various container formats as an unprivileged user, e.g. convert a docker container to a singularity container. Among the possible container conversions are conversions to/from the `sandbox format <http://apptainer.org/docs/user/main/build_a_container.html#creating-writable-sandbox-directories>`_. The `sandbox format` technically lets you build containers in user space by:

1. Converting a base image to a sandbox directory.
2. Installing your software in the sandbox directory (as a normal user).
3. Converting the sandbox directory to a singularity SIF file.

However, this comes at the cost of both a much more manual and tedious build procedure as well as a lack of built-in reproducibility since no record of the changes to the sandbox is automatically kept. Thus, the convenience and reproducibility of the singularity definition file is lost.

`cotainr` restores this convenience and reproducibility by providing an easy way to automate the above sandbox container build workflow for certain :ref:`use cases <use_cases>`.


Container sandbox design
------------------------
When using :code:`cotainr build`, containers are built using a sandbox, for now a `Singularity`_/`Apptainer`_ sandbox, i.e. a temporary folder is created containing the base container content. The sandbox is created using the `--fix-perms` option to ensure owner rwX permissions for all files in the container. The requested software and its configuration, e.g. a :ref:`conda environment <conda_environments>` is then packed into this sandbox using `Singularity`_/`Apptainer`_  as a chroot bootstrapper. Once everything is in place in the sandbox, it is converted to a SIF image file. Finally, everything is cleaned-up and the sandbox directory is removed.


`cotainr` specific implementation details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The container sandbox is implemented in the :mod:`cotainr.container` module, specifically in the :class:`cotainr.container.SingularitySandbox` class which is used as a `context manager <https://docs.python.org/3/reference/datamodel.html#context-managers>`_. Running a command in the sandbox context is wrapped as a :mod:`subprocess` call to :code:`singularity exec`.

The packing of software into the container sandbox is implemented in the :mod:`cotainr.pack` module. This packing functionality interacts with a container sandbox from :mod:`cotainr.container`.


Limitations
-----------
Building containers in user space comes with the following limitations:

- We are unable to correctly handle file permissions that should be set with root privileges. We are forcing owner rwX permission on all files using the `--fix-perms` option to `singularity build`, `as is also implied in the most basic Apptainer fakeroot builds <https://apptainer.org/docs/user/latest/fakeroot.html#build>`_.
- You can only install software in user space in the container, i.e. there is no :code:`sudo apt install` or the like.


.. _Apptainer: https://apptainer.org/
.. _Singularity: https://sylabs.io/singularity/
