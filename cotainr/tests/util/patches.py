"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pathlib
from pathlib import Path

import pytest

import cotainr.util


@pytest.fixture
def patch_disable_stream_subprocess(monkeypatch):
    """
    Disable stream_subprocess(...).

    The `stream_subprocess` function is replaced by a mock that prints to
    stdout, logs to stderr (if a log_dispatcher is provided), and returns a
    message about the process that would have been run.
    """

    def mock_stream_subprocess(*, args, log_dispatcher, **kwargs):
        msg = f"PATCH: Streamed subprocess: {args=}, {kwargs=}"
        if log_dispatcher is not None:
            log_dispatcher.log_to_stderr(msg)
        print(msg)
        return msg

    monkeypatch.setattr(cotainr.util, "stream_subprocess", mock_stream_subprocess)


@pytest.fixture
def patch_empty_system(monkeypatch):
    """
    Fake an empty JSON file.

    Used to patch `cotainr.util.systems_file` as empty.
    """
    monkeypatch.setattr(pathlib.Path, "is_file", lambda _: True)
    monkeypatch.setattr(pathlib.Path, "read_text", lambda _: "{}")


@pytest.fixture
def patch_system_with_actual_file(monkeypatch):
    """
    Fake a JSON file with 2 entries.

    Used to patch `cotainr.util.systems_file` with two entries.
    """
    monkeypatch.setattr(pathlib.Path, "is_file", lambda _: True)
    monkeypatch.setattr(
        pathlib.Path,
        "read_text",
        lambda _: """{
            "some_system_6021": {"base-image": "some_base_image_6021"},
            "another_system_6021": {"base-image": "another_base_image_6021"}
        }""",
    )


@pytest.fixture
def patch_system_with_non_existing_file(monkeypatch):
    """
    Set `cotainr.util.systems_file` to an empty path.
    """
    monkeypatch.setattr(
        cotainr.util, "systems_file", Path("/some_non_existing_file_6021")
    )


@pytest.fixture
def patch_system_with_badly_formatted_file(monkeypatch):
    """
    Fake a badly formatted JSON file.

    Used to patch `cotainr.util.systems_file` as badly formatted.
    """
    monkeypatch.setattr(pathlib.Path, "is_file", lambda _: True)
    monkeypatch.setattr(
        pathlib.Path,
        "read_text",
        lambda _: '{"some_system_6021": {"some_variable_6021": "some_value_6021"}}',
    )
