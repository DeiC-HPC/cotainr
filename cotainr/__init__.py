"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

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
if sys.version_info < _minimum_dependency_version["python"]:
    sys.exit(
        (
            "\033[91m"  # start of red colored text
            "Cotainr requires Python>=3.8\n"
            "You are running Python=='%s' from '%s'\n"
            "ABORTING!"
            "\033[0m"  # end of red colored text
        )
        % (sys.version, sys.executable)
    )
