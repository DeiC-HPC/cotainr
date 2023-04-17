"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import platform
import sys

__version__ = "2023.02.0"
_minimum_dependency_version = {
    # Versions must be specified as a (major, minor, patchlevel) tuple of
    # integers
    "python": (3, 8, 0),
    "apptainer": (1, 0, 0),
    "singularity": (3, 7, 4),
}

# Error early on too old Python version
_py_ver = platform.python_version_tuple()
if tuple(map(int, _py_ver)) < (3, 8, 0):
    sys.exit(
        (
            "\033[91mCotainr requires Python>=3.8, you are running Python==%s from %s, "
            "ABORTING!\033[0m"
        )
        % (".".join(_py_ver), sys.executable)
    )
