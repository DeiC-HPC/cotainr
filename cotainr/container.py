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

import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from . import comm, tracing
from .util import cpath

logger = logging.getLogger(__name__)


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

    def __init__(self, *, base_image, log_settings=None, prefix=None):
        """Construct the SingularitySandbox context manager."""
        self.base_image = base_image
        self.sandbox_dir = None
        self.architecture = None
        self.env_file = None
        self.metadata_file = None
        self.comm = None
        self.prefix = prefix

        if log_settings is None:
            log_settings = tracing.LogSettings()

        self.log_dispatcher = tracing.LogDispatcher(
            name=__class__.__name__,
            map_log_level_func=self._map_log_level,
            log_settings=log_settings,
        )

        if log_settings.verbosity < 0:
            self.ss_verbosity = "-s"  # --silent (-s)
        elif log_settings.verbosity == 0:
            self.ss_verbosity = "-q"  # --quiet (-q)
        elif log_settings.verbosity == 3:
            self.ss_verbosity = "-v"  # --verbose (-v); limited debug information
        elif log_settings.verbosity >= 4:
            self.ss_verbosity = "-d"  # --debug (-d); all debug information
        else:
            self.ss_verbosity = ""

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
        self._tmp_dir = TemporaryDirectory(prefix=self.prefix)
        sandbox_dir = Path(self._tmp_dir.name) / "singularity_sandbox"
        sandbox_dir.mkdir(exist_ok=False)

        # Create communication interface into sandbox
        """
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
        self.sandbox_dir = cpath.from_hostpath(sandbox_dir, sandbox_dir)
        # self.sandbox_dir = cpath(sandbox_dir)
        exec_default = [
            "singularity",
            "--nocolor",
            "exec",
            "--writable",
            "--no-home",
            "--no-umask",
            self.sandbox_dir.host_path,
        ]
        self.comm = comm.CommunicationInterface(exec_default)
        self.env_file = self.sandbox_dir / ".singularity.d/env/92-cotainr-env.sh"
        self.metadata_file = self.sandbox_dir / ".singularity.d/labels.json"

        self.comm.subprocess_runner(
            args=[
                "singularity",
                self.ss_verbosity,
                "--nocolor",
                "build",
                "--force",  # sandbox_dir.mkdir() checks for existing sandbox image
                "--sandbox",
                "--fix-perms",
                self.sandbox_dir.host_path,
                self.base_image,
            ],
            log_dispatcher=self.log_dispatcher,
        )

        # Change directory to the sandbox
        os.chdir(self.sandbox_dir.host_path)

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

    def __getattr__(self, func):
        """
        Wrap all methods of CommunicationInterface.

        It is called as last resort after getattr(self, method) ie. self.method()
        is not found.
        """

        def method(*args, **kwargs):
            if func in dir(self.comm) and not func.startswith("_"):
                return getattr(self.comm, func)(
                    *args, **kwargs, log_dispatcher=self.log_dispatcher
                )
            else:
                raise AttributeError

        return method

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
                self.ss_verbosity,
                "--nocolor",
                "build",
                "--force",
                path,
                self.sandbox_dir.host_path,
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
