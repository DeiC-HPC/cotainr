"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements the interaction with the container runtime.

Classes
-------
CommunicationInterface
    A interface to communicate with the Singularity container.
"""

from json import dump, load
from pathlib import Path
from shutil import copyfile
import subprocess


class CommunicationInterface:
    """
    Handle communication with Container objects.

    Parameters
    ----------
    exec_default : list
        default arguments required to execute commands inside container
    """

    def __init__(self, exec_default):
        self.exec_default = exec_default

    def write_to_file(
        self, filename: Path | str, data: str | dict, mode: str = "a", *, log_dispatcher
    ):
        """
        Use to writing `data` into the file located at `filename`.

        Parameters
        ----------
        filename : PathLike
            The file written that is written to
        data : str
            The data that is written
        mode : str
            Default (a) appends data, alternatives are 'r+', 'a' for write, append
        log_dispatcher : :class:`LogDispatcher`
        """
        if isinstance(filename, str):
            filename = Path(filename)

        if not filename.exists():
            self.create_file(filename=filename, log_dispatcher=log_dispatcher)

        log_dispatcher.log_to_stdout(f"Writing to file: {filename}")
        with open(filename, mode) as fd:
            if filename.suffix == ".json":
                assert isinstance(data, dict)

                new_data = load(fd)
                for key, value in data.items():
                    new_data[key] = value
                fd.seek(0)  # Move cursor to start of file?
                dump(new_data, fd)
            else:
                fd.write(data)

    def create_file(self, *, filename, log_dispatcher):
        """
        Create any file `f` in an existing folder in the Singularity container.

        The file permissions will ignore the system umask.

        Parameters
        ----------
        f : :class:`pathlib.PosixPath` or string
            For example, Path("sandbox_dir/.singularity.d/env/92-cotainr-env.sh")
        log_dispatcher : :class:`LogDispatcher`
        """
        # ensure that the file is created *within* the container to get correct permissions, et
        log_dispatcher.log_to_stdout(f"Creating file: {filename}")
        self.run_command_in_container(
            cmd=f"touch {filename}", log_dispatcher=log_dispatcher
        )

        if not filename.exists():
            raise FileNotFoundError(f"Creating file {filename} failed.")

    def copy_file(self, src_fd, dst_fd, *, log_dispatcher):
        """
        Copy any file from `src_fd` from the filesystem to `dst_fd` in the container.

        The file permissions will ignore the system umask.

        Parameters
        ----------
        src_fd : :class:`pathlib.PosixPath` or string
        dst_fd : :class:`pathlib.PosixPath` or string
        log_dispatcher : :class:`LogDispatcher`
        """
        if not src_fd.exists():
            raise FileNotFoundError

        log_dispatcher.log_to_stdout(f"Copying {src_fd} to {dst_fd}")
        copyfile(src_fd, dst_fd)  # shutil function, potential permission issue

        if not dst_fd.exists():
            raise FileNotFoundError

    def run_command_in_container(self, cmd, log_dispatcher, **kwargs):
        """
        Wrap the subprocess runner with container information.

        Parameters
        ----------
        cmd : list
            A cli command delimited in a list where spaces normally occur
        log_dispatcher : LogDispatcher
            Logging the command to the responsible class
        kwargs : dict
            Optional "exec" keyword-argument to overwrite the exec_default

        Returns
        -------
        process : :class:`subprocess.CompletedProcess`
            Information about the process that ran in the container sandbox.
        """
        singularity_args = kwargs.pop("exec", self.exec_default)
        if isinstance(cmd, str):
            cmd = cmd.split(" ")
        return self._subprocess_runner(singularity_args + cmd, log_dispatcher)

    def _subprocess_runner(self, args, log_dispatcher, **kwargs):
        """
        Wrap the choice of subprocess runner.

        Parameters
        ----------
        args : list or str
            Subprocess arguments.
        log_dispatcher : :class:`~cotainr.tracing.LogDispatcher`, optional
            The log dispatcher to use when running the command

        Returns
        -------
        process : :class:`subprocess.CompletedProcess`
            Information about the subprocess.
        """
        if isinstance(args, list):
            args = [str(a) for a in args]  # Convert PosixPath into string
            args = list(filter(None, args))  # Filter empty strings

        log_dispatcher.log_to_stdout(f"Running command: {' '.join(args)}")
        try:
            completed_process = subprocess.run(
                args, capture_output=True, text=True, check=True, **kwargs
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(
                f"Invalid command: {' '.join(args)}\n Captured error: {e.stderr}"
            ) from e

        log_dispatcher.log_to_stdout(completed_process.stdout)
        return completed_process
