import pytest

import cotainr.pack


@pytest.fixture
def patch_disable_conda_install_bootstrap_conda(monkeypatch):
    """
    Disable CondaInstall._bootstrap_conda(...).

    The conda bootstrap method is replaced by a mock that prints and returns a
    message about the conda bootstrap that would have happened.

    """

    def mock_bootstrap_conda(self, *, installer_path):
        msg = f"PATCH: Bootstrapped Conda using {installer_path}"
        print(msg)
        return msg

    monkeypatch.setattr(
        cotainr.pack.CondaInstall, "_bootstrap_conda", mock_bootstrap_conda
    )


@pytest.fixture
def patch_disable_conda_install_download_conda_installer(monkeypatch):
    """
    Disable CondaInstall._download_conda_installer(...).

    The installer download is replaced by a method that, in place of the
    installer, creates a file containing a line saying that this is where the
    installer would have been downloaded to.
    """

    def mock_download_conda_installer(self, *, path):
        path.write_text("Conda installer downloaded to this file")
        assert path.exists()

    monkeypatch.setattr(
        cotainr.pack.CondaInstall,
        "_download_conda_installer",
        mock_download_conda_installer,
    )
