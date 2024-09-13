"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import itertools
import logging
import re

import pytest

from cotainr.tracing import LogDispatcher, LogSettings

from .data import (
    data_log_dispatcher_critical_color_log_messages,
    data_log_dispatcher_debug_color_log_messages,
    data_log_dispatcher_info_color_log_messages,
    data_log_dispatcher_info_no_color_log_messages,
    data_log_dispatcher_warning_color_log_messages,
)
from .stubs import AlwaysCompareFalse


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

    def test_adding_filters(self):
        # Define test filters
        class TestFilter1(logging.Filter):
            pass

        class TestFilter2(logging.Filter):
            pass

        filters = [TestFilter1(), TestFilter2()]

        # Setup the LogDispatcher
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: 0,  # not used in test since we log directly to loggers
            log_settings=LogSettings(),
            filters=filters,
        )
        for logger in [log_dispatcher.logger_stdout, log_dispatcher.logger_stderr]:
            for handler in logger.handlers:
                assert len(handler.filters) == 2
                for handler_filter, test_filter in zip(handler.filters, filters):
                    assert handler_filter is test_filter

    @pytest.mark.parametrize("verbosity", [-1, -2, -3, -5, -1000])
    def test_log_dispatcher_critical_logging(
        self,
        verbosity,
        capsys,
        data_log_dispatcher_critical_color_log_messages,
    ):
        (
            logger_name,
            log_level_msgs,
            stdout_msgs,
            stderr_msgs,
        ) = data_log_dispatcher_critical_color_log_messages

        # Setup the LogDispatcher
        log_dispatcher = LogDispatcher(
            name=logger_name,
            map_log_level_func=lambda msg: 0,  # not used in test since we log directly to loggers
            log_settings=LogSettings(
                verbosity=verbosity, log_file_path=None, no_color=False
            ),
        )
        assert f"{logger_name}.out" in logging.Logger.manager.loggerDict
        assert f"{logger_name}.err" in logging.Logger.manager.loggerDict

        # Log test messages to log dispatcher loggers
        for logger in [log_dispatcher.logger_stdout, log_dispatcher.logger_stderr]:
            # Log messages
            for level, msg in log_level_msgs.items():
                logger.log(level=level, msg=msg)

            # Check correct log level
            assert logger.getEffectiveLevel() == logging.CRITICAL

            # Check correct handles
            # Pytest manipulates the handler streams to capture the logging output
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        assert stdout.rstrip("\n").split("\n") == stdout_msgs
        assert stderr.rstrip("\n").split("\n") == stderr_msgs

    @pytest.mark.parametrize("verbosity", [3, 4, 5, 1000])
    def test_log_dispatcher_debug_logging(
        self,
        verbosity,
        capsys,
        data_log_dispatcher_debug_color_log_messages,
    ):
        (
            logger_name,
            log_level_msgs,
            expected_stdout_msgs,
            expected_stderr_msgs,
        ) = data_log_dispatcher_debug_color_log_messages

        # Setup the LogDispatcher
        log_dispatcher = LogDispatcher(
            name=logger_name,
            map_log_level_func=lambda msg: 0,  # not used in test since we log directly to loggers
            log_settings=LogSettings(
                verbosity=verbosity, log_file_path=None, no_color=False
            ),
        )
        assert f"{logger_name}.out" in logging.Logger.manager.loggerDict
        assert f"{logger_name}.err" in logging.Logger.manager.loggerDict

        # Log test messages to log dispatcher loggers
        for logger in [log_dispatcher.logger_stdout, log_dispatcher.logger_stderr]:
            # Log messages
            for level, msg in log_level_msgs.items():
                logger.log(level=level, msg=msg)

            # Check correct log level
            assert logger.getEffectiveLevel() == logging.DEBUG

            # Check correct handles
            # Pytest manipulates the handler streams to capture the logging output
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        actual_stdout_msgs = stdout.rstrip("\n").split("\n")
        actual_stderr_msgs = stderr.rstrip("\n").split("\n")
        assert len(actual_stdout_msgs) == len(expected_stdout_msgs)
        assert len(actual_stderr_msgs) == len(expected_stderr_msgs)
        debug_msg_start_re = re.compile(
            # Verbose debug msg prefix along lines of:
            # 2023-09-27 10:39:07,763 -
            r"^\d{4}(-\d{2}){2} (\d{2}:){2}\d{2},\d{3} - "
        )
        for actual_msg, expected_msg in itertools.chain(
            zip(actual_stdout_msgs, expected_stdout_msgs),
            zip(actual_stderr_msgs, expected_stderr_msgs),
        ):
            assert debug_msg_start_re.match(actual_msg)
            assert actual_msg.endswith(expected_msg)

    @pytest.mark.parametrize("verbosity", [1, 2])
    def test_log_dispatcher_info_logging(
        self,
        verbosity,
        capsys,
        data_log_dispatcher_info_color_log_messages,
    ):
        (
            logger_name,
            log_level_msgs,
            stdout_msgs,
            stderr_msgs,
        ) = data_log_dispatcher_info_color_log_messages

        # Setup the LogDispatcher
        log_dispatcher = LogDispatcher(
            name=logger_name,
            map_log_level_func=lambda msg: 0,  # not used in test since we log directly to loggers
            log_settings=LogSettings(
                verbosity=verbosity, log_file_path=None, no_color=False
            ),
        )
        assert f"{logger_name}.out" in logging.Logger.manager.loggerDict
        assert f"{logger_name}.err" in logging.Logger.manager.loggerDict

        # Log test messages to log dispatcher loggers
        for logger in [log_dispatcher.logger_stdout, log_dispatcher.logger_stderr]:
            # Log messages
            for level, msg in log_level_msgs.items():
                logger.log(level=level, msg=msg)

            # Check correct log level
            assert logger.getEffectiveLevel() == logging.INFO

            # Check correct handles
            # Pytest manipulates the handler streams to capture the logging output
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        assert stdout.rstrip("\n").split("\n") == stdout_msgs
        assert stderr.rstrip("\n").split("\n") == stderr_msgs

    def test_log_dispatcher_warning_logging(
        self,
        capsys,
        data_log_dispatcher_warning_color_log_messages,
    ):
        verbosity = 0
        (
            logger_name,
            log_level_msgs,
            stdout_msgs,
            stderr_msgs,
        ) = data_log_dispatcher_warning_color_log_messages

        # Setup the LogDispatcher
        log_dispatcher = LogDispatcher(
            name=logger_name,
            map_log_level_func=lambda msg: 0,  # not used in test since we log directly to loggers
            log_settings=LogSettings(
                verbosity=verbosity, log_file_path=None, no_color=False
            ),
        )
        assert f"{logger_name}.out" in logging.Logger.manager.loggerDict
        assert f"{logger_name}.err" in logging.Logger.manager.loggerDict

        # Log test messages to log dispatcher loggers
        for logger in [log_dispatcher.logger_stdout, log_dispatcher.logger_stderr]:
            # Log messages
            for level, msg in log_level_msgs.items():
                logger.log(level=level, msg=msg)

            # Check correct log level
            assert logger.getEffectiveLevel() == logging.WARNING

            # Check correct handles
            # Pytest manipulates the handler streams to capture the logging output
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        assert stdout.rstrip("\n").split("\n") == stdout_msgs
        assert stderr.rstrip("\n").split("\n") == stderr_msgs

    @pytest.mark.parametrize("no_color", [True, False])
    def test_log_to_file(
        self,
        no_color,
        tmp_path,
        data_log_dispatcher_info_no_color_log_messages,
    ):
        (
            logger_name,
            log_level_msgs,
            stdout_msgs,
            stderr_msgs,
        ) = data_log_dispatcher_info_no_color_log_messages

        # Setup the LogDispatcher
        log_file_path = tmp_path / "cotainr_log"
        log_dispatcher = LogDispatcher(
            name=logger_name,
            map_log_level_func=lambda msg: 0,  # not used in test since we log directly to loggers
            log_settings=LogSettings(
                verbosity=1, log_file_path=log_file_path, no_color=no_color
            ),
        )
        assert f"{logger_name}.out" in logging.Logger.manager.loggerDict
        assert f"{logger_name}.err" in logging.Logger.manager.loggerDict

        # Log test messages to log dispatcher loggers
        for logger in [log_dispatcher.logger_stdout, log_dispatcher.logger_stderr]:
            # Log messages
            for level, msg in log_level_msgs.items():
                logger.log(level=level, msg=msg)

            # Check correct log level
            assert logger.getEffectiveLevel() == logging.INFO

            # Check correct handles
            # Pytest manipulates the handler streams to capture the logging output
            assert len(logger.handlers) == 2
            assert isinstance(logger.handlers[0], logging.StreamHandler)
            assert isinstance(logger.handlers[1], logging.FileHandler)

        # Check correct logging, incl. message format, coloring, log level to file
        assert (
            log_file_path.with_suffix(".out").read_text().rstrip("\n").split("\n")
            == stdout_msgs
        )
        assert (
            log_file_path.with_suffix(".err").read_text().rstrip("\n").split("\n")
            == stderr_msgs
        )

    def test_no_color_on_console(
        self,
        capsys,
        data_log_dispatcher_info_no_color_log_messages,
    ):
        (
            logger_name,
            log_level_msgs,
            stdout_msgs,
            stderr_msgs,
        ) = data_log_dispatcher_info_no_color_log_messages

        # Setup the LogDispatcher
        log_dispatcher = LogDispatcher(
            name=logger_name,
            map_log_level_func=lambda msg: 0,  # not used in test since we log directly to loggers
            log_settings=LogSettings(verbosity=1, log_file_path=None, no_color=True),
        )
        assert f"{logger_name}.out" in logging.Logger.manager.loggerDict
        assert f"{logger_name}.err" in logging.Logger.manager.loggerDict

        # Log test messages to log dispatcher loggers
        for logger in [log_dispatcher.logger_stdout, log_dispatcher.logger_stderr]:
            # Log messages
            for level, msg in log_level_msgs.items():
                logger.log(level=level, msg=msg)

            # Check correct log level
            assert logger.getEffectiveLevel() == logging.INFO

            # Check correct handles
            # Pytest manipulates the handler streams to capture the logging output
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        assert stdout.rstrip("\n").split("\n") == stdout_msgs
        assert stderr.rstrip("\n").split("\n") == stderr_msgs


