.. _cotainr_technical_motivation:

Technical motivation
--------------------

TODO: Describe in-detail the technical user space limitations that motivates the use of `cotainr`


Container sandbox design
------------------------

The container is built using a sandbox, for now a Singularity sandbox, i.e. a temporary folder is created containing the container content. Software may then be packed into this sandbox using Singularity as a chroot bootstrapper. Once everything is in place in the sandbox, it may be converted to a SIF image file. The sandbox is removed when the builder exists.


### Implementation of container sandbox

The container sandbox is implemented in the `container.py` module as a context manger. Running a command in the sandbox context is wrapped as a subprocess call to `singularity exec`.

### Implementation of software packing

Functionality that allows for packing software into the container sandbox is implemented in the `pack.py` module. This packing functionality must interact with a container sandbox from `container.py`.


## Limitations

- Since the container is being built entirely in user space, we are unable to correctly handle file permissions that should be set with root privileges.

TODO: everything must be installed in user space