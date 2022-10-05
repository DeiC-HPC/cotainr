"""
Container tools for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Classes
-------
Sandbox
"""

import os
from pathlib import Path
import shlex
from tempfile import TemporaryDirectory

from util import stream_subprocess


class Sandbox:
    def __init__(self, base_image):
        self.base_image = base_image
        self.sandbox_dir = None

    def __enter__(self):
        # Store current directory
        self._origin = Path(".").absolute()

        # Create sandbox
        self._tmp_dir = TemporaryDirectory()
        self.sandbox_dir = Path(self._tmp_dir.name) / "sandbox"
        stream_subprocess(
            [
                "singularity",
                "build",
                "--sandbox",
                f"{shlex.quote(str(self.sandbox_dir))}",
                f"{shlex.quote(self.base_image)}",
            ]
        )

        # Change directory to the sandbox
        os.chdir(self.sandbox_dir)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self._origin)
        self._tmp_dir.cleanup()
        self.sandbox_dir = None

    def add_to_env(self, shell_script):
        self._assert_within_sandbox_context()

        env_file = self.sandbox_dir / "environment"
        with env_file.open(mode="a") as f:
            f.write(shell_script + "\n")

    def build_image(self, path):
        self._assert_within_sandbox_context()

        stream_subprocess(
            [
                "singularity",
                "build",
                "--force",
                f"{shlex.quote(str(path))}",
                f"{shlex.quote(str(self.sandbox_dir))}",
            ]
        )

    def _assert_within_sandbox_context(self):
        if self.sandbox_dir is None:
            raise ValueError("The operation is only valid inside a sandbox context.")
