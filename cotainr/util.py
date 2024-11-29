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
import shlex

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


def run_command_in_sandbox(*, cmd, sandbox_dir, log_dispatcher):
    """
    Run a command in the container sandbox.

    Wraps `singularity exec` of the `cmd` in the container sandbox`
    allowing for running commands inside the container sandbox context,
    e.g. for installing software in the container sandbox.

    Parameters
    ----------
    cmd : str
        The command to run in the container sandbox.
    sandbox_dir : :class:`pathlib.PosixPath`
    log_dispatcher : :class:`~cotainr.tracing.LogDispatcher`
        The log dispatcher to use when running the command.
    verbosity : int

    Returns
    -------
    process : :class:`subprocess.CompletedProcess`
        Information about the process that ran in the container sandbox.

    Notes
    -----
    We pass several flags to the `singularity exec` command to provide
    maximum compatibility with different HPC systems. In particular, we
    use:

    - `--no-home` as trying to mount the home folder on some systems (e.g.
        LUMI) causes problems. Thus, when running a command in the container,
        you cannot reference files in your home directory. Instead you must
        copy all files into the container sandbox and then reference the
        files relative to the container root.
    - `--no-umask` as some systems use a default umask (e.g. 0007 on LUMI)
        that prevents you from accessing any files added to the container as
        a regular user when you run the built container, e.g. such files are
        owned by root:root with 660 permissions for a 0007 umask. Thus, all
        files added to the container by running a command in the container
        will have file permissions 644 (Apptainer/Singularity forces the
        umask to 0022). If you need other file permissions, you must manually
        change them.
    """
    sing_verbosity = to_singularity_verbosity(log_dispatcher.verbosity)
    try:
        process = stream_subprocess(
            args=[
                "singularity",
                sing_verbosity,
                "--nocolor",
                "exec",
                "--writable",
                "--no-home",
                "--no-umask",
                sandbox_dir,
                *shlex.split(cmd),
            ],
            log_dispatcher=log_dispatcher,
        )
    except subprocess.CalledProcessError as e:
        singularity_fatal_error = "\n".join(
            [line for line in e.stderr.split("\n") if line.startswith("FATAL")]
        )
        raise ValueError(
            f"Invalid command {cmd=} passed to Singularity "
            f"resulted in the FATAL error: {singularity_fatal_error}"
        ) from e

    return process


def add_to_env(*, shell_script, env_file):
    """
    Add `shell_script` to the sourced environment in the container.

    Parameters
    ----------
    shell_script : str
        The shell script to add to the sourced environment in the
        container.
    env_file : Path
    """
    with env_file.open(mode="a") as f:
        f.write(shell_script + "\n")


def to_singularity_verbosity(verbosity: int) -> str:
    """
    Add a verbosity level to Singularity commands.

    A mapping of the internal cotainr verbosity level to `Singularity
    verbosity flags
    <https://apptainer.org/docs/user/main/cli/apptainer.html#options>`_.

    Parameters
    ----------
    args : list
        The list of command line arguments constituting the full
        singularity command.

    Returns
    -------
    args : list
        The updated list of singularity command line arguments.
    """
    if verbosity < 0:
        # --silent (-s)
        return "-s"
    elif verbosity == 0:
        # --quiet (-q)
        return "-q"
    elif verbosity >= 3:
        # Assume --verbose (-v) is a debug level
        return "-v"
    else:
        raise ValueError(
            f"The value {verbosity} is cannot be converted to singularity level"
        )


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


def _flush_stdin_buffer():
    """
    Discard queued data on stdin file descriptor.
    TCIOFLUSH selects both the input queue and output queue to be discarded

    https://stackoverflow.com/questions/2520893/how-to-flush-the-input-stream
    """
    from io import UnsupportedOperation

    try:
        sys.stdin.fileno()
    except UnsupportedOperation:
        # stdin is a pseudofile (e.g. Pytest without --no-capture)
        return

    # Python Standard library, Linux/Unix/OSX
    from termios import tcflush, TCIOFLUSH

    tcflush(sys.stdin, TCIOFLUSH)
