import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def safedir(tmp_path):
    """
    Always safe guard tests by running in a temporary directory.

    A lot of the functionality in cotainr manipulates directories. In order to
    provide some protection against messing up the current working directory by
    running a test, we force all tests to run from a temporary directory.
    """
    origin = Path().resolve()
    safe_dir = tmp_path / "safe_dir"
    safe_dir.mkdir()
    os.chdir(safe_dir)
    yield
    os.chdir(origin)
