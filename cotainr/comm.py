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

from abc import ABC, abstractmethod
from json import dump, load
from pathlib import Path, PosixPath
import random
from shutil import copyfile
import subprocess
import time
import urllib.error
import urllib.request

from .util import cpath


class BaseCommunicator(ABC):
    """
    Abstract base class to specify container communication API.

    Additionally, basic functionality of running subprocesses and parsing inputs is implemented.
    """

    @abstractmethod
    def write(
        self, filename: Path | str, data: str | dict, mode: str = "a", *, log_dispatcher
    ):
        """Write `data` to the `filename` using the FileDescriptor mode `mode`, and log to log_dispatcher."""
        return NotImplemented

    @abstractmethod
    def copy(self, src_fd, dst_fd, *, log_dispatcher):
        """Copy source file descriptor to destination file descriptor, and log to log_dispatcher."""
        return NotImplemented

    @abstractmethod
    def add(self, *, filename, log_dispatcher):
        """Add new file to container with `filename`, and log to log_dispatcher."""
        return NotImplemented

    @abstractmethod
    def download(self, *, src_url, dst_path, log_dispatcher):
        """Download file from source URL and put it at destination path, and log to log_dispatcher."""
        return NotImplemented

    @abstractmethod
    def run(self, cmd, log_dispatcher, **kwargs):
        """Wrap _subprocess_runner to run command in context of the container and log to log_dispatcher."""
        return NotImplemented

    @staticmethod
    def parse_filename(filename):
        """Convert strings and PosixPath into the container path dataclass `cpath`."""
        if isinstance(filename, str):
            filename = Path(filename)
        if isinstance(filename, PosixPath):
            cfile = cpath(filename)
        else:
            assert isinstance(filename, cpath), (
                f"file-type {type(filename)} is not supported"
            )
            cfile = filename
        return cfile

    @staticmethod
    def subprocess_runner(args, log_dispatcher, **kwargs):
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


class CommunicationInterface(BaseCommunicator):
    """
    Handle communication with Container objects.

    Parameters
    ----------
    exec_default : list
        default arguments required to execute commands inside container
    """

    def __init__(self, exec_default):
        super().__init__()
        self.exec_default = exec_default

    def write(
        self, filename: Path | str, data: str | dict, mode: str = "a", *, log_dispatcher
    ):
        """
        Use to writing `data` into the file located at `filename`.

        Parameters
        ----------
        filename : string, PosixPath or cpath
            The file written that is written to
        data : str
            The data that is written
        mode : str
            Default (a) appends data, alternatives are 'r+', 'wb', 'a' for write, append
        log_dispatcher : :class:`LogDispatcher`
        """
        cfile = self.parse_filename(filename)

        if not cfile.host_path.exists():
            self.add(filename=cfile, log_dispatcher=log_dispatcher)

        log_dispatcher.log_to_stdout(f"Writing to file: {cfile.host_path}")
        with open(cfile.host_path, mode) as fd:
            if cfile.host_path.suffix == ".json":
                assert isinstance(data, dict)

                new_data = load(fd)
                for key, value in data.items():
                    new_data[key] = value
                fd.seek(0)  # Move cursor to start of file?
                dump(new_data, fd)
            else:
                fd.write(data)

    def add(self, *, filename, log_dispatcher):
        """
        Create any file `f` in an existing folder in the Singularity container.

        The file permissions will ignore the system umask.

        Parameters
        ----------
        f : :class:`pathlib.PosixPath` or string
            For example, Path("sandbox_dir/.singularity.d/env/92-cotainr-env.sh")
        log_dispatcher : :class:`LogDispatcher`
        """
        cfile = self.parse_filename(filename)

        # ensure that the file is created *within* the container to get correct permissions, et
        log_dispatcher.log_to_stdout(f"Creating file: {cfile.host_path}")
        self.run(cmd=f"touch {cfile.path}", log_dispatcher=log_dispatcher)

        if not cfile.host_path.exists():
            raise FileNotFoundError(f"Creating file {filename.host_path} failed.")

    def copy(self, src_fd, dst_fd, *, log_dispatcher):
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

        log_dispatcher.log_to_stdout(f"Copying {src_fd} to {dst_fd.host_path}")
        copyfile(
            src_fd, dst_fd.host_path
        )  # shutil function, potential permission issue

        if not dst_fd.host_path.exists():
            raise FileNotFoundError

    def download(self, *, src_url, dst_path, log_dispatcher):
        """
        Download the installer_url to `installer_path`.

        Parameters
        ----------
        src_url : str
            The name of the url where the data is found
        dst_path : str | PosixPath | cpath
            The path where the downloaded file is stored.

        Raises
        ------
        RuntimeError
            If the container sandbox architecture is unknown.
        urllib.error.URLError
            If three attempts at downloading the installer all fail.
        """
        log_dispatcher.log_to_stdout(msg=f"Downloading {src_url}")

        # Make up to 3 attempts at downloading the installer
        for retry in range(3):
            try:
                with urllib.request.urlopen(src_url) as url:  # nosec B310
                    self.write(
                        filename=dst_path,
                        data=url.read(),
                        mode="wb",
                        log_dispatcher=log_dispatcher,
                    )
                    # dst_path.write_bytes(url.read())

                return dst_path

            except urllib.error.URLError as e:
                url_error = e

                # Exponential back-off
                time.sleep(2**retry + random.uniform(0.001, 1))  # nosec B311

        else:
            raise url_error

    def run(self, cmd, log_dispatcher, **kwargs):
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

        return self.subprocess_runner(singularity_args + cmd, log_dispatcher)
