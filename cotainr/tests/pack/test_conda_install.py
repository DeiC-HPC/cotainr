"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import re
import urllib.error

import pytest

from cotainr.container import SingularitySandbox
from cotainr.pack import CondaInstall
from .patches import (
    patch_disable_conda_install_bootstrap_conda,
    patch_disable_conda_install_download_conda_installer,
)
from ..container.data import data_cached_ubuntu_sif
from ..container.patches import patch_disable_singularity_sandbox_subprocess_runner


class TestConstructor:
    def test_attributes(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_conda_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)
        assert conda_install.sandbox == sandbox
        assert conda_install.prefix == "/opt/conda"

    def test_cleanup(
        self,
        capsys,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_conda_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)

            # Check that installer was removed after use
            assert not (
                conda_install.sandbox.sandbox_dir / "conda_installer.sh"
            ).exists()

        _, bootstrap_out, clean_out, _ = capsys.readouterr().out.split("\n")

        # Check that installer (mock) was created in the first place
        assert bootstrap_out.startswith("PATCH: Bootstrapped Conda using ")
        assert bootstrap_out.endswith("conda_installer.sh")

        # Check that the conda clean (mock) command ran
        assert clean_out.startswith("PATCH: Ran command in sandbox:")
        assert "'conda', 'clean', '-y', '-a'" in clean_out


@pytest.mark.conda_integration
@pytest.mark.singularity_integration
class TestAddEnvironment:
    def test_env_creation(self, tmp_path, data_cached_ubuntu_sif):
        conda_env_path = tmp_path / "conda_env.yml"
        conda_env_path.write_text(
            "channels:\n  - conda-forge\ndependencies:\n  - python"
        )
        conda_env_name = "some_env_name_6021"
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)
            conda_install.add_environment(path=conda_env_path, name=conda_env_name)
            process = sandbox.run_command_in_container(cmd="conda info -e")
            assert re.search(
                rf"^{conda_env_name}(\s)+/opt/conda/envs/{conda_env_name}$",
                process.stdout,
                flags=re.MULTILINE,
            )


@pytest.mark.conda_integration
@pytest.mark.singularity_integration
class TestCleanupUnusedFiles:
    def test_all_unneeded_removed(self, data_cached_ubuntu_sif):
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            CondaInstall(sandbox=sandbox)
            process = sandbox.run_command_in_container(cmd="conda clean -d -a")
            clean_msg = "\n".join(
                [
                    "There are no unused tarball(s) to remove.",
                    "There are no index cache(s) to remove.",
                    "There are no unused package(s) to remove.",
                    "There are no tempfile(s) to remove.",
                    "There are no logfile(s) to remove.",
                ]
            )
            assert process.stdout.strip() == clean_msg


@pytest.mark.conda_integration
@pytest.mark.singularity_integration
class Test_BootstrapConda:
    def test_correct_conda_installer_bootstrap(self, data_cached_ubuntu_sif):
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            conda_install_dir = sandbox.sandbox_dir / "opt/conda"
            assert not conda_install_dir.exists()
            CondaInstall(sandbox=sandbox)

            # Check that conda has been installed
            assert conda_install_dir.exists()

            # Check that we are using our installed conda
            process = sandbox.run_command_in_container(cmd="conda info --base")
            assert process.stdout.strip() == "/opt/conda"

            # Check that the installed conda is up-to-date
            process = sandbox.run_command_in_container(
                cmd="conda update -n base -d conda"
            )
            assert "# All requested packages already installed." in process.stdout


class Test_CheckCondaBootstrapIntegrity:
    def test_bail_on_interfering_conda_installs(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_conda_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)
            with pytest.raises(RuntimeError) as exc_info:
                # Abuse that the output of the mocked subprocess runner in the
                # sandbox is a line about the command run
                # - not the actual output of "conda info --base"
                conda_install._check_conda_bootstrap_integrity()

        exc_msg = str(exc_info.value)
        assert exc_msg.startswith(
            "Multiple Conda installs interfere. "
            "We risk destroying the Conda install in "
            "PATCH: Ran command in sandbox: "
        )
        assert exc_msg.endswith("Aborting!")
        assert "'conda', 'info', '--base'" in exc_msg


class Test_DownloadCondaInstaller:
    def test_installer_download_success(
        self,
        patch_urllib_urlopen_as_bytes_stream,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)
            conda_installer_path = (
                conda_install.sandbox.sandbox_dir / "conda_installer_download"
            )
            conda_install._download_conda_installer(path=conda_installer_path)
            assert conda_installer_path.read_bytes() == (
                b"PATCH: Bytes returned by urlopen for url="
                b"'https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh'"
            )

    def test_installer_download_fail(
        self,
        patch_urllib_urlopen_force_fail,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            with pytest.raises(
                urllib.error.URLError, match="PATCH: urlopen error forced for url="
            ):
                CondaInstall(sandbox=sandbox)
