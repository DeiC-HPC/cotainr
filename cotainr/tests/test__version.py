"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

from importlib.metadata import PackageNotFoundError
from pathlib import Path
import re
import types

import tomllib

import cotainr
import cotainr._version
from cotainr._version import (
    _determine_cotainr_version,
    _get_hatch_version,
    _get_importlib_metadata_version,
)


class Test__determine_cotainr_version:
    def test_hatch_vcs_based_version(self, monkeypatch):
        def mock_get_hatch_version():
            return "test_version_6021"

        monkeypatch.setattr(
            cotainr._version, "_get_hatch_version", mock_get_hatch_version
        )
        assert _determine_cotainr_version() == "test_version_6021"

    def test_importlib_metadata_based_version(self, monkeypatch):
        def mock_get_hatch_version():
            return None

        def mock_get_importlib_metadata_version():
            return "test_version_6021"

        monkeypatch.setattr(
            cotainr._version, "_get_hatch_version", mock_get_hatch_version
        )
        monkeypatch.setattr(
            cotainr._version,
            "_get_importlib_metadata_version",
            mock_get_importlib_metadata_version,
        )

        assert _determine_cotainr_version() == "test_version_6021"

    def test_unknown_version(self, monkeypatch):
        def mock_get_hatch_version():
            return None

        def mock_get_importlib_metadata_version():
            return None

        monkeypatch.setattr(
            cotainr._version, "_get_hatch_version", mock_get_hatch_version
        )
        monkeypatch.setattr(
            cotainr._version,
            "_get_importlib_metadata_version",
            mock_get_importlib_metadata_version,
        )

        assert _determine_cotainr_version() == "<unknown version>"


class Test__get_hatch_version:
    def test_correct_dev_version_number(self):
        pyproject_toml = (
            (Path(__file__) / "../../../pyproject.toml").resolve().read_text()
        )
        cotainr_calver_tag_pattern = (
            rf"{tomllib.loads(pyproject_toml)['tool']['hatch']['version']['tag-pattern']}"
        )[:-2]  # Remove training "$)"
        dev_extension_pattern = r"(\.dev[0-9]+\+g[a-z0-9]{7})?"
        local_version_pattern = r"(\.d20[0-9]{2}(0[1-9]|10|11|12)[0-9]{2})?"
        cotainr_dev_version_pattern = (
            cotainr_calver_tag_pattern  # YYYY.MM.MICRO
            + dev_extension_pattern  # .devN+ghash (optional)
            + local_version_pattern  # .dYYYYMMDD (optional)
            + r"$)"  # Add in trailing "$)" again
        )
        cotainr_dev_version = _get_hatch_version()
        assert re.match(cotainr_dev_version_pattern, cotainr_dev_version)
        assert (
            # If the hatch based version is available (which it should be when
            # running these tests), that version should be the same as the
            # cotainr version
            cotainr.__version__ == cotainr._version.__version__ == cotainr_dev_version
        )

    def test_hatchling_not_installed(self, context_importerror):
        with context_importerror("hatchling.metadata.core"):
            assert _get_hatch_version() is None

        with context_importerror("hatchling.plugin.manager"):
            assert _get_hatch_version() is None

    def test_no_vcs_version(self, monkeypatch):
        class StubDummyProjectMetadata:
            def __init__(self, *args, **kwargs):
                self.hatch = types.SimpleNamespace(version=types.SimpleNamespace())

        monkeypatch.setattr(
            "hatchling.metadata.core.ProjectMetadata", StubDummyProjectMetadata
        )
        assert _get_hatch_version() is None


class Test__get_importlib_metadata_version:
    def test_correct_version_number(self, monkeypatch):
        def mock_version(package):
            return "test_version_6021"

        monkeypatch.setattr("importlib.metadata.version", mock_version)
        assert _get_importlib_metadata_version() == "test_version_6021"

    def test_not_installed(self, monkeypatch):
        def mock_version(package):
            raise PackageNotFoundError

        monkeypatch.setattr("importlib.metadata.version", mock_version)
        assert _get_importlib_metadata_version() is None
