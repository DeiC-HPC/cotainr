"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pathlib

from cotainr.tracing import LogSettings


class TestConstructor:
    def test_correct_types_and_values(self):
        log_settings = LogSettings(
            verbosity=1, log_file_path="/some/path_6021", no_color=True
        )
        assert isinstance(log_settings.verbosity, int)
        assert log_settings.verbosity == 1
        assert isinstance(log_settings.log_file_path, pathlib.Path)
        assert log_settings.log_file_path.parent.as_posix() == "/some"
        assert log_settings.log_file_path.name == "path_6021"
        assert isinstance(log_settings.no_color, bool)
        assert log_settings.no_color

    def test_default_values(self):
        log_settings = LogSettings()
        assert log_settings.verbosity == 0
        assert log_settings.log_file_path is None
        assert not log_settings.no_color
