"""
Packaging for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Classes
-------
CondaInstall
    A Conda installation in a container sandbox.
"""

from pathlib import Path
import urllib.request


class CondaInstall:
    """
    A Conda installation in a container sandbox.

    Bootstraps a miniforge based Conda installation in a container sandbox.

    Parameters
    ----------
    sandbox : pack.SingularitySandbox
        The sandbox in which Conda should be installed.
    prefix : str
        The Conda prefix to use for the Conda install.

    Attributes
    ----------
    sandbox : pack.SingularitySandbox
        The sandbox in which Conda is installed.
    prefix : str
        The Conda prefix used for the Conda install.
    """

    def __init__(self, *, sandbox, prefix="/opt/conda"):
        self.sandbox = sandbox
        self.prefix = prefix

        # Download Conda installer
        conda_installer_url = (
            "https://github.com/conda-forge/miniforge/releases/latest/download/"
            "Miniforge3-Linux-x86_64.sh"
        )
        conda_installer_path = (
            Path(self.sandbox.sandbox_dir).absolute() / "conda_installer.sh"
        )
        with urllib.request.urlopen(conda_installer_url) as url:
            conda_installer_path.write_bytes(url.read())

        # Run Conda installer
        self.sandbox.run_command_in_container(
            cmd=f"bash {conda_installer_path.name} -b -s -p {self.prefix}"
        )

        # Add Conda to container sandbox env
        self.sandbox.add_to_env(
            shell_script=f"source {self.prefix + '/etc/profile.d/conda.sh'}"
        )

        # Check that we correctly use the newly installed Conda from now on
        source_check_process = self.sandbox.run_command_in_container(
            cmd="conda info --base"
        )
        if source_check_process.stdout.strip() != f"{self.prefix}":
            raise RuntimeError(
                "Multiple Conda installs interfere. "
                "We risk destroying the Conda install in "
                f"{source_check_process.stdout.strip()}. Aborting!"
            )

        # Update the installed Conda package manager to the latest version
        self.sandbox.run_command_in_container(
            cmd="conda update -y -n base -c conda-forge conda"
        )

        # Remove unneeded files
        conda_installer_path.unlink()
        self.cleanup_unused_files()

    def add_environment(self, *, path, name):
        """
        Add an exported Conda environment to the Conda install.

        Equivalent to calling "conda env create -f `path` -n `name`".

        Parameters
        ----------
        path : os.PathLike
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
