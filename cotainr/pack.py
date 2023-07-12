"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements packing of software into the container.

Classes
-------
CondaInstall
    A Conda installation in a container sandbox.
"""

import logging
from pathlib import Path
import time
import random
import re
import urllib.error
import urllib.request

from . import tracing

logger = logging.getLogger(__name__)


class CondaInstall:
    """
    A Conda installation in a container sandbox.

    Bootstraps a miniforge based Conda installation in a container sandbox.

    Parameters
    ----------
    sandbox : :class:`~cotainr.container.SingularitySandbox`
        The sandbox in which Conda should be installed.
    prefix : str
        The Conda prefix to use for the Conda install.

    Attributes
    ----------
    sandbox : :class:`~cotainr.container.SingularitySandbox`
        The sandbox in which Conda is installed.
    prefix : str
        The Conda prefix used for the Conda install.
    """

    def __init__(self, *, sandbox, prefix="/opt/conda", verbosity, log_file_path=None):
        """Bootstrap a conda installation."""
        self.sandbox = sandbox
        self.prefix = prefix
        self.verbosity = verbosity
        self.log_dispatcher = tracing.LogDispatcher(
            name=__class__.__name__,
            map_log_level_func=self._map_log_level,
            verbosity=verbosity,
            log_file_path=log_file_path,
            filters=self._logging_filters,
        )

        # Download Conda installer
        conda_installer_path = (
            Path(self.sandbox.sandbox_dir).resolve() / "conda_installer.sh"
        )
        self._download_conda_installer(path=conda_installer_path)

        # Bootstrap Conda environment in container
        self._bootstrap_conda(installer_path=conda_installer_path)

        # Remove unneeded files
        conda_installer_path.unlink()
        self.cleanup_unused_files()

    def add_environment(self, *, path, name):
        """
        Add an exported Conda environment to the Conda install.

        Equivalent to calling "conda env create -f `path` -n `name`".

        Parameters
        ----------
        path : :class:`os.PathLike`
            The path to the exported env.yml file describing the Conda
            environment to install.
        name : str
            The name to use for the installed Conda environment.
        """
        self._run_command_in_sandbox(
            cmd=f"conda env create -f {path} -n {name}" + self._conda_verbosity_arg
        )

    def cleanup_unused_files(self):
        """
        Remove all unused Conda files.

        Equivalent to calling "conda clean -a".
        """
        self._run_command_in_sandbox(
            cmd="conda clean -y -a" + self._conda_verbosity_arg
        )

    def _bootstrap_conda(self, *, installer_path):
        """
        Install Conda and at its source script to the sandbox env.

        Parameters
        ----------
        installer_path : pathlib.Path
            The path of the Conda installer to run to bootstrap Conda.
        """
        # Run Conda installer
        self._run_command_in_sandbox(
            cmd=f"bash {installer_path.name} -b -s -p {self.prefix}"
        )

        # Add Conda to container sandbox env
        self.sandbox.add_to_env(
            shell_script=f"source {self.prefix + '/etc/profile.d/conda.sh'}"
        )

        # Check that we correctly use the newly installed Conda from now on
        self._check_conda_bootstrap_integrity()

        # Update the installed Conda package manager to the latest version
        self._run_command_in_sandbox(
            cmd=(
                "conda update -y -n base -c conda-forge conda"
                + self._conda_verbosity_arg
            )
        )

    def _check_conda_bootstrap_integrity(self):
        """Raise RuntimeError if multiple interfering Conda installs are found."""
        source_check_process = self._run_command_in_sandbox(cmd="conda info --base")
        if source_check_process.stdout.strip() != f"{self.prefix}":
            raise RuntimeError(
                "Multiple Conda installs interfere. "
                "We risk destroying the Conda install in "
                f"{source_check_process.stdout.strip()}. Aborting!"
            )

    def _download_conda_installer(self, *, path):
        """
        Download the Conda installer to `path`.

        Parameters
        ----------
        path : pathlib.Path
            The path to download the conda installer to.
        """
        conda_installer_url = (
            "https://github.com/conda-forge/miniforge/releases/latest/download/"
            "Miniforge3-Linux-x86_64.sh"
        )

        # Make up to 3 attempts at downloading the installer
        for retry in range(3):
            try:
                with urllib.request.urlopen(conda_installer_url) as url:  # nosec B310
                    path.write_bytes(url.read())

                break

            except urllib.error.URLError as e:
                url_error = e

                # Exponential back-off
                time.sleep(2**retry + random.uniform(0.001, 1))  # nosec B311

        else:
            raise url_error

    def _run_command_in_sandbox(self, *, cmd):
        # TODO: document
        return self.sandbox.run_command_in_container(
            cmd=cmd, custom_log_dispatcher=self.log_dispatcher
        )

    @property
    def _conda_verbosity_arg(self):
        if self.verbosity <= 0:
            return " -q"
        elif self.verbosity == 2:
            return " -v"
        elif self.verbosity == 3:
            return " -vv"
        elif self.verbosity >= 4:
            return " -vvv"
        else:
            return ""

    @property
    def _logging_filters(self):
        class NoEmptyLinesFilter(logging.Filter):
            # Replace any empty lines including lines only containing the
            # "cursor up" ANSI escape code
            def filter(self, record):
                return record.msg.replace("\x1b[A", "") != ""

        class OnlyFinalProgressbarFilter(logging.Filter):
            # Assume a progress bar line like
            # [some text]|[some text]|[progress bar characters]| [percentage complete]% [ansi escape codes]
            # Only include final 100% complete line
            progress_bar_re = re.compile(
                r"^(.+?)\|(.+?)\|[ \#0-9]+?\|[ ]{1,3}[0-9]{1,2}\%"
            )

            def filter(self, record):
                return not self.progress_bar_re.match(record.msg)

        logging_filters = [NoEmptyLinesFilter(), OnlyFinalProgressbarFilter()]

        return logging_filters

    @staticmethod
    def _map_log_level(msg):
        if (
            msg.startswith("DEBUG")
            or msg.startswith("VERBOSE")
            or msg.startswith("TRACE")
        ):
            return logging.DEBUG
        elif msg.startswith("INFO"):
            return logging.INFO
        elif msg.startswith("WARNING"):
            return logging.WARNING
        elif msg.startswith("ERROR"):
            return logging.ERROR
        elif msg.startswith("CRITICAL"):
            return logging.CRITICAL
        else:
            # If no prefix on message, assume its INFO level
            return logging.INFO
