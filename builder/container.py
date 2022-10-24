"""
Container tools for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Classes
-------
Sandbox
    A Singularity container sandbox context manager.
"""

import os
from pathlib import Path
import shlex
from tempfile import TemporaryDirectory

from util import stream_subprocess


class SingularitySandbox:
    """
    A Singularity container sandbox context manager.

    This creates and manipulates a `Singularity sandbox
    <https://docs.sylabs.io/guides/3.0/user-guide/build_a_container.html#creating-writable-sandbox-directories>`_,
    i.e. a temporary directory representing the container. As a final step, the
    sandbox should be converted into a SIF container image file.

    Parameters
    ----------
    base_image : str
        Base image to use for the container which may be any valid
        Apptainer/Singularity <BUILD SPEC>.

    Attributes
    ----------
    base_image : str
        Base image to use for the container.
    sanbbox_dir : os.PathLike or None
        The path to the temporary directory containing the sandbox if within a
        sandbox context, otherwise it is None.
    """

    def __init__(self, *, base_image):
        self.base_image = base_image
        self.sandbox_dir = None

    def __enter__(self):
        """
        Build and enter sandbox context.

        Returns
        -------
        self : SingularitySandbox
            The sandbox context.
        """
        # Store current directory
        self._origin = Path(".").absolute()

        # Create sandbox
        self._tmp_dir = TemporaryDirectory()
        self.sandbox_dir = Path(self._tmp_dir.name) / "sandbox"
        stream_subprocess(
            args=[
                "singularity",
                "build",
                "--sandbox",
                self.sandbox_dir,
                self.base_image,
            ]
        )

        # Change directory to the sandbox
        os.chdir(self.sandbox_dir)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit and destroy sandbox context."""
        os.chdir(self._origin)
        self._tmp_dir.cleanup()
        self.sandbox_dir = None

    def add_to_env(self, *, shell_script):
        """
        Add `shell_script` to the sourced environment in the container.

        The content of `shell_script` is written as-is to the /environment file
        in the Singularity container which is sourced on execution of the
        container.

        Parameters
        ----------
        shell_script : str
            The shell script to add to the sourced environment in the
            container.
        """
        self._assert_within_sandbox_context()

        env_file = self.sandbox_dir / "environment"
        with env_file.open(mode="a") as f:
            f.write(shell_script + "\n")

    def build_image(self, *, path):
        """
        Build a SIF image file from sandbox.

        Takes the current content of the sandbox and builds a SIF container
        image from it. The container image is outputted to `path`.

        Parameters
        ----------
        path : os.PathLike
            Path to the built container image.
        """
        self._assert_within_sandbox_context()

        stream_subprocess(
            args=[
                "singularity",
                "build",
                "--force",
                path,
                self.sandbox_dir,
            ]
        )

    def run_command_in_container(self, *, cmd):
        """
        Run a command in the container sandbox.

        Wraps `singularity exec` of the `cmd` in the container sandbox`
        allowing for running commands inside the container sandbox context,
        e.g. for installing software in the container sandbox.

        Parameters
        ----------
        cmd : str
            The command to run in the container sandbox.

        Returns
        -------
        process : subprocess.CompletedProcess
            Information about the process that ran in the container sandbox.

        Notes
        -----
        The command is run with `--no-home` for maximum compatibility (e.g.
        trying to mount the home folder on LUMI causes problems). Thus, when
        running a command in the container, you cannot reference files in your
        home directory. Instead you must copy all files into the container
        sandbox and then reference the files relative to the container root.
        """
        self._assert_within_sandbox_context()

        process = stream_subprocess(
            args=[
                "singularity",
                "exec",
                "--writable",
                "--no-home",
                self.sandbox_dir,
                *shlex.split(cmd),
            ]
        )

        return process

    def _assert_within_sandbox_context(self):
        """Raise a ValueError if we are not inside the sandbox context."""
        if self.sandbox_dir is None:
            raise ValueError("The operation is only valid inside a sandbox context.")
