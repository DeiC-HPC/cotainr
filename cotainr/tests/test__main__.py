from pathlib import Path
import subprocess
import sys

import pytest

from .cli.patches import patch_disable_main
import cotainr


class Test__main__:
    def test_programmatic_import_run(self, patch_disable_main):
        with pytest.raises(SystemExit) as exc_info:
            from cotainr import __main__
        exc_msg = str(exc_info.value)
        assert exc_msg == "PATCH: Ran cotainr.cli main function"

    def test_cli_m_flag(self):
        env = {
            # cotainr is not importable anymore when the safedir fixture changes
            # the working directory during the test invocation.
            "PYTHONPATH": f"{Path(cotainr.__file__).parent.parent}"
        }
        process = subprocess.run(
            [sys.executable, "-m", "cotainr"],
            capture_output=True,
            check=True,
            text=True,
            env=env,
        )
        assert process.stdout.startswith("usage: cotainr [-h]")
