"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import sys

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
def patch_disable_conda_install_display_miniforge_license_for_acceptance(monkeypatch):
    """
    Disable CondaInstall._display_miniforge_license_for_acceptance(...).

    The explicit request for an acceptance of the Miniforge license terms is
    replaced by a mock exits with a message about what would have happened.
    """

    def mock_display_miniforge_license_for_acceptance(self, *, installer_path):
        sys.exit("PATCH: Showing license terms for {installer_path}")

    monkeypatch.setattr(
        cotainr.pack.CondaInstall,
        "_display_miniforge_license_for_acceptance",
        mock_display_miniforge_license_for_acceptance,
    )


@pytest.fixture
def patch_disable_conda_install_download_miniforge_installer(monkeypatch):
    """
    Disable CondaInstall._download_minforge_installer(...).

    The installer download is replaced by a method that, in place of the
    installer, creates a file containing a line saying that this is where the
    installer would have been downloaded to.
    """

    def mock_download_miniforge_installer(self, *, installer_path):
        installer_path.write_text("Miniforge installer downloaded to this file")
        assert installer_path.exists()

    monkeypatch.setattr(
        cotainr.pack.CondaInstall,
        "_download_miniforge_installer",
        mock_download_miniforge_installer,
    )
