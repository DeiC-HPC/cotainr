import pytest
from pathlib import Path

import cotainr.system


@pytest.fixture
def patch_empty_system(monkeypatch):
    """
    Change filename in SystemData to an empty file
    """
    monkeypatch.setattr(
        cotainr.system.SystemData,
        "systems_file",
        (Path(__file__) / "../systems_empty.json").resolve(),
    )


@pytest.fixture
def patch_system_with_actual_file(monkeypatch):
    """
    Change filename in SystemData to a file with 2 entries
    """
    print(Path(__file__))
    monkeypatch.setattr(
        cotainr.system.SystemData,
        "systems_file",
        (Path(__file__) / "../systems_2.json").resolve(),
    )


@pytest.fixture
def patch_system_with_non_existing_file(monkeypatch):
    """
    Change filename in SystemData to a non-existing file
    """
    monkeypatch.setattr(
        cotainr.system.SystemData, "systems_file", Path("/some_non_existing_file_6021")
    )
