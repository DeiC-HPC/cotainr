import pytest

import cotainr.util


@pytest.fixture
def patch_stream_subprocess(monkeypatch):
    def mock_stream_subprocess(args, **kwargs):
        msg = f"PATCH: Streamed subprocess: {args=}, {kwargs=}"
        print(msg)
        return msg

    monkeypatch.setattr(cotainr.util, "stream_subprocess", mock_stream_subprocess)
