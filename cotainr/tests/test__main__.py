"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

from pathlib import Path
import subprocess
import sys

import pytest

import cotainr

from .cli.patches import patch_disable_main


class Test__main__:
    def test_programmatic_import_run(self, patch_disable_main):
        with pytest.raises(SystemExit, match="^PATCH: Ran cotainr.cli main function$"):
            from cotainr import __main__

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
