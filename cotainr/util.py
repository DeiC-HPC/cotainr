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
from pathlib import Path
import sys

logger = logging.getLogger(__name__)
systems_file = (Path(__file__) / "../../systems.json").resolve()


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
