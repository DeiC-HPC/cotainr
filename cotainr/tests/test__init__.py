"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import sys
from pathlib import Path

import pytest


class Test__init__:
    cotainr_path = Path(__file__).parents[2]
    min_py_ver = (cotainr_path/"cotainr/__init__.py").read_text()  # TODO

    @pytest.mark.skipif(
        sys.version_info > (3, 8), reason="only error early on too old Python version"
    )
    def test_error_early(self):
        # Intended to be run using: pytest -c /dev/null --noconftest
        #   --import-mode=importlib cotainr/tests/test__init__.py
        sys.path.insert(0, str(self.cotainr_path))  # Manually make cotainr importable
        print(self.min_py_ver)
        1/0
        with pytest.raises(SystemExit, match=r"^\033\[91mCotainr requires Python>=3.8"):
            import cotainr
            
