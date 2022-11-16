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
import json
from pathlib import Path
import subprocess
import sys
import time
import re


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


def stream_subprocess(*, args, **kwargs):
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
        with ThreadPoolExecutor(max_workers=3) as executor:
            # (Attempt to) pass the process stdout and stderr to the terminal in real
            # time while also storing it for later inspection.
            progress = ProgressHandler()
            stdout_future = executor.submit(
                _print_and_capture_stream,
                stream_handle=process.stdout,
                progress=progress,
            )
            stderr_future = executor.submit(
                _print_and_capture_stream,
                stream_handle=process.stderr,
                progress=progress,
            )
            executor.submit(
                progress.run,
            )
            captured_stdout = stdout_future.result()
            captured_stderr = stderr_future.result()
            progress.stop()

    completed_process = subprocess.CompletedProcess(
        process.args,
        process.returncode,
        stdout="".join(captured_stdout),
        stderr="".join(captured_stderr),
    )

    completed_process.check_returncode()

    return completed_process


def _print_and_capture_stream(*, stream_handle, progress):
    """
    Print a text stream while also storing it.

    Parameters
    ----------
    stream_handle : io.TextIOWrapper
        The text stream to print and capture.
    progress : ProgressHandler
        The object that prints the output.
    """
    captured_stream = []
    for line in stream_handle:
        captured_stream.append(line)
        progress.change_message(line)

    return captured_stream


class ProgressHandler:
    """
    A class for printing output progress nicely.
    It needs to run in a separate thread.
    """

    def __init__(self):
        """Construct the progress handler"""
        self._spinner = "⣾⣷⣯⣟⡿⢿⣻⣽"
        self._index = 0
        self._msg = ""
        self._sleep_interval = 0.1
        self._running = True
        self._ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def stop(self):
        """Stop the printing process"""
        self._running = False

    def change_message(self, msg):
        """
        Change the message that is being printed.

        Parameters
        ----------
        msg : str
            Change the message that is being printed.
        """
        msg = msg.strip(" \r\n")
        msg = self._ansi_escape.sub("", msg)
        if len(msg) > 100:
            msg = msg[:97] + "..."
        self._msg = msg

    def run(self):
        """
        Start the process of printing out the lastest message.
        It will run until the stop function is being called.
        """
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        while self._running:
            self._index = (self._index + 1) % len(self._spinner)
            print(f"\r{self._spinner[self._index]} {self._msg:<100}", end="\r")
            time.sleep(self._sleep_interval)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
