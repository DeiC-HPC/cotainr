import pytest

from cotainr.container import SingularitySandbox
from cotainr.pack import CondaInstall
from .integrations import integration_conda_singularity
from ..container.patches import patch_sandbox_run_command_in_container
from ..util.patches import patch_stream_subprocess


class TestConstructor:
    def test_attributes(self):
        raise NotImplementedError("Test not implemented'")

    def test_cleanup(self):
        # mock bootstrap
        # test remove installer script
        # test clean_up_unused_files ran
        raise NotImplementedError("Test not implemented'")


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
        self,
        patch_stream_subprocess,
    ):
        with SingularitySandbox(base_image="some_base.sif") as sandbox:
            sandbox.run_command_in_container(cmd="EPICCMD")
        # conda installed
        # source environment
        # conda updated
        raise NotImplementedError("Test not implemented'")


class Test_CheckCondaBootstrapIntegrity:
    def test_bail_on_interfering_conda_installs(self):
        # mock conda installer download
        # mock bootstrap
        # test source_check_porcess stdout
        raise NotImplementedError("Test not implemented'")

    def test_continue_on_single_conda_install(self):
        # mock conda installer download
        # mock bootstrap
        # test source_check_porcess stdout
        raise NotImplementedError("Test not implemented'")


class Test_DownloadCondaInstaller:
    def test_installer_download_success(self):
        # mock urllib.request.urlopen
        # test write of bytes
        raise NotImplementedError("Test not implemented'")

    def test_installer_download_fail(self):
        # mock urllib.request.urlopen
        # test exception handling
        # maybe retry handling
        raise NotImplementedError("Test not implemented'")
