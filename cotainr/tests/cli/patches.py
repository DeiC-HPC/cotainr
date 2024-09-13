"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest

import cotainr.cli


@pytest.fixture
def patch_disable_main(monkeypatch):
    """
    Disable main.

    Replace the `main` cli function with a function that prints and returns a
    message about the execution of the main function that would have run.
    """

    def mock_main(*args, **kwargs):
        msg = "PATCH: Ran cotainr.cli main function"
        print(msg)
        return msg

    monkeypatch.setattr(cotainr.cli, "main", mock_main)


@pytest.fixture
def patch_disable_cotainrcli_init(monkeypatch):
    """
    Make the construction of the CotainrCLI a no-op.
    """

    def mock_init(self, *, args=None):
        pass

    monkeypatch.setattr(cotainr.cli.CotainrCLI, "__init__", mock_init)


@pytest.fixture
def patch_disables_cotainrcli_setup_cotainr_cli_logging(monkeypatch):
    """
    Disable the setup of the logging machinery for the cotainr CLI.

    Replaces the `CotainrCLI._setup_cotainr_cli_logging` method with a method
    that just prints and returns the `tracing.LogSettings` object provided to
    it as an argument.
    """

    def mock_setup_cotainr_cli_logging(self, *, log_settings):
        print(log_settings)
        return log_settings

    monkeypatch.setattr(
        cotainr.cli.CotainrCLI,
        "_setup_cotainr_cli_logging",
        mock_setup_cotainr_cli_logging,
    )
