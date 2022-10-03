"""
Container tools for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Classes
-------
Sandbox
"""

from multiprocessing.sharedctypes import Value
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from util import stream_subprocess


class Sandbox:
    def __init__(self, base_image):
        self.base_image = base_image
        self.sandbox_dir = None

    def __enter__(self):
        # Store current directory
        self.origin = Path(".").absolute()

        # Create sandbox
        self.tmp_dir = TemporaryDirectory()
        self.sandbox_dir = Path(self.tmp_dir.name) / "sandbox"
        # TODO: handle custom tmp dir placement?
        stream_subprocess(
            [
                "singularity",
                "build",
                "--sandbox",
                f"{self.sandbox_dir}",
                f"{self.base_image}",
            ]
        )
        # TODO: handle apptainer? TODO: extra args to singularity?

        # Change directory to the sandbox
        os.chdir(self.sandbox_dir)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.origin)
        self.tmp_dir.cleanup()
        self.sandbox_dir = None

    def add_to_env(self, shell_script):
        if self.sandbox_dir is None:
            raise ValueError("Operation only available inside sandbox context.")

        env_file = self.sandbox_dir / "environment"
        with env_file.open(mode="a") as f:
            f.write(shell_script)

    def build_image(self, path):
        if self.sandbox_dir is None:
            raise ValueError("Operation only available inside sandbox context.")

        # TODO: gracefully handle not overwriting existing image file

        stream_subprocess(
            ["singularity", "build", "--force", f"{path}", f"{self.sandbox_dir}"]
        )
