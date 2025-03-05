"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Copyright Aarni Koskela

Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements packing of software into the container.

Classes
-------
PipInstall
    A virtualenv + pip installation in a container sandbox.
"""

from __future__ import annotations

import logging
import os.path
import pathlib
import shlex

from . import container
from . import pack
from . import tracing


logger = logging.getLogger(__name__)


PIP_INSTALL_ARGS = (
    "--no-cache-dir",
    "--disable-pip-version-check",
    "--no-warn-script-location",
)


class PipInstall(pack.PackBase):
    def __init__(
        self,
        *,
        sandbox: container.SingularitySandbox,
        prefix: str = "/opt/venv",
        base_python: str = "python3",
        use_uv: bool = False,
        log_settings: tracing.LogSettings | None = None,
    ):
        """Bootstrap a virtualenv with requirements file(s)."""
        super().__init__(sandbox=sandbox, log_settings=log_settings)
        self.prefix = prefix
        self.base_python = base_python
        self.use_uv = use_uv

        if self.use_uv:
            self._run_command_in_sandbox(
                cmd=[self.base_python, "-m", "pip", "install", *PIP_INSTALL_ARGS, "uv"],
            )

        if self.use_uv:
            self._run_command_in_sandbox(
                cmd=[
                    self.base_python,
                    "-m",
                    "uv",
                    "venv",
                    self.prefix,
                    "-p",
                    self.base_python,
                    "--seed",  # Although we'll be using `uv`, some other software may expect `pip` to be present
                ],
            )
        else:
            self._run_command_in_sandbox(
                cmd=[self.base_python, "-m", "venv", self.prefix],
            )

        self.venv_python = os.path.join(self.prefix, "bin", "python")

    def configure(
        self,
        *,
        requirements_files: list[str | pathlib.Path],
        add_to_env: bool,
    ) -> None:
        for file in requirements_files:
            logger.info("Installing requirements from %s", file)
            if self.use_uv:
                self._run_command_in_sandbox(
                    cmd=[
                        self.base_python,
                        "-m",
                        "uv",
                        "pip",
                        "install",
                        "--python",
                        self.venv_python,
                        "--no-cache",
                        "--link-mode=copy",  # hard-linking/cloning won't work anyway
                        "-r",
                        str(file),
                    ],
                )
            else:
                self._run_command_in_sandbox(
                    cmd=[
                        self.venv_python,
                        "-m",
                        "pip",
                        "install",
                        *PIP_INSTALL_ARGS,
                        "-r",
                        str(file),
                    ],
                )

        self.cleanup()  # We have to do this before adding the activate script to env, otherwise `base_python` is gone

        if add_to_env:
            logger.info(
                "Adding virtualenv %s activation script to environment",
                self.prefix,
            )
            activate_script = os.path.join(self.prefix, "bin/activate")
            self.sandbox.add_to_env(shell_script=f"source {activate_script}")

    def cleanup(self) -> None:
        logger.info("Cleaning up Python installer caches")
        self._run_command_in_sandbox(
            cmd=[
                "sh",
                "-c",
                f'rm -rf "$({shlex.quote(self.base_python)} -m pip cache dir)"',
            ],
        )
        if self.use_uv:
            self._run_command_in_sandbox(
                cmd=[self.base_python, "-m", "uv", "-q", "cache", "clean"],
            )
