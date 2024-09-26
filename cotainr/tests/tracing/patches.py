"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import contextlib

import pytest

import cotainr.tracing

from .stubs import FixedNumberOfSpinsEvent


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


@pytest.fixture
def patch_fix_number_of_message_spins(spins, monkeypatch):
    """
    Force `cotainr.tracing.MessageSpinner` to update the spinning message
    exactly `spins` times before stopping.

    The `spin` parameter must be passed to the fixture using a pytest
    parameterization.
    """

    class FixedNumberOfSpinsMessageSpinner(cotainr.tracing.MessageSpinner):
        def __init__(self, *, msg, stream):
            super().__init__(msg=msg, stream=stream)
            self._stop_signal = FixedNumberOfSpinsEvent(spins=spins)

    monkeypatch.setattr(
        cotainr.tracing, "MessageSpinner", FixedNumberOfSpinsMessageSpinner
    )
