"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import logging

import pytest

from cotainr.tracing import LogDispatcher, LogSettings


class TestConstructor:
    def test_attributes(self):
        def loc_level_func(msg):
            pass

        log_settings = LogSettings()
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=loc_level_func,
            log_settings=log_settings,
        )
        assert log_dispatcher.map_log_level is loc_level_func
        assert log_dispatcher.verbosity == log_settings.verbosity
        assert log_dispatcher.log_file_path == log_settings.log_file_path
        assert log_dispatcher.no_color == log_settings.no_color
        assert log_dispatcher.logger_stdout.name == "test_dispatcher_6021.out"
        assert log_dispatcher.logger_stderr.name == "test_dispatcher_6021.err"


class TestLogToStderr:
    @pytest.mark.parametrize(
        "level",
        [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL],
    )
    def test_log_to_correct_level(self, level, caplog):
        def loc_level_func(msg):
            return level

        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=loc_level_func,
            log_settings=LogSettings(verbosity=3, log_file_path=None, no_color=True),
        )
        log_dispatcher.log_to_stderr("test_6021")
        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == level
        assert caplog.records[0].name == "test_dispatcher_6021.err"
        assert caplog.records[0].msg == "test_6021"

    def test_strip_whitespace(self, caplog):
        def loc_level_func(msg):
            return logging.INFO

        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=loc_level_func,
            log_settings=LogSettings(verbosity=1, log_file_path=None, no_color=True),
        )
        for msg in ["  before", "after  ", "  before and after  "]:
            log_dispatcher.log_to_stderr(msg=msg)

        assert len(caplog.records) == 3
        assert all(rec.name == "test_dispatcher_6021.err" for rec in caplog.records)
        assert caplog.records[0].msg == "before"
        assert caplog.records[1].msg == "after"
        assert caplog.records[2].msg == "before and after"


class TestLogToStdout:
    @pytest.mark.parametrize(
        "level",
        [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL],
    )
    def test_log_to_correct_level(self, level, caplog):
        def loc_level_func(msg):
            return level

        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=loc_level_func,
            log_settings=LogSettings(verbosity=3, log_file_path=None, no_color=True),
        )
        log_dispatcher.log_to_stdout("test_6021")
        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == level
        assert caplog.records[0].name == "test_dispatcher_6021.out"
        assert caplog.records[0].msg == "test_6021"

    def test_strip_whitespace(self, caplog):
        def loc_level_func(msg):
            return logging.INFO

        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=loc_level_func,
            log_settings=LogSettings(verbosity=1, log_file_path=None, no_color=True),
        )
        for msg in ["  before", "after  ", "  before and after  "]:
            log_dispatcher.log_to_stdout(msg=msg)

        assert len(caplog.records) == 3
        assert all(rec.name == "test_dispatcher_6021.out" for rec in caplog.records)
        assert caplog.records[0].msg == "before"
        assert caplog.records[1].msg == "after"
        assert caplog.records[2].msg == "before and after"
