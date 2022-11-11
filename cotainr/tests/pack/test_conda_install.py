import pytest

from cotainr.container import SingularitySandbox
from cotainr.pack import CondaInstall
from .integrations import integration_conda_singularity
from .patches import (
    patch_conda_install_bootstrap_conda,
    patch_conda_install_download_conda_installer,
)
from ..container.patches import patch_singularity_sandbox_subprocess_runner


class TestConstructor:
    def test_attributes(
        self,
        patch_conda_install_bootstrap_conda,
        patch_conda_install_download_conda_installer,
        patch_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)
        assert conda_install.sandbox == sandbox
        assert conda_install.prefix == "/opt/conda"

    def test_cleanup(
        self,
        capsys,
        patch_conda_install_bootstrap_conda,
        patch_conda_install_download_conda_installer,
        patch_singularity_sandbox_subprocess_runner,
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
        # assert clean_out == "MOCK: Ran command in container: conda clean -y -a"


@pytest.mark.usefixtures("integration_conda_singularity")
class TestAddEnvironment:
    def test_env_creation(self):
        # test environment name and content
        raise NotImplementedError("Test not implemented'")


@pytest.mark.usefixtures("integration_conda_singularity")
class TestCleanupUnusedFiles:
    def test_all_unneeded_removed(self):
        # tarballs and ?
        raise NotImplementedError("Test not implemented'")


@pytest.mark.usefixtures("integration_conda_singularity")
class Test_BootstrapConda:
    # refactor to have all bootstrap code in private method
    def test_conda_installer_bootstrap(
        self, patch_singularity_sandbox_subprocess_runner
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            sandbox.run_command_in_container(cmd="EPICCMD")
        # conda installed
        # source environment
        # conda updated
        raise NotImplementedError("Test not implemented'")


class Test_CheckCondaBootstrapIntegrity:
    def test_bail_on_interfering_conda_installs(
        self,
        patch_conda_install_bootstrap_conda,
        patch_conda_install_download_conda_installer,
        patch_singularity_sandbox_subprocess_runner,
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
        patch_conda_install_bootstrap_conda,
        patch_singularity_sandbox_subprocess_runner,
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

    def test_installer_download_fail(self):
        # mock urllib.request.urlopen
        # test exception handling
        # maybe retry handling
        raise NotImplementedError("Test not implemented'")
