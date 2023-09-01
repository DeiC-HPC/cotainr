"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import re
import subprocess
import urllib.error

import pytest

from cotainr.container import SingularitySandbox
from cotainr.pack import CondaInstall
from .patches import (
    patch_disable_conda_install_bootstrap_conda,
    patch_disable_conda_install_download_miniforge_installer,
)
from .stubs import StubEmptyLicensePopen, StubShowLicensePopen
from ..container.data import data_cached_ubuntu_sif
from ..container.patches import patch_disable_singularity_sandbox_subprocess_runner


class TestConstructor:
    def test_attributes(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
        assert conda_install.sandbox == sandbox
        assert conda_install.prefix == "/opt/conda"
        assert conda_install.license_accepted

    def test_beforehand_license_acceptance(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            CondaInstall(sandbox=sandbox, license_accepted=True)

        # Check that the message about accepting Miniforge license on
        # beforehand is shown
        (
            _sandbox_create_cmd,
            miniforge_license_accept_cmd,
            _conda_bootstrap_cmd,
            _conda_bootstrap_clean_cmd,
        ) = (
            capsys.readouterr().out.strip().split("\n")
        )
        assert miniforge_license_accept_cmd == (
            "You have accepted the Miniforge installer license via the command line option "
            "'--accept-licenses'."
        )

    def test_cleanup(
        self,
        capsys,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)

            # Check that installer was removed after use
            assert not (
                conda_install.sandbox.sandbox_dir / "conda_installer.sh"
            ).exists()

        (
            _sandbox_create_cmd,
            _miniforge_license_accept_cmd,
            bootstrap_cmd,
            clean_cmd,
            _,
        ) = capsys.readouterr().out.split("\n")

        # Check that installer (mock) was created in the first place
        assert bootstrap_cmd.startswith("PATCH: Bootstrapped Conda using ")
        assert bootstrap_cmd.endswith("conda_installer.sh")

        # Check that the conda clean (mock) command ran
        assert clean_cmd.startswith("PATCH: Ran command in sandbox:")
        assert "'conda', 'clean', '-y', '-a'" in clean_cmd


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
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            conda_install.add_environment(path=conda_env_path, name=conda_env_name)
            process = sandbox.run_command_in_container(cmd="conda info -e")
            assert re.search(
                # We expect to find a line in the list of environments similar to:
                # some_env_name_6021         /opt/conda/envs/some_env_name_6021
                rf"^{conda_env_name}(\s)+/opt/conda/envs/{conda_env_name}$",
                process.stdout,
                flags=re.MULTILINE,
            )

    def test_other_conda_channels_than_condaforge(
        self, tmp_path, data_cached_ubuntu_sif
    ):
        conda_env_path = tmp_path / "conda_env.yml"
        conda_env_path.write_text(
            "channels:\n  - bioconda\ndependencies:\n  - samtools"
        )
        conda_env_name = "some_bioconda_env_6021"
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            conda_install.add_environment(path=conda_env_path, name=conda_env_name)
            process = sandbox.run_command_in_container(cmd="conda info -e")
            assert re.search(
                # We expect to find a line in the list of environments similar to:
                # some_env_name_6021         /opt/conda/envs/some_env_name_6021
                rf"^{conda_env_name}(\s)+/opt/conda/envs/{conda_env_name}$",
                process.stdout,
                flags=re.MULTILINE,
            )


@pytest.mark.conda_integration
@pytest.mark.singularity_integration
class TestCleanupUnusedFiles:
    def test_all_unneeded_removed(self, data_cached_ubuntu_sif):
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            CondaInstall(sandbox=sandbox, license_accepted=True)
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
            CondaInstall(sandbox=sandbox, license_accepted=True)

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
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
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


class Test_DisplayMiniforgeLicenseForAcceptance:
    def test_acccepting_license(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr(subprocess, "Popen", StubShowLicensePopen)
        monkeypatch.setattr("builtins.input", lambda: "yes")
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)

        stdout_lines = capsys.readouterr().out.strip().split("\n")
        assert "You have accepted the Miniforge installer license." in stdout_lines
        assert conda_install.license_accepted

    @pytest.mark.parametrize("answer", ["n", "N", "", "some_answer_6021"])
    def test_not_accepting_license(
        self,
        answer,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr(subprocess, "Popen", StubShowLicensePopen)
        monkeypatch.setattr("builtins.input", lambda: answer)
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            with pytest.raises(SystemExit):
                CondaInstall(sandbox=sandbox)

        stdout_lines = capsys.readouterr().out.strip().split("\n")
        assert (
            "You have not accepted the Miniforge installer license. Aborting!"
        ) in stdout_lines

    def test_installer_not_showing_license(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        monkeypatch,
    ):
        monkeypatch.setattr(subprocess, "Popen", StubEmptyLicensePopen)
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            with pytest.raises(
                RuntimeError,
                match="^No license seems to be displayed by the Miniforge installer.$",
            ):
                CondaInstall(sandbox=sandbox)

    def test_license_interaction_handling(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr(subprocess, "Popen", StubShowLicensePopen)
        monkeypatch.setattr("builtins.input", lambda: "yes")
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            CondaInstall(sandbox=sandbox)

        stdout = capsys.readouterr().out.strip()
        stdout_lines = stdout.split("\n")

        # Check that we send the "ENTER" and kill the process.
        assert "StubShowLicensePopen received: input='\\n'." in stdout_lines
        assert "StubShowLicensePopen killed." in stdout_lines

        # Check that the prompt for "ENTER" is not displayed to the user
        assert "Please, press ENTER to continue\n>>> " not in stdout

        # Check that the license is displayed to the user
        assert "STUB:\n\n\nThis is the license terms..." in stdout

    @pytest.mark.conda_integration
    def test_miniforge_still_showing_license(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr("builtins.input", lambda: "yes")
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)

        stdout = capsys.readouterr().out.strip()

        # Check that various lines that we expect to always be part of
        # https://github.com/conda-forge/miniforge/blob/main/LICENSE are still
        # shown to the user when extracting and showing the Miniforge license
        # terms from the installer - just to have an idea that the license is
        # still being shown correctly to the user
        assert (
            "Miniforge installer code uses BSD-3-Clause license as stated below."
        ) in stdout
        assert (
            "Miniforge installer comes with a boostrapping executable that is used\n"
            "when installing miniforge and is deleted after miniforge is installed."
        ) in stdout
        assert "conda-forge" in stdout
        assert "All rights reserved." in stdout


class Test_DownloadCondaInstaller:
    def test_installer_download_success(
        self,
        patch_urllib_urlopen_as_bytes_stream,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            conda_installer_path = (
                conda_install.sandbox.sandbox_dir / "conda_installer_download"
            )
            conda_install._download_miniforge_installer(
                installer_path=conda_installer_path
            )
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
