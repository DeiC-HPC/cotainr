r"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements utility functions.

Functions
---------
stream_subprocess(\*, args, \*\*kwargs)
    Run a the command described by `args` while streaming stdout and stderr.
get_systems()
    Get a dictionary of predefined systems, defined in systems.json

Attributes
----------
systems_file
    The path to the systems.json file (if present).
"""

from concurrent.futures import ThreadPoolExecutor
import functools
import logging
import json
from pathlib import Path
import subprocess
import sys

logger = logging.getLogger(__name__)
systems_file = (Path(__file__) / "../../systems.json").resolve()


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


def stream_subprocess(*, log_dispatcher=None, args, **kwargs):
    """
    Run a the command described by `args` while streaming stdout and stderr.

    The command described by `args` is run in a subprocess with that
    subprocess' stdout and stderr streamed to the stdout. Extra `kwargs` are
    passed to `Popen` when opening the subprocess.

    Parameters
    ----------
    args : list or str
        Program arguments. See the docstring for :class:`subprocess.Popen` for
        details.
    TODO: Cleanup and document
    TODO: Consider reworking to avoid API break

    Returns
    -------
    completed_process : :class:`subprocess.CompletedProcess`
        Information about the completed subprocess.

    Raises
    ------
    :class:`subprocess.CalledProcessError`
        If the subprocess returned a non-zero status code.
    """
    with subprocess.Popen(
        args,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        **kwargs,
    ) as process:
        with ThreadPoolExecutor(max_workers=2) as executor:
            # (Attempt to) pass the process stdout and stderr to the terminal in real
            # time while also storing it for later inspection.
            stdout_future = executor.submit(
                _print_and_capture_stream,
                stream_handle=process.stdout,
                print_dispatch=log_dispatcher.log_to_stdout
                if log_dispatcher is not None
                else functools.partial(print, end="", file=sys.stdout),
            )
            stderr_future = executor.submit(
                _print_and_capture_stream,
                stream_handle=process.stderr,
                print_dispatch=log_dispatcher.log_to_stderr
                if log_dispatcher is not None
                else functools.partial(print, end="", file=sys.stderr),
            )
            captured_stdout = stdout_future.result()
            captured_stderr = stderr_future.result()

    completed_process = subprocess.CompletedProcess(
        process.args,
        process.returncode,
        stdout="".join(captured_stdout),
        stderr="".join(captured_stderr),
    )

    completed_process.check_returncode()

    return completed_process


def _print_and_capture_stream(*, stream_handle, print_dispatch):
    """
    Print a text stream while also storing it.

    Parameters
    ----------
    stream_handle : io.TextIOWrapper
        The text stream to print and capture.
    print_dispatch : Callable
        The callable to use for printing.
    """
    captured_stream = []
    for line in stream_handle:
        print_dispatch(line)
        captured_stream.append(line)

    return captured_stream
