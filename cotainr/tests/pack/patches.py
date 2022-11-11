import pytest

import cotainr.pack


@pytest.fixture
def patch_conda_install_bootstrap_conda(monkeypatch):
    def mock_bootstrap_conda(self, *, installer_path):
        msg = f"PATCH: Bootstrapped Conda using {installer_path}"
        print(msg)
        return msg

    monkeypatch.setattr(
        cotainr.pack.CondaInstall, "_bootstrap_conda", mock_bootstrap_conda
    )


@pytest.fixture
def patch_conda_install_download_conda_installer(monkeypatch):
    def mock_download_conda_installer(self, *, path):
        path.write_text("Conda installer downloaded to this file")
        assert path.exists()

    monkeypatch.setattr(
        cotainr.pack.CondaInstall,
        "_download_conda_installer",
        mock_download_conda_installer,
    )
