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
answer_yes
    Pass text to the terminal and verify that the answer is yes

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


def stream_subprocess(*, args, log_dispatcher=None, **kwargs):
    """
    Run a the command described by `args` while streaming stdout and stderr.

    The command described by `args` is run in a subprocess with that
    subprocess' stdout and stderr streamed to the main process. Each line in
    the subprocess' output is streamed separately to the main process. Extra
    `kwargs` are passed to `Popen` when opening the subprocess.

    Parameters
    ----------
    args : list or str
        Program arguments. See the docstring for :class:`subprocess.Popen` for
        details.
    log_dispatcher : :class:`~cotainr.tracing.LogDispatcher`, optional
        The log dispatcher which subprocess stdout/stderr messages are
        forwarded to (the default is None which implies that subprocess
        messages are forwarded directly to stdout/stderr).

    Returns
    -------
    completed_process : :class:`subprocess.CompletedProcess`
        Information about the completed subprocess.

    Raises
    ------
    :class:`subprocess.CalledProcessError`
        If the subprocess returned a non-zero status code.

    Notes
    -----
    The way we handle stdout and stderr messages in separate threads introduces
    a race condition in cases where subprocesses write to stdout and stderr at
    the same time. All messages are always guaranteed to be streamed to the
    console, but they might arrive in the wrong order. We accept this "feature"
    as is.
    """
    with subprocess.Popen(
        args,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        **kwargs,
    ) as process:
        with ThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix=f"cotainr_stream_subprocess_thread_for_{args}",
        ) as executor:
            # (Attempt to) pass the process stdout and stderr to the terminal in real
            # time while also storing it for later inspection.
            stdout_future = executor.submit(
                _print_and_capture_stream,
                stream_handle=process.stdout,
                print_dispatch=(
                    log_dispatcher.log_to_stdout
                    if log_dispatcher is not None
                    else functools.partial(print, end="", file=sys.stdout)
                ),
            )
            stderr_future = executor.submit(
                _print_and_capture_stream,
                stream_handle=process.stderr,
                print_dispatch=(
                    log_dispatcher.log_to_stderr
                    if log_dispatcher is not None
                    else functools.partial(print, end="", file=sys.stderr)
                ),
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
    stream_handle : :py:class:`io.TextIOWrapper`
        The text stream to print and capture.
    print_dispatch : Callable
        The callable to use for printing.

    Returns
    -------
    captured_stream : list of str
        The lines captured from the stream.
    """
    captured_stream = []
    for line in stream_handle:
        print_dispatch(line)
        captured_stream.append(line)

    return captured_stream


def answer_is_yes(input_text):
    """
    Print text and compare the input given to "yes"

    Parameters
    ----------
    input_text : str
        a string to be printed for verification by the user

    Returns
    -------
    answer_is_yes : boolean
        A boolean indicating whether or not the answer is yes
    """
    answer_prompt = input_text
    while True:
        answer = input(answer_prompt).lower()
        answer_yes = answer == "yes"
        answer_no = answer.startswith("n") or answer == ""
        if answer_yes:
            return True
        if answer_no:
            return False
        answer_prompt = "Did not understand your input. Please answer yes/[N]o\n"
