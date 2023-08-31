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
import random
import subprocess
import sys
import time
import urllib.error
import urllib.request


class CondaInstall:
    """
    A Conda installation in a container sandbox.

    Bootstraps a Miniforge based Conda installation in a container sandbox. As
    part of the bootstrapping of Miniforge, the user must accept the `Miniforge
    license terms
    <https://github.com/conda-forge/miniforge/blob/main/LICENSE>`_.


    Parameters
    ----------
    sandbox : :class:`~cotainr.container.SingularitySandbox`
        The sandbox in which Conda should be installed.
    prefix : str
        The Conda prefix to use for the Conda install.
    license_accepted : bool, default=False
        The flag to indicate whether or not the user has already accepted the
        Miniforge license terms.

    Attributes
    ----------
    sandbox : :class:`~cotainr.container.SingularitySandbox`
        The sandbox in which Conda is installed.
    prefix : str
        The Conda prefix used for the Conda install.
    license_accepted : bool
        Whether or not the Miniforge license terms have been accepted.

    Notes
    -----
    When adding a Conda environment, it is the responsibility of the user of
    cotainr to make sure they have the necessary rights to use the Conda
    channels/repositories and packages specified in the Conda environment, e.g.
    if `using the default Anaconda repositories
    <https://www.anaconda.com/blog/anaconda-commercial-edition-faq>`_.
    """

    def __init__(self, *, sandbox, prefix="/opt/conda", license_accepted=False):
        """Bootstrap a conda installation."""
        self.sandbox = sandbox
        self.prefix = prefix
        self.license_accepted = license_accepted

        # Download Conda installer
        conda_installer_path = (
            Path(self.sandbox.sandbox_dir).resolve() / "conda_installer.sh"
        )
        self._download_miniforge_installer(installer_path=conda_installer_path)

        # Make sure the user has accepted the Miniforge installer license
        if not license_accepted:
            self._display_miniforge_license_for_acceptance(
                installer_path=conda_installer_path
            )
        else:
            print(
                "You have accepted the Miniforge installer license via the command line "
                "option '--accept-licenses'."
            )

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

    def _display_miniforge_license_for_acceptance(self, *, installer_path):
        """
        Extract and display Miniforge installer license for acceptance.

        Runs the Miniforge bootstrap installer to extract the license, displays
        it to the user, and prompts for acceptance of the license terms. Exits
        if the license terms are not accepted.

        Parameters
        ----------
        installer_path : pathlib.Path
            The path of the Miniforge installer to run to bootstrap Conda.

        Raises
        ------
        RuntimeError
            If unable to extract a license from the Miniforge installer.

        Notes
        -----
        This assumes that the Miniforge installer, as it is run, prompts the
        user for pressing ENTER to display the license, then displays the
        license and prompts the user to answer "yes" to accept the license
        terms.

        We try to "forward" this flow to the user by extracting the text shown
        when running the installer and pressing ENTER. We then prompt for a
        "yes" to the license terms.
        """
        with subprocess.Popen(
            ["bash", f"{installer_path.name}"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        ) as process:
            license, _ = process.communicate(
                # "press" ENTER to display the license and capture it
                "\n"
            )
            process.kill()  # We only use this process to extract the license

        if license:
            license = license.replace(
                # remove prompt for pressing enter (as we have already done this...)
                "Please, press ENTER to continue\n>>> ",
                "\n",
            )
            print(license)
            val = input()  # prompt user for acceptance of license terms
            if val != "yes":
                print(
                    "You have not accepted the Miniforge installer license. Aborting!"
                )
                sys.exit(0)

            self.license_accepted = True
            print("You have accepted the Miniforge installer license.")
        else:
            raise RuntimeError(
                "No license seems to be displayed by the Miniforge installer."
            )

    def _download_miniforge_installer(self, *, installer_path):
        """
        Download the Miniforge installer to `path`.

        Parameters
        ----------
        installer_path : pathlib.Path
            The path to download the conda installer to.
        """
        miniforge_installer_url = (
            "https://github.com/conda-forge/miniforge/releases/latest/download/"
            "Miniforge3-Linux-x86_64.sh"
        )

        # Make up to 3 attempts at downloading the installer
        for retry in range(3):
            try:
                with urllib.request.urlopen(
                    miniforge_installer_url
                ) as url:  # nosec B310
                    installer_path.write_bytes(url.read())

                break

            except urllib.error.URLError as e:
                url_error = e

                # Exponential back-off
                time.sleep(2**retry + random.uniform(0.001, 1))  # nosec B311

        else:
            raise url_error
