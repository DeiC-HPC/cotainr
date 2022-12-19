"""
Packaging for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Functions
---------
stream_subprocess(\*, args, \*\*kwargs)
    Run a the command described by `args` while streaming stdout and stderr.
"""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import os

systems_file = (Path(__file__) / "../../systems.json").resolve()


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
        with ThreadPoolExecutor(max_workers=2) as executor:
            # (Attempt to) pass the process stdout and stderr to the terminal in real
            # time while also storing it for later inspection.
            stdout_future = executor.submit(
                _print_and_capture_stream,
                stream_handle=process.stdout,
                print_stream=sys.stdout,
            )
            stderr_future = executor.submit(
                _print_and_capture_stream,
                stream_handle=process.stderr,
                print_stream=sys.stderr,
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

def _print_and_capture_stream(*, stream_handle, print_stream):
    """
    Print a text stream while also storing it.

    Parameters
    ----------
    stream_handle : io.TextIOWrapper
        The text stream to print and capture.
    print_stream : file object implementing write(string) method.
        The file object to print the stream to.
    """
    captured_stream = []
    for line in stream_handle:
        print(line, end="", file=print_stream)
        captured_stream.append(line)

    return captured_stream


def get_systems():
    """
    Get a dictionary of predefined systems, defined in systems.json

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


def check_python(version_to_check):
    """
    Check python version for running version of python with minimum requried version.

    Parameters
    ----------
    vesion_to_check : tuple
        A version tuple with major and minor versions
    """
    try:
        assert sys.version_info >= version_to_check
    except AssertionError:
        return False
    return True

def check_path(path_to_check):
    """
    Check if a path exist on the system running containr.

    Parameters
    ----------
    path_to_check : list of string
        path on the system to cehck if exist.
    """
    
    for r in path_to_check:
        if os.path.exists(path_to_check):
            return True
    return False

def check_container_version(version_to_check):
    """
    check for singularity version for minimum version.

    Paramesters
    ---------
    version_to_check : tuple of int
        minimum version of singularity.
    """
    try:
        p = subprocess.check_output([
                    "singularity",
                    "version"]
            )
        s = p.decode()
        print(s)
        v = tuple(map(int, s.split('.')))
        assert version_to_check >= v
        return True
    except ValueError:
        return False
    except FileNotFoundError:
        return False
    except AssertionError:
        return False
    
    return True
    
    
