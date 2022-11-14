import pytest

import cotainr.util


@pytest.fixture
def patch_disable_stream_subprocess(monkeypatch):
    """
    Disable stream_subprocess(...).

    The `stream_subprocess` function is replaced by a mock that prints and
    returns a message about the process that would have been run.
    """

    def mock_stream_subprocess(args, **kwargs):
        msg = f"PATCH: Streamed subprocess: {args=}, {kwargs=}"
        print(msg)
        return msg

    monkeypatch.setattr(cotainr.util, "stream_subprocess", mock_stream_subprocess)
