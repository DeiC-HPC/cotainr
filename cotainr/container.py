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

import json
import logging
import os
from pathlib import Path
import shlex
import subprocess
import weakref
from tempfile import TemporaryDirectory

from . import tracing
from . import util

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
    """

    def __init__(self, *, base_image, log_settings=None):
        """Construct the SingularitySandbox context manager."""

        if log_settings is not None:
            _verbosity = log_settings.verbosity
            self.log_dispatcher = tracing.LogDispatcher(
                name=__class__.__name__,
                map_log_level_func=self._map_log_level,
                log_settings=log_settings,
            )
        else:
            _verbosity = 0
            self.log_dispatcher = None
        self._singularity_verbosity = to_singularity_verbosity(_verbosity)

        # Store current directory
        self._origin = Path().resolve()

        # Create sandbox
        _tmp_dir = TemporaryDirectory()
        self.sandbox_dir = Path(_tmp_dir.name) / "singularity_sandbox"
        self.sandbox_dir.mkdir(exist_ok=False)

        # Build sandbox.
        util.stream_subprocess(
            args=[
                "singularity",
                self._singularity_verbosity,
                "--nocolor",
                "build",
                "--force",  # sandbox_dir.mkdir() checks for existing sandbox image
                "--sandbox",
                "--fix-perms",
                self.sandbox_dir,
                base_image,
            ],
            log_dispatcher=self.log_dispatcher,
        )

        self.finalizer = weakref.finalize(
            self, self._cleanup, Path().resolve(), _tmp_dir
        )

        # Change directory to the sandbox
        os.chdir(self.sandbox_dir)

        self.env_file = self.sandbox_dir / ".singularity.d/env/92-cotainr-env.sh"
        if not self.env_file.exists():
            self._create_file(fil=self.env_file)

        self.labels_file = self.sandbox_dir / ".singularity.d/labels.json"
        if not self.labels_file.exists():
            self._create_file(fil=self.labels_file)

    @staticmethod
    def _cleanup(_origin, _tmp_dir):
        os.chdir(_origin)
        _tmp_dir.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit and destroy sandbox context."""
        self.finalizer()

    def add_metadata(self, metadata):
        """
        Add metadata to the container sandbox.

        The following metadata is added to the container sandbox:
          - "cotainr.command": The full command line used to build the container.
          - "cotainr.version": The version of cotainr used to build the container.
          - "cotainr.url": The cotainr project url.

        The container metadata may be inspected by running `singularity inspect` on the
        built container image file.

        Notes
        -----
        The metadata entries are added to the `.singularity.d/labels.json
        <https://apptainer.org/docs/user/main/environment_and_metadata.html#singularity-d-directory>`_
        file.

        """

        with open(self.labels_path, "r+") as f:
            metadata = json.load(f)
            f.seek(0)
            json.dump(metadata, f)

    def _create_file(self, *, fil):
        """
        Create the Path/file `fil` in the Singularity container.

        Parameters
        ----------
        fil : :class:`pathlib.PosixPath`
            For example, Path("sandbox_dir/.singularity.d/env/92-cotainr-env.sh")
        """

        # ensure that the file is created *within* the container to get correct permissions, etc.
        self.run_command_in_container(cmd=f"touch {fil}")

        if not fil.exists():
            raise FileNotFoundError(f"Creating file {fil} failed.")

    def add_to_env(self, *, shell_script):
        """
        Add `shell_script` to the sourced environment in the container.

        Parameters
        ----------
        shell_script : str
            The shell script to add to the sourced environment in the
            container.
        """
        with self.env_file.open(mode="a") as f:
            f.write(shell_script + "\n")

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
        util.stream_subprocess(
            args=[
                "singularity",
                self._singularity_verbosity,
                "--nocolor",
                "build",
                "--force",
                path,
                self.sandbox_dir,
            ],
            log_dispatcher=self.log_dispatcher,
        )

    def run_command_in_container(self, *, cmd, custom_log_dispatcher=None):
        """
        Run a command in the container sandbox.

        Wraps `singularity exec` of the `cmd` in the container sandbox`
        allowing for running commands inside the container sandbox context,
        e.g. for installing software in the container sandbox.

        Parameters
        ----------
        cmd : str
            The command to run in the container sandbox.
        custom_log_dispatcher : :class:`~cotainr.tracing.LogDispatcher`, optional
            The custom log dispatcher to use when running the command (the
            default is None which implies that the `SingularitySandbox` log
            dispatcher is used).

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

        try:
            process = util.stream_subprocess(
                args=[
                    "singularity",
                    self._singularity_verbosity,
                    "--nocolor",
                    "exec",
                    "--writable",
                    "--no-home",
                    "--no-umask",
                    self.sandbox_dir,
                    *shlex.split(cmd),
                ],
                log_dispatcher=custom_log_dispatcher,
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
    elif verbosity == 1 or verbosity == 2:
        return ""
    else:
        raise ValueError(
            f"The value {verbosity} is cannot be converted to singularity level"
        )
