"""
Packaging for user space Apptainer/Singularity container builder.

Created by DeiC, deic.dk

Classes
-------
CondaInstall
"""

from pathlib import Path
import shlex
import shutil
import urllib.request

from util import stream_subprocess


class CondaInstall:
    def __init__(self, install_root, prefix="/opt/conda"):
        self.prefix = prefix
        self.install_root = Path(install_root).absolute()

        # Setup fakechroot vars
        # TODO: exclude everything but prefix parent... ?
        self._fakechroot_exclude_path = f"FAKECHROOT_EXCLUDE_PATH=/dev:/proc:/sys:{Path(shutil.which('bash')).parent}"
        self._fakechroot_cmd = (
            f"fakechroot chroot {shlex.quote(str(self.install_root))}"
        )

        # Set Conda bootstrap variables
        self._conda_source_script = self.prefix + "/etc/profile.d/conda.sh"
        self.conda_bootstrap_cmd = f"source {shlex.quote(self._conda_source_script)}"

        # Download Conda installer
        conda_installer_url = (
            "https://github.com/conda-forge/miniforge/releases/latest/download/"
            "Miniforge3-Linux-x86_64.sh"
        )
        conda_installer_path = self.install_root / "conda_installer.sh"
        with urllib.request.urlopen(conda_installer_url) as url:
            conda_installer_path.write_bytes(url.read())

        # Run Conda installer
        stream_subprocess(
            (
                f"{self._fakechroot_exclude_path} {self._fakechroot_cmd} "
                f"bash {shlex.quote(str(conda_installer_path.name))} -b -s "
                f"-p {shlex.quote(str(self.prefix))}"
            ),
            shell=True,
        )
        conda_installer_path.unlink()  # ... and remove the installer

        # Check that we correctly use the newly installed Conda from now on
        source_check_process = self.run_command("conda info --base")
        if source_check_process.stdout.strip() != f"{self.prefix}":

            raise RuntimeError(
                "Multiple local Conda installs interfere. "
                "We risk destroying the Conda install in "
                f"{source_check_process.strip()}. Aborting!"
            )

        # Update the installed Conda package manager to the latest version
        self.run_command("conda update -y -n base -c conda-forge conda")
        self.cleanup_unused_files()

    def run_command(self, conda_cmd):
        # TODO: Some sort of sanity check of `conda_cmd` is required
        process = stream_subprocess(
            (
                f"{self._fakechroot_exclude_path} {self._fakechroot_cmd} "
                f"bash -c '{self.conda_bootstrap_cmd}; {conda_cmd}'"
            ),
            shell=True,
        )
        return process

    def cleanup_unused_files(self):
        self.run_command("conda clean -y -a")
