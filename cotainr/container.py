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
import sys
from pathlib import Path
import weakref
from tempfile import TemporaryDirectory

from . import tracing
from . import util
from . import __version__ as _cotainr_version

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

        self.base_image = base_image
        if log_settings is None:
            log_settings = tracing.LogSettings()

        self.log_dispatcher = tracing.LogDispatcher(
            name=__class__.__name__,
            map_log_level_func=self._map_log_level,
            log_settings=log_settings,
        )

        self._singularity_verbosity = to_singularity_verbosity(log_settings.verbosity)

    @staticmethod
    def _cleanup(_origin, _tmp_dir):
        os.chdir(_origin)
        _tmp_dir.cleanup()

    def __enter__(self):
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
                self.base_image,
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

        self.labels_path = self.sandbox_dir / ".singularity.d/labels.json"
        if not self.labels_path.exists():
            self._create_file(fil=self.labels_path)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit and destroy sandbox context."""
        self.finalizer()

    def add_metadata(self):
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
            metadata["cotainr.command"] = " ".join(sys.argv)
            metadata["cotainr.version"] = _cotainr_version
            metadata["cotainr.url"] = "https://github.com/DeiC-HPC/cotainr"
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
        util.run_command_in_sandbox(
            cmd=f"touch {fil}",
            sandbox_dir=self.sandbox_dir,
            log_dispatcher=self.log_dispatcher,
        )

        if not fil.exists():
            raise FileNotFoundError(f"Creating file {fil} failed.")

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
            f"The value {verbosity} is cannot be converted to singularity log-level"
        )
