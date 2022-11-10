import os
from pathlib import Path
import shlex
import subprocess

import pytest


@pytest.fixture
def singularity_exec():
    """Provide a function wrapping a "singularity exec" call."""

    def _singularity_exec(cmd):
        singularity_process = subprocess.run(
            ["singularity", "exec", *shlex.split(cmd)],
            capture_output=True,
            check=True,
            text=True,
        )

        return singularity_process

    return _singularity_exec


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
