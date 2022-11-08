import pytest

import cotainr.util


@pytest.fixture
def patch_stream_subprocess(monkeypatch):
    def mock_stream_subprocess(args, **kwargs):
        print(f"Streamed subprocess: {args=}, {kwargs=}")

    monkeypatch.setattr(cotainr.util, "stream_subprocess", mock_stream_subprocess)
