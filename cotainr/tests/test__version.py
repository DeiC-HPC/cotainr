"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

from importlib.metadata import PackageNotFoundError
import re
import types

import cotainr
import cotainr._version


class Test__get_hatch_version:
    def test_correct_dev_version_number(self):
        cotainr_calver_tag_pattern = r"20[0-9]{2}\.(0[1-9]|10|11|12)\.[0-9]+"
        dev_extension_pattern = r"(\.dev[0-9]+\+[a-z0-9]{8})?"
        local_version_pattern = r"(\.d20[0-9]{2}(0[1-9]|10|11|12)[0-9]{2})?"
        cotainr_dev_version_pattern = (
            r"^"
            + cotainr_calver_tag_pattern  # YYYY.MM.MINOR
            + dev_extension_pattern  # .devN+hash (optional)
            + local_version_pattern  # .dYYYYMMDD (optional)
            + r"$"
        )
        cotainr_dev_version = cotainr._version._get_hatch_version()
        assert re.match(cotainr_dev_version_pattern, cotainr_dev_version)
        assert (
            # If a hatch version is available, it should be the same as the cotainr version
            cotainr.__version__ == cotainr._version.__version__ == cotainr_dev_version
        )

    def test_hatchling_not_installed(self, context_importerror):
        with context_importerror("hatchling.metadata.core"):
            assert cotainr._version._get_hatch_version() is None

        with context_importerror("hatchling.plugin.manager"):
            assert cotainr._version._get_hatch_version() is None

    def test_no_vcs_version(self, monkeypatch):
        class StubDummyProjectMetadata:
            def __init__(self, *args, **kwargs):
                self.hatch = types.SimpleNamespace(version=types.SimpleNamespace())

        monkeypatch.setattr(
            "hatchling.metadata.core.ProjectMetadata", StubDummyProjectMetadata
        )
        assert cotainr._version._get_hatch_version() is None


class Test__get_importlib_metadata_version:
    def test_correct_version_number(self, monkeypatch):
        def mock_version(package):
            return "test_version_6021"

        monkeypatch.setattr("importlib.metadata.version", mock_version)
        assert cotainr._version._get_importlib_metadata_version() == "test_version_6021"

    def test_not_installed(self, monkeypatch):
        def mock_version(package):
            raise PackageNotFoundError

        monkeypatch.setattr("importlib.metadata.version", mock_version)
        assert cotainr._version._get_importlib_metadata_version() is None