class TestLogToStderr:
    @pytest.mark.parametrize(
        "level",
        [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL],
    )
    def test_log_to_correct_level(self, level, caplog):
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: level,
            log_settings=LogSettings(verbosity=3, log_file_path=None, no_color=True),
        )
        log_dispatcher.log_to_stderr("test_6021")
        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == level
        assert caplog.records[0].name == "test_dispatcher_6021.err"
        assert caplog.records[0].msg == "test_6021"

    def test_not_stripping_whitespace(self, caplog):
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: logging.INFO,
            log_settings=LogSettings(verbosity=1, log_file_path=None, no_color=True),
        )
        msgs = ["  before", "after  ", "  before and after  "]
        for msg in msgs:
            log_dispatcher.log_to_stderr(msg=msg)

        assert len(caplog.records) == 3
        assert all(rec.name == "test_dispatcher_6021.err" for rec in caplog.records)
        assert all(msg == rec.msg for msg, rec in zip(msgs, caplog.records))


class TestLogToStdout:
    @pytest.mark.parametrize(
        "level",
        [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL],
    )
    def test_log_to_correct_level(self, level, caplog):
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: level,
            log_settings=LogSettings(verbosity=3, log_file_path=None, no_color=True),
        )
        log_dispatcher.log_to_stdout("test_6021")
        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == level
        assert caplog.records[0].name == "test_dispatcher_6021.out"
        assert caplog.records[0].msg == "test_6021"

    def test_not_stripping_whitespace(self, caplog):
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: logging.INFO,
            log_settings=LogSettings(verbosity=1, log_file_path=None, no_color=True),
        )
        msgs = ["  before", "after  ", "  before and after  "]
        for msg in msgs:
            log_dispatcher.log_to_stdout(msg=msg)

        assert len(caplog.records) == 3
        assert all(rec.name == "test_dispatcher_6021.out" for rec in caplog.records)
        assert all(msg == rec.msg for msg, rec in zip(msgs, caplog.records))


