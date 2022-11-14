import contextlib
import io
import os
from pathlib import Path
import shlex
import subprocess
import urllib.request

import pytest


@pytest.fixture
def patch_urllib_urlopen_as_bytes_stream(monkeypatch):
    """
    Disable urllib.request.urlopen(...).

    The `urlopen` contextmanager is replaced by a mock that returns a bytes
    message about the URL content that would have been opened.
    """

    @contextlib.contextmanager
    def mock_urlopen(url, *args, **kwargs):
        yield io.BytesIO(f"PATCH: Bytes returned by urlopen for {url=}".encode())

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)


@pytest.fixture(autouse=True)
def safedir(tmp_path):
    """
    Force test to be run in a temporary directory.

    A lot of the functionality in cotainr manipulates directories. In order to
    provide some protection against messing up the current working directory by
    running a test, we force all tests to run from a temporary directory by
    making this an "autouse" fixture.
    """
    origin = Path().resolve()
    safe_dir = tmp_path / "safe_dir"
    safe_dir.mkdir()
    os.chdir(safe_dir)
    yield
    os.chdir(origin)


@pytest.fixture
def singularity_exec():
    """
    Provide a function wrapping a "singularity exec" call.

    The function returned by this fixture provides a shorthand to run
    "singularity exec {cmd}" as a python subprocess.
    """

    def _singularity_exec(cmd):
        singularity_process = subprocess.run(
            ["singularity", "exec", *shlex.split(cmd)],
            capture_output=True,
            check=True,
            text=True,
        )

        return singularity_process

    return _singularity_exec
