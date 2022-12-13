import pytest
from pathlib import Path

import pathlib
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


@pytest.fixture
def patch_empty_system(monkeypatch):
    """
    Change filename in SystemData to an empty file
    """
    monkeypatch.setattr(pathlib.Path, "is_file", lambda _: True)
    monkeypatch.setattr(pathlib.Path, "read_text", lambda _: "{}")


@pytest.fixture
def patch_system_with_actual_file(monkeypatch):
    """
    Change filename in SystemData to a file with 2 entries
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
    Change filename in SystemData to a non-existing file
    """
    monkeypatch.setattr(
        cotainr.util, "systems_file", Path("/some_non_existing_file_6021")
    )


@pytest.fixture
def patch_system_with_badly_formatted_file(monkeypatch):
    """
    Change filename in SystemData to a file with 2 entries
    """
    monkeypatch.setattr(pathlib.Path, "is_file", lambda _: True)
    monkeypatch.setattr(
        pathlib.Path,
        "read_text",
        lambda _: '{"some_system_6021": {"some_variable_6021": "some_value_6021"}}',
    )
