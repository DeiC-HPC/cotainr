"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements the interaction with the container runtime.

Classes
-------
SingularitySandbox
    A Singularity container sandbox context manager.
"""

from json import dump, load
import logging
import os
from pathlib import Path
import random
from shutil import copyfile
import sys
from tempfile import TemporaryDirectory
import time
import urllib.error
import urllib.request

from . import __version__ as _cotainr_version
from . import interface, tracing

logger = logging.getLogger(__name__)


class SandboxInterface(interface.BaseInterface):
    """Interface to communicate with Singularity Sandbox folders."""

    def __init__(self, commands: dict):
        super().__init__(commands)

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
        if not filename.exists():
            self.add(filename=filename, log_dispatcher=log_dispatcher)

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


class SingularitySandbox:
    """
    A Singularity container sandbox context manager.

    This creates and manipulates a `Singularity sandbox
    <http://apptainer.org/docs/user/main/build_a_container.html#creating-writable-sandbox-directories>`_,
    i.e. a temporary directory representing the container. As a final step, the
    sandbox should be converted into a SIF container image file.

    Parameters
    ----------
    base_image : str
        Base image to use for the container which may be any valid
        Apptainer/Singularity <BUILD SPEC>.
    log_settings : :class:`~cotainr.tracing.LogSettings`, optional
        The data used to setup the logging machinery (the default is None which
        implies that the logging machinery is not used).

    Attributes
    ----------
    base_image : str
        Base image to use for the container.
    sandbox_dir : :class:`os.PathLike` or None
        The path to the temporary directory containing the sandbox if within a
        sandbox context, otherwise it is None.
    log_dispatcher : :class:`~cotainr.tracing.LogDispatcher` or None.
        The log dispatcher used to process stdout/stderr message from
        Singularity commands that run in sandbox, if the logging machinery is
        used.
    architecture : str or None.
        The machine architecture of the sandbox as returned by `uname -m`. Its
        value is `None` (unknown) until entering the the sandbox context.
    """

    def __init__(self, *, base_image, log_settings=None):
        """Construct the SingularitySandbox context manager."""
        self.base_image = base_image
        self.sandbox_dir = None
        self.architecture = None
        if log_settings is not None:
            self._verbosity = log_settings.verbosity
            self.log_dispatcher = tracing.LogDispatcher(
                name=__class__.__name__,
                map_log_level_func=self._map_log_level,
                log_settings=log_settings,
            )
        else:
            self._verbosity = 0
            self.log_dispatcher = None

        if log_settings.verbosity < 0:
            self._v = "-s"  # --silent (-s)
        elif log_settings.verbosity == 0:
            self._v = "-q"  # --quiet (-q)
        elif log_settings.verbosity == 3:
            self._v = "-v"  # --verbose (-v); limited debug information
        elif log_settings.verbosity >= 4:
            self._v = "-d"  # --debug (-d); all debug information
        else:
            self._v = ""

    def __enter__(self):
        """
        Build and enter sandbox context.

        Returns
        -------
        self : :class:`SingularitySandbox`
            The sandbox context.
        """
        # Store current directory
        self._origin = Path().resolve()

        # Create sandbox
        self._tmp_dir = TemporaryDirectory()
        self.sandbox_dir = Path(self._tmp_dir.name) / "singularity_sandbox"
        self.sandbox_dir.mkdir(exist_ok=False)

        run = f"singularity --nocolor exec --writable --no-home --no-umask {self.sandbox_dir} "
        commands = {"run": run, "add": run + "touch ", "copy": copyfile}
        self.comm = SandboxInterface(commands)

        self.comm.subprocess_runner(
            args=[
                "singularity",
                self._v,
                "--nocolor",
                "build",
                "--force",  # sandbox_dir.mkdir() checks for existing sandbox image
                "--sandbox",
                "--fix-perms",
                self.sandbox_dir,
                self.base_image,
            ],
            log_dispatcher=self.log_dispatcher,
        )

        # Change directory to the sandbox
        os.chdir(self.sandbox_dir)

        self.env_file = self.sandbox_dir / ".singularity.d/env/92-cotainr-env.sh"
        self.comm.write(
            self.sandbox_dir / ".singularity.d/labels.json",
            data={
                "cotainr.command": " ".join(sys.argv),
                "cotainr.version": _cotainr_version,
                "cotainr.url": "https://github.com/DeiC-HPC/cotainr",
            },
            mode="r+",
            log_dispatcher=self.log_dispatcher,
        )

        # Get the architecture of the sandbox if it is not already set
        # (should not be set in real world scenarios)
        if self.architecture is None:
            arch_process = self.comm.run(
                cmd="uname -m", log_dispatcher=self.log_dispatcher
            )
            self.architecture = arch_process.stdout.strip()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit and destroy sandbox context."""
        os.chdir(self._origin)
        self._tmp_dir.cleanup()
        self.sandbox_dir = None

    def build_image(self, *, path):
        """
        Build a SIF image file from sandbox.

        Takes the current content of the sandbox and builds a SIF container
        image from it. The container image is outputted to `path`.

        Parameters
        ----------
        path : :class:`os.PathLike`
            Path to the built container image.
        """
        self.comm.subprocess_runner(
            args=[
                "singularity",
                self._v,
                "--nocolor",
                "build",
                "--force",
                path,
                self.sandbox_dir,
            ],
            log_dispatcher=self.log_dispatcher,
        )

    @staticmethod
    def _map_log_level(msg):
        """
        Attempt to infer log level for a message.

        Parameters
        ----------
        msg : str
            The message to infer log level for.

        Returns
        -------
        log_level : int
            One of the standard log levels (DEBUG, INFO, WARNING, ERROR, or
            CRITICAL).
        """
        if msg.startswith("DEBUG") or msg.startswith("VERBOSE"):
            return logging.DEBUG
        elif msg.startswith("INFO") or msg.startswith("LOG"):
            return logging.INFO
        elif msg.startswith("WARNING"):
            return logging.WARNING
        elif msg.startswith("ERROR"):
            return logging.ERROR
        elif msg.startswith("ABRT") or msg.startswith("FATAL"):
            return logging.CRITICAL
        else:
            # If no prefix on message, assume its INFO level
            return logging.INFO
