"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import logging

import pytest

from cotainr.tracing import ColoredOutputFormatter


class TestClassAttributes:
    def test_log_level_fg_colors(self):
        assert hasattr(ColoredOutputFormatter, "log_level_fg_colors")
        assert isinstance(ColoredOutputFormatter.log_level_fg_colors, dict)
        for log_level in [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]:
            assert log_level in ColoredOutputFormatter.log_level_fg_colors

    def test_reset_color(self):
        assert hasattr(ColoredOutputFormatter, "reset_color")
        assert ColoredOutputFormatter.reset_color == "\x1b[0m"


class TestFormat:
    @pytest.mark.parametrize(
        ["level", "msg", "color_msg"],
        [
            (logging.DEBUG, "test_debug", "\x1b[38;5;8mtest_debug\x1b[0m"),
            (logging.INFO, "test_info", "test_info"),
            (logging.WARNING, "test_warning", "\x1b[38;5;3mtest_warning\x1b[0m"),
            (logging.ERROR, "test_error", "\x1b[38;5;1mtest_error\x1b[0m"),
            (logging.CRITICAL, "test_critical", "\x1b[38;5;160mtest_critical\x1b[0m"),
        ],
    )
    def test_correct_formatting(self, level, msg, color_msg):
        formatter = ColoredOutputFormatter()
        rec = logging.LogRecord(
            name="test",
            level=level,
            pathname="test_path",
            lineno=0,
            msg=msg,
            args=None,
            exc_info=None,
        )
        assert formatter.format(rec) == color_msg

    def test_original_record_unchanged(self):
        formatter = ColoredOutputFormatter()
        rec = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test_path",
            lineno=0,
            msg="test_msg",
            args=None,
            exc_info=None,
        )
        msg = formatter.format(rec)
        assert msg is not rec.msg
        assert rec.msg == "test_msg"
