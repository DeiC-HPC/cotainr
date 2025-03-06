"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import contextlib
import importlib
import io
import logging
import os
from pathlib import Path
import shlex
import subprocess
import sys
import urllib.error
import urllib.request

import pytest


@pytest.fixture
def argparse_options_line():
    """
    Return the help text line for optional arguments in argparse.

    Apparently this line changed from "optional arguments" to "options" in Python 3.10.
    """
    py_ver = sys.version_info
    if py_ver.major > 3 or (py_ver.major == 3 and py_ver.minor >= 10):
        return "options:\n"
    else:
        return "optional arguments:\n"


@pytest.fixture(autouse=True)
def context_reload_logging():
    """
    Reset the internal state of the logging module on test teardown.

    Needed in tests of logging functionality where the tests end up affecting
    the internal state of the logging module.

    See https://stackoverflow.com/q/7460363 for more context.
    """
    yield
    importlib.reload(logging)


@pytest.fixture
def context_set_umask():
    """Return a context manager providing a context with the specified umask."""

    @contextlib.contextmanager
    def set_umask(umask):
        current_umask = None
        try:
            current_umask = os.umask(umask)
            yield
        finally:
            if current_umask is not None:
                os.umask(current_umask)

    return set_umask


@pytest.fixture
def data_log_level_names_mapping():
    """
    A mapping from log levels to their names.

    From Python 3.11 this mapping is also available as
    logging.getLevelNamesMapping().
    """
    level_names_mapping = {
        level: logging.getLevelName(level)
        for level in [
            logging.CRITICAL,
            logging.ERROR,
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
        ]
    }

    return level_names_mapping


@pytest.fixture
def factory_mock_input():
    """
    Create mock of the builtins `input` function that returns a fixed "input".

    Returns a factory for creating mocked versions of the builtin `input`
    function to be used with the `monkeypatch` fixture to replace
    `builtins.input` with a function that prints the prompt (its argument, if
    provided) and returns a "fixed user input", provided as argument to the
    factory.
    """

    def create_mock_input(fixed_user_input=None):
        def mock_input(prompt):
            print(prompt, end="")
            return fixed_user_input

        return mock_input

    return create_mock_input


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


@pytest.fixture
def patch_urllib_urlopen_force_fail(monkeypatch):
    """
    Force urllib.request.urlopen(...) to raise URLError.

    The `urlopen` contextmanager is replaced by a mock that always raises an
    `urllib.error.URLError` when entering the contextmanager.
    """

    @contextlib.contextmanager
    def mock_urlopen(url, *args, **kwargs):
        raise urllib.error.URLError(f"PATCH: urlopen error forced for {url=}")

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


@pytest.fixture
def singularity_inspect():
    """Provide a function wrapping a "singularity inspect" call."""
    return lambda container_path: subprocess.run(
        ["singularity", "inspect", container_path],
        capture_output=True,
        check=True,
        text=True,
    )
