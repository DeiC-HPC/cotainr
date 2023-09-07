"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""
import contextlib

import pytest

import cotainr.tracing


@pytest.fixture
def patch_disable_console_spinner(monkeypatch):
    """
    Disable the ConsoleSpinner() context.

    Replaces the console spinner context with a no-op context.
    """

    @contextlib.contextmanager
    def mock_console_spinner():
        yield

    monkeypatch.setattr(cotainr.tracing, "ConsoleSpinner", mock_console_spinner)
