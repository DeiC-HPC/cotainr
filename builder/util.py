"""
Packaging for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Functions
---------
stream_subprocess(args, **kwargs)
    Run a the command described by `args` while streaming stdout and stderr.
"""

import subprocess


def stream_subprocess(args, **kwargs):
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
        stderr=subprocess.STDOUT,
        bufsize=1,
        **kwargs,
    ) as process:
        for line in process.stdout:
            print(line, end="")

    completed_process = subprocess.CompletedProcess(
        process.args,
        process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
    )
    completed_process.check_returncode()

    return completed_process
