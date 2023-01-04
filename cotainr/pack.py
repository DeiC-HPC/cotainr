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

from pathlib import Path
import time
import random
import urllib.error
import urllib.request


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

    def __init__(self, *, sandbox, prefix="/opt/conda"):
        """Bootstrap a conda installation."""
        self.sandbox = sandbox
        self.prefix = prefix

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
        self.sandbox.run_command_in_container(
            cmd=f"conda env create -f {path} -n {name}"
        )

    def cleanup_unused_files(self):
        """
        Remove all unused Conda files.

        Equivalent to calling "conda clean -a".
        """
        self.sandbox.run_command_in_container(cmd="conda clean -y -a")

    def _bootstrap_conda(self, *, installer_path):
        """
        Install Conda and at its source script to the sandbox env.

        Parameters
        ----------
        installer_path : pathlib.Path
            The path of the Conda installer to run to bootstrap Conda.
        """
        # Run Conda installer
        self.sandbox.run_command_in_container(
            cmd=f"bash {installer_path.name} -b -s -p {self.prefix}"
        )

        # Add Conda to container sandbox env
        self.sandbox.add_to_env(
            shell_script=f"source {self.prefix + '/etc/profile.d/conda.sh'}"
        )

        # Check that we correctly use the newly installed Conda from now on
        self._check_conda_bootstrap_integrity()

        # Update the installed Conda package manager to the latest version
        self.sandbox.run_command_in_container(
            cmd="conda update -y -n base -c conda-forge conda"
        )

    def _check_conda_bootstrap_integrity(self):
        """Raise RuntimeError if multiple interfering Conda installs are found."""
        source_check_process = self.sandbox.run_command_in_container(
            cmd="conda info --base"
        )
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
