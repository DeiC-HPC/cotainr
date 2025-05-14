"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import contextlib
from importlib.metadata import PackageNotFoundError
import re
import types

import pytest

import cotainr._version
from cotainr._version import (
    _get_cotainr_calver_tag_pattern,
    _get_hatch_version,
    _get_importlib_metadata_version,
)


class Test__get_cotainr_calver_tag_pattern:
    def test_extract_tag_pattern(self, monkeypatch):
        @contextlib.contextmanager
        def mock_open(*args, **kwargs):
            yield ["tag-pattern = test_pattern_6021"]

        monkeypatch.setattr("builtins.open", mock_open)
        assert _get_cotainr_calver_tag_pattern() == "test_pattern_6021"

    @pytest.mark.parametrize(
        ["tag_line", "tag_pattern"],
        [
            ("tag-pattern = test_pattern_6021 # comment", "test_pattern_6021"),
            ("tag-pattern = test_pattern_6021# comment", "test_pattern_6021"),
            ("tag-pattern = test_pattern_6021 #comment", "test_pattern_6021"),
            ("tag-pattern = test_pattern_6021#comment", "test_pattern_6021"),
        ],
    )
    def test_remove_comments(self, tag_line, tag_pattern, monkeypatch):
        @contextlib.contextmanager
        def mock_open(*args, **kwargs):
            yield [tag_line]

        monkeypatch.setattr("builtins.open", mock_open)
        assert _get_cotainr_calver_tag_pattern() == tag_pattern

    def test_strip_whitespace(self, monkeypatch):
        @contextlib.contextmanager
        def mock_open(*args, **kwargs):
            yield ["tag-pattern =    test_pattern_6021   "]

        monkeypatch.setattr("builtins.open", mock_open)
        assert _get_cotainr_calver_tag_pattern() == "test_pattern_6021"

    def test_remove_single_quotes(self, monkeypatch):
        @contextlib.contextmanager
        def mock_open(*args, **kwargs):
            yield ["tag-pattern = 'test_pattern_6021'"]

        monkeypatch.setattr("builtins.open", mock_open)
        assert _get_cotainr_calver_tag_pattern() == "test_pattern_6021"

    def test_unable_to_find_tag_pattern(self, monkeypatch):
        @contextlib.contextmanager
        def mock_open(*args, **kwargs):
            yield ["not a tag-pattern line"]

        monkeypatch.setattr("builtins.open", mock_open)
        with pytest.raises(RuntimeError):
            _get_cotainr_calver_tag_pattern()


class Test__get_hatch_version:
    def test_correct_dev_version_number(self):
        start_full_pattern = cotainr._version._get_cotainr_calver_tag_pattern()[
            :-2  # Remove trailing "$)"
        ]
        dev_extension_pattern = r"(\.dev[0-9]+\+g[a-z0-9]{7})?"
        local_version_pattern = r"(\.d20[0-9]{2}(0[1-9]|10|11|12)[0-9]{2})?"
        cotainr_dev_version_pattern = (
            start_full_pattern  # YYYY.MM.MICRO
            + dev_extension_pattern  # .devN+ghash (optional)
            + local_version_pattern  # .dYYYYMMDD (optional)
            + r"$)"  # Add in trailing "$)" back in
        )
        cotainr_dev_version = _get_hatch_version()
        assert re.match(cotainr_dev_version_pattern, cotainr_dev_version)
        assert (
            # If the hatch based version is available (which it should be when
            # running these tests), that version should be the same as the
            # cotainr version
            cotainr.__version__ == cotainr._version.__version__ == cotainr_dev_version
        )

    def test_installed_package(self):
        installed_file_path = "/foo/bar/site-packages/cotainr"
        assert _get_hatch_version(installed_file_path) is None

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