class TestPrefixStderrName:
    def test_context_prefix_changes(self, caplog):
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: 0,  # not used in test since we log directly to loggers,
            log_settings=LogSettings(verbosity=3, log_file_path=None, no_color=True),
        )
        with log_dispatcher.prefix_stderr_name(prefix="context_prefix_6021"):
            log_dispatcher.logger_stderr.info("test_6021")

        log_dispatcher.logger_stderr.info("test_6022")

        assert len(caplog.records) == 2
        assert caplog.records[0].name == "context_prefix_6021/test_dispatcher_6021.err"
        assert caplog.records[1].name == "test_dispatcher_6021.err"


class Test_DetermineLogLevel:
    @pytest.mark.parametrize(
        ["verbosity", "log_level"],
        [
            (-1000, logging.CRITICAL),
            (-2, logging.CRITICAL),
            (-1, logging.CRITICAL),
            (0, logging.WARNING),
            (1, logging.INFO),
            (2, logging.INFO),
            (3, logging.DEBUG),
            (4, logging.DEBUG),
            (1000, logging.DEBUG),
        ],
    )
    def test_correct_mapping_of_defined_log_levels(self, verbosity, log_level):
        assert LogDispatcher._determine_log_level(verbosity=verbosity) == log_level

    def test_error_on_not_equal_to_any_integer_but_comparable(self):
        with pytest.raises(ValueError) as exc_info:
            LogDispatcher._determine_log_level(verbosity=AlwaysCompareFalse())

        assert str(exc_info.value) == (
            "Somehow we ended up with a verbosity=AlwaysCompareFalseStub of "
            "type(verbosity)=<class 'cotainr.tests.tracing.stubs.AlwaysCompareFalse'> "
            "that does not compare well with integers."
        )
