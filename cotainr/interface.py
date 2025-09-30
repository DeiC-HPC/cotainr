"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module contains lower level interfaces define communication protocol with containers.

Classes
-------
AbstractInterface
    An abstract class to define the methods subclasses must define
BaseInterface
    A default implementation that dispatches subprocessors and functions
"""

from abc import ABC, abstractmethod
import subprocess


class AbstractInterface(ABC):
    """
    Abstract base class to specify container communication API.

    Additionally, basic functionality of running subprocesses and parsing inputs is implemented.
    """

    @abstractmethod
    def write(self, filename, data, mode, *, log_dispatcher):
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

    @staticmethod
    def function_runner(func, log_dispatcher, *args, **kwargs):
        """
        Execute function with args and kwargs and log the results.

        Parameters
        ----------
        func : `callable` function
        log_dispatcher : :class:`~cotainr.tracing.LogDispatcher`, optional
            The log dispatcher to use when running the command

        Returns
        -------
        process : function output
        """
        log_dispatcher.log_to_stdout(
            f"Running function: {func.__name__}({args}, {kwargs})"
        )
        output = func(*args, **kwargs)
        log_dispatcher.log_to_stdout(f"Function output: {output}")
        return output

    def dispatch(self, cmd_type, *args, **kwargs):
        """Dispatch cli commands through subprocess and python functions."""
        cmd = self.commands.get(cmd_type, None)
        if isinstance(cmd, str):
            sub_args = kwargs.pop(
                "args", args[0]
            )  #  try keyword args else positional args [0]
            sub_args = cmd + str(sub_args)
            sub_args = sub_args.split(" ")
            log_dispatcher = kwargs.pop("log_dispatcher")
            return self.subprocess_runner(sub_args, log_dispatcher, **kwargs)
        elif callable(cmd):
            log_dispatcher = kwargs.pop("log_dispatcher")
            return self.function_runner(cmd, log_dispatcher, *args, **kwargs)
        else:
            print(
                f"Command of type {cmd_type} of type {type(cmd)} with args {args} and kwargs {kwargs} failed."
            )
            raise AttributeError("Command not recognized")


class BaseInterface(AbstractInterface):
    """
    Handle communication with Container objects.

    Parameters
    ----------
    exec_default : list
        default arguments required to execute commands inside container
    """

    def __init__(self, commands: dict):
        super().__init__()
        self.commands = commands

    def write(self, filename, data, mode, *, log_dispatcher):
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
        self.dispatch("write", filename, data, mode, log_dispatcher=log_dispatcher)

    def add(self, filename, *, log_dispatcher):
        """
        Create any file `filename` in an existing folder in the Singularity container.

        The file permissions will ignore the system umask.

        Parameters
        ----------
        f : :class:`pathlib.PosixPath` or string
            For example, Path("sandbox_dir/.singularity.d/env/92-cotainr-env.sh")
        log_dispatcher : :class:`LogDispatcher`
        """
        self.dispatch("add", filename, log_dispatcher=log_dispatcher)

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
        self.dispatch("copy", src_fd, dst_fd, log_dispatcher=log_dispatcher)

    def download(self, *, src_url, dst_path, log_dispatcher):
        """
        Download the installer_url to `installer_path`.

        Parameters
        ----------
        src_url : str
            The name of the url where the data is found
        dst_path : str | PosixPath | cpath
            The path where the downloaded file is stored.

        v        Raises
        ------
        RuntimeError
            If the container sandbox architecture is unknown.
        urllib.error.URLError
            If three attempts at downloading the installer all fail.
        """
        self.dispatch("download", src_url, dst_path, log_dispatcher=log_dispatcher)

    def run(self, cmd, *, log_dispatcher, **kwargs):
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
        return self.dispatch("run", cmd, log_dispatcher=log_dispatcher)
