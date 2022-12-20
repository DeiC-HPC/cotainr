"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

__version__ = "2022.12.0"
_minimum_dependency_version = {
    # Versions must be specified as a (major, minor, patchlevel) tuple of
    # integers
    "python": (3, 8, 0),
    "apptainer": (1, 0, 0),
    "singularity": (3, 7, 4),
}
