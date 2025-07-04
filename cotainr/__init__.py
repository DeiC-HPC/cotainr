"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import sys

from ._version import __version__

__all__ = ["__version__"]

_minimum_dependency_version = {
    # Versions must be specified as a (major, minor, patchlevel) tuple of
    # integers
    "python": (
        3,
        9,
        0,
    ),  # MARK_PYTHON_VERSION: Update this to reflect the minimum supported Python version.
    "apptainer": (
        1,
        3,
        4,
    ),  # MARK_APPTAINER_VERSION: Update this to reflect the minimum supported Apptainer version.
    "singularity-ce": (
        3,
        9,
        2,
    ),  # MARK_APPTAINER_VERSION: Update this to reflect the minimum supported SingularityCE version.
}

# Error early on too old Python version
if sys.version_info < _minimum_dependency_version["python"]:  # pragma: no cover
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
