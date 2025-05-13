"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import contextlib
from importlib.metadata import PackageNotFoundError
import logging
import re
import types

import pytest

import cotainr._version
from cotainr._version import (
    _determine_cotainr_version,
    _get_cotainr_calver_tag_pattern,
)


class Test__determine_cotainr_version:
    def test_hatch_correct_dev_version_number(self, caplog):
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
        with caplog.at_level(logging.DEBUG, logger="cotainr._version"):
            cotainr_version = _determine_cotainr_version()
        assert "Cotainr version number determined by hatch" in caplog.text
        assert re.match(cotainr_dev_version_pattern, cotainr_version)
        assert cotainr.__version__ == cotainr._version.__version__ == cotainr_version

    @pytest.mark.parametrize(
        "hatch_library", ["hatchling.metadata.core", "hatchling.plugin.manager"]
    )
    def test_hatch_graceful_hatchling_not_installed(
        self, hatch_library, caplog, context_importerror
    ):
        with context_importerror(hatch_library):
            with caplog.at_level(logging.DEBUG, logger="cotainr._version"):
                _determine_cotainr_version()
        assert (
            "Unable to determine cotainr version number from hatch, "
            "falling back to importlib.metadata."
        ) in caplog.text

    def test_hatch_graceful_no_vcs_version(self, caplog, monkeypatch):
        class StubDummyProjectMetadata:
            def __init__(self, *args, **kwargs):
                self.hatch = types.SimpleNamespace(version=types.SimpleNamespace())

        monkeypatch.setattr(
            "hatchling.metadata.core.ProjectMetadata", StubDummyProjectMetadata
        )
        with caplog.at_level(logging.DEBUG, logger="cotainr._version"):
            _determine_cotainr_version()

        assert (
            "Unable to determine cotainr version number from hatch, "
            "falling back to importlib.metadata."
        ) in caplog.text

    def test_importlib_fallback(self, caplog, monkeypatch, context_importerror):
        def mock_version(package):
            return "test_version_6021"

        monkeypatch.setattr("importlib.metadata.version", mock_version)

        with context_importerror("hatchling.metadata.core"):
            with caplog.at_level(logging.DEBUG, logger="cotainr._version"):
                cotainr_version = _determine_cotainr_version()

        assert cotainr_version == "test_version_6021"
        assert (
            "Unable to determine cotainr version number from hatch, "
            "falling back to importlib.metadata."
        ) in caplog.text
        assert "Cotainr version number determined by importlib.metadata" in caplog.text

    def test_give_up(self, caplog, monkeypatch, context_importerror):
        def mock_version(package):
            raise PackageNotFoundError

        monkeypatch.setattr("importlib.metadata.version", mock_version)

        with context_importerror("hatchling.metadata.core"):
            with caplog.at_level(logging.DEBUG, logger="cotainr._version"):
                cotainr_version = _determine_cotainr_version()

        assert cotainr_version == "<unknown version>"
        assert (
            "Unable to determine cotainr version number from hatch or importlib."
            in caplog.text
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
