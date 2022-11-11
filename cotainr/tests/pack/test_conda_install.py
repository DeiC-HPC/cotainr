import pytest

import cotainr.container
from cotainr.pack import CondaInstall
from ..util.patches import patch_stream_subprocess
from ..container.patches import patch_sandbox_run_command_in_container


@pytest.fixture(
    params=[
        pytest.param("conda_only", marks=pytest.mark.conda_integration),
        pytest.param(
            "conda_and_singularity",
            marks=(pytest.mark.conda_integration, pytest.mark.singularity_integration),
        ),
    ]
)
def conda_singularity_integration(request):
    """
    Handle integration to conda and singularity.

    This fixture parameterize testing of integration to conda only and
    integration to conda and singularity at the same time.
    """
    if request.param == "conda_only":
        return request.getfixturevalue("patch_sandbox_run_command_in_container")


class TestConstructor:
    def test_attributes(self):
        raise NotImplementedError("Test not implemented'")

    def test_installer_download_fail(self):
        # refactor installer download to private method
        # mock urllib.request.urlopen
        # test exception handling
        # maybe retry handling
        raise NotImplementedError("Test not implemented'")

    def test_cleanup(self):
        # mock conda installer download
        # mock bootstrap
        # test remove installer script
        # test clean_up_unsed_files ran
        raise NotImplementedError("Test not implemented'")


class TestCheckCondaInstall:
    # refactor to have conda install check in private method
    def test_bail_on_interfering_conda_installs(self):
        # mock conda installer download
        # mock bootstrap
        # test source_check_porcess stdout
        raise NotImplementedError("Test not implemented'")


@pytest.mark.usefixtures("conda_singularity_integration")
class TestBootstrap:
    # refactor to have all bootstrap code in private method
    def test_conda_installer_bootstrap(
        self,
        patch_stream_subprocess,
    ):
        with cotainr.container.SingularitySandbox(
            base_image="some_base.sif"
        ) as sandbox:
            sandbox.run_command_in_container(cmd="EPICCMD")
        # conda installed
        # source environment
        # conda updated
        raise NotImplementedError("Test not implemented'")


@pytest.mark.usefixtures("conda_singularity_integration")
class TestAddEnvironment:
    def test_env_creation(self):
        raise NotImplementedError("Test not implemented'")



@pytest.mark.usefixtures("conda_singularity_integration")
class TestCleanupUnusedFiles:
    def test_all_unneeded_removed(self):
        # tarballs and ?
        raise NotImplementedError("Test not implemented'")
