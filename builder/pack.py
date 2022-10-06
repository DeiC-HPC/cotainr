"""
Packaging for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Classes
-------
CondaInstall
"""

from pathlib import Path
import urllib.request


class CondaInstall:
    def __init__(self, sandbox, prefix="/opt/conda"):
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
            f"bash {conda_installer_path.name} -b -s -p {self.prefix}"
        )

        # Add Conda to container sandbox env
        self.sandbox.add_to_env(f"source {self.prefix + '/etc/profile.d/conda.sh'}")

        # Check that we correctly use the newly installed Conda from now on
        source_check_process = self.sandbox.run_command_in_container(
            "conda info --base"
        )
        if source_check_process.stdout.strip() != f"{self.prefix}":
            raise RuntimeError(
                "Multiple Conda installs interfere. "
                "We risk destroying the Conda install in "
                f"{source_check_process.stdout.strip()}. Aborting!"
            )

        # Update the installed Conda package manager to the latest version
        self.sandbox.run_command_in_container(
            "conda update -y -n base -c conda-forge conda"
        )

        # Remove unneeded files
        conda_installer_path.unlink()
        self.cleanup_unused_files()

    def add_environment(self, env_file_path, name):
        self.sandbox.run_command_in_container(
            f"conda env create -f {env_file_path} -n {name}"
        )

    def cleanup_unused_files(self):
        self.sandbox.run_command_in_container("conda clean -y -a")
