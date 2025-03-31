"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import sys

__version__ = "2025.03.0"
_minimum_dependency_version = {
    # Versions must be specified as a (major, minor, patchlevel) tuple of
    # integers
    "python": (3, 9, 0),
    "apptainer": (1, 0, 0),
    "singularity": (3, 7, 4),
    "singularity-ce": (3, 9, 2),
}

# Error early on too old Python version
if sys.version_info < _minimum_dependency_version["python"]:
    # Note that this is using percent formatting on purpose, so this
    # file can be executed by Python versions older than the minimum
    # for Cotainr in general; this includes being able to run with
    # Python 2.7!
    sys.exit(
        (  # noqa: UP031
            "\x1b[38;5;160m"  # start of red colored text
            "Cotainr requires Python>=%s\n"
            "You are running Python==%s\n"
            "from '%s'\n"
            "ABORTING!"
            "\x1b[0m"  # end of red colored text
        )
        % (
            ".".join(map(str, _minimum_dependency_version["python"])),
            sys.version,
            sys.executable,
        )
    )
