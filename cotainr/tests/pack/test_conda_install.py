import pytest

from cotainr.pack import CondaInstall


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


@pytest.mark.singularity_integration  # TODO: parametrized with/without singularity
@pytest.mark.conda_integration
class TestBootstrap:
    # refactor to have all bootstrap code in private method
    def test_conda_installer_bootstrap(self):
        # conda installed
        # source environment
        # conda updated
        raise NotImplementedError("Test not implemented'")

@pytest.mark.singularity_integration
@pytest.mark.conda_integration
class TestAddEnvironment:
    def test_env_creation(self):
        raise NotImplementedError("Test not implemented'")


@pytest.mark.singularity_integration
@pytest.mark.conda_integration
class TestCleanupUnusedFiles:
    def test_all_unneeded_removed(self):
        # tarballs and ?
        raise NotImplementedError("Test not implemented'")
