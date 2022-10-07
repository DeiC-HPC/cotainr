"""
Packaging for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Functions
---------
stream_subprocess(*, args, **kwargs)
    Run a the command described by `args` while streaming stdout and stderr.
"""

from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys


def stream_subprocess(*, args, **kwargs):
    """
    Run a the command described by `args` while streaming stdout and stderr.

    The command described by `args` is run in a subprocess with that
    subprocess' stdout and stderr streamed to the stdout. Extra `kwargs` are
    passed to `Popen` when opening the subprocess.

    Parameters
    ----------
    args : sequence or str or path_like
        Program arguments. See the docstring for subprocess.Popen for details.

    Returns
    -------
    completed_process : subprocess.CompletedProcess
        Information about the completed subprocess.

    Raises
    ------
    subprocess.CalledProcessError
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
            stdout="\n".join(captured_stdout),
            stderr="\n".join(captured_stderr),
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
