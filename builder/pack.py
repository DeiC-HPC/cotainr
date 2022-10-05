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
        self.install_dir = self.install_root / self.prefix.lstrip("/")

        # Set Conda bootstrap variables
        #    At container runtime
        self._conda_runtime_source_script = (
            self.prefix + "/etc/profile.d/conda.sh"
        )
        self.conda_runtime_bootstrap_script = (
            f"source {shlex.quote(self._conda_runtime_source_script)}"
        )
        #    During installation / container build
        self._conda_install_source_script = (
            self.install_dir / "etc/profile.d/conda.sh"
        ).as_posix()
        self._conda_install_bootstrap_source = (
            f"source {shlex.quote(self._conda_install_source_script)};"
        )
        #TODO: Needs conda-pack...

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
                f"bash {shlex.quote(str(conda_installer_path))} -b -s"
                f"-p {shlex.quote(str(self.install_dir))}"
            ),
            shell=True,
        )

        # Check that we correctly use the newly installed Conda from now on
        source_check_process = self.run_command("conda info --base")
        if source_check_process.stdout.strip() != f"{self.install_dir}":

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
            f"{self._conda_install_bootstrap_source} {conda_cmd}",
            shell=True,
            executable=shutil.which("bash"),
        )
        return process

    def cleanup_unused_files(self):
        self.run_command("conda clean -y -a")
