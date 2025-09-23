r"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements utility functions.

Functions
---------
answer_is_yes()
    Ask user for confirmation ("yes") of `input_text`.
get_systems()
    Get a dictionary of predefined systems, defined in systems.json
stream_subprocess(\*, args, \*\*kwargs)
    Run a the command described by `args` while streaming stdout and stderr.

Attributes
----------
systems_file
    The path to the systems.json file (if present).
"""

import json
import logging
from pathlib import Path, PosixPath
import sys

logger = logging.getLogger(__name__)
systems_file = (Path(__file__) / "../../systems.json").resolve()


class cpath:
    """
    Dataclass to store the path to a folder or file inside a container.

    Parameters
    ----------
    path : PosixPath or str
        The absolute path to a file or folder in the reference of the container file system.
    container_directory : PosixPath or str
        The absolute path to the container in the reference of the host file system.
    """

    def __init__(
        self, path: PosixPath | str = "/", container_directory: PosixPath | str = None
    ):
        self._container_directory = container_directory
        self.path = Path(path)

    @property
    def container_directory(self):
        """Wrapper to expose the optional directory on the host filesystem."""
        if self._container_directory is None:
            raise AttributeError(
                f"{self.path} is only defined in the context of the container:\n"
            )
        return Path(self._container_directory)

    @property
    def host_path(self):
        """Get the host filesystem path to a file inside the container."""
        if str(self.path)[0] == "/":
            path = Path(str(self.path)[1:])
        else:
            path = self.path
        return self.container_directory / path

    @classmethod
    def from_hostpath(cls, host_path, container_directory):
        """Alternative Constructor using from a host filesystem path."""
        if isinstance(host_path, str):
            host_path = Path(host_path)
        if isinstance(container_directory, str):
            container_directory = Path(container_directory)
        path = host_path.relative_to(container_directory)  # Errors if not relative
        path = Path("/" + str(path))
        return cls(path=path, container_directory=container_directory)

    def __truediv__(self, other):
        """Overwrite Python builtin to mirror pathlib.Path syntax."""
        if isinstance(other, cpath):
            assert self._container_directory == other._container_directory
        else:
            other = cpath(path=other)
        return cpath(
            path=self.path / other.path, container_directory=self._container_directory
        )


def answer_is_yes(input_text, max_attempts=1000):
    """
    Ask user for confirmation ("yes") of `input_text`.

    Parameters
    ----------
    input_text : str
        The prompt to be printed for verification by the user.
    max_attempts : int, optional
        The maximum number of attempts to get a valid answer from the user before giving up. The default is 1000.

    Returns
    -------
    answer_is_yes : bool
        The indicator of whether or not the answer is yes.
    """
    input_text = input_text.replace(
        # remove prompt for pressing enter (as we have already done this...)
        "Please, press ENTER to continue\n>>> ",
        "\n",
    )
    # Remove "[yes|no]"" and ">>>" from license text as answer_is_yes
    # adds them as part of the input handling
    input_text = input_text.replace(" [yes|no]\n>>> ", "")
    answer_prompt = input_text + " [yes/no]\n>>> "
    for _ in range(max_attempts):
        answer = input(answer_prompt)
        if answer.lower() == "yes":
            return True
        elif answer.lower() == "no":
            return False
        else:
            answer_prompt = f'You answered "{answer}". Please answer yes or no.\n>>> '
    else:
        logger.error(
            'You provided an invalid answer %d times in a row. Now assuming you meant "no".',
            max_attempts,
        )
        return False


def get_systems():
    """
    Get a dictionary of predefined systems, defined in the systems.json file.

    Returns
    -------
    systems : Dict
        A dictionary of predefined systems

    Raises
    ------
    :class:`NameError`
        If some required arguments are missing in the systems.json file.
    """
    if systems_file.is_file():
        systems = json.loads(systems_file.read_text())
        for system in systems:
            if "base-image" not in systems[system]:
                raise NameError(
                    f"Error in systems.json: {system} missing argument base-image"
                )
        return systems
    else:
        return {}


def _flush_stdin_buffer():
    """
    Discard queued data on stdin file descriptor.

    TCIOFLUSH selects both the input queue and output queue to be discarded.

    https://stackoverflow.com/questions/2520893/how-to-flush-the-input-stream
    """
    from io import UnsupportedOperation

    try:
        sys.stdin.fileno()
    except UnsupportedOperation:
        # stdin is a pseudofile (e.g. Pytest without --no-capture)
        return

    # Python Standard library, Linux/Unix/OSX
    from termios import TCIOFLUSH, tcflush

    tcflush(sys.stdin, TCIOFLUSH)
