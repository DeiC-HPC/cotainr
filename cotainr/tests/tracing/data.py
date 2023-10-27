"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest


@pytest.fixture
def data_log_dispatcher_critical_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the LogDispatcher logging machinery at CRITICAL level.
    """
    # Choose a logger name
    logger_name = "LD_6021"

    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected stdout messages
    stdout_msgs = ["LD_6021.out:-: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m"]

    # Expected stderr messages
    stderr_msgs = ["LD_6021.err:-: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m"]

    return logger_name, log_level_msgs, stdout_msgs, stderr_msgs


@pytest.fixture
def data_log_dispatcher_debug_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the LogDispatcher logging machinery at DEBUG level.
    """
    # Choose a logger name
    logger_name = "LD_6021"

    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected ending of stdout messages
    # (debug messages are prepended with a time stamp)
    stdout_msgs = [
        "LD_6021.out:-:CRITICAL: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "LD_6021.out:-:ERROR: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "LD_6021.out:-:WARNING: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
        "LD_6021.out:-:INFO: Log INFO 6021",
        "LD_6021.out:-:DEBUG: \x1b[38;5;8mLog DEBUG 6021\x1b[0m",
    ]

    # Expected ending of stderr messages
    # (debug messages are prepended with a time stamp)
    stderr_msgs = [
        "LD_6021.err:-:CRITICAL: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "LD_6021.err:-:ERROR: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "LD_6021.err:-:WARNING: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
        "LD_6021.err:-:INFO: Log INFO 6021",
        "LD_6021.err:-:DEBUG: \x1b[38;5;8mLog DEBUG 6021\x1b[0m",
    ]

    return logger_name, log_level_msgs, stdout_msgs, stderr_msgs


@pytest.fixture
def data_log_dispatcher_info_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the LogDispatcher logging machinery at INFO level.
    """
    # Choose a logger name
    logger_name = "LD_6021"

    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected stdout messages
    stdout_msgs = [
        "LD_6021.out:-: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "LD_6021.out:-: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "LD_6021.out:-: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
        "LD_6021.out:-: Log INFO 6021",
    ]

    # Expected stderr messages
    stderr_msgs = [
        "LD_6021.err:-: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "LD_6021.err:-: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "LD_6021.err:-: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
        "LD_6021.err:-: Log INFO 6021",
    ]

    return logger_name, log_level_msgs, stdout_msgs, stderr_msgs


@pytest.fixture
def data_log_dispatcher_info_no_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the LogDispatcher logging machinery at INFO level -
    without message coloring.
    """
    # Choose a logger name
    logger_name = "LD_6021"

    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected stdout messages
    stdout_msgs = [
        "LD_6021.out:-: Log CRITICAL 6021",
        "LD_6021.out:-: Log ERROR 6021",
        "LD_6021.out:-: Log WARNING 6021",
        "LD_6021.out:-: Log INFO 6021",
    ]

    # Expected stderr messages
    stderr_msgs = [
        "LD_6021.err:-: Log CRITICAL 6021",
        "LD_6021.err:-: Log ERROR 6021",
        "LD_6021.err:-: Log WARNING 6021",
        "LD_6021.err:-: Log INFO 6021",
    ]

    return logger_name, log_level_msgs, stdout_msgs, stderr_msgs


@pytest.fixture
def data_log_dispatcher_warning_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the LogDispatcher logging machinery at WARNING level.
    """
    # Choose a logger name
    logger_name = "LD_6021"

    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected stdout messages
    stdout_msgs = [
        "LD_6021.out:-: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "LD_6021.out:-: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "LD_6021.out:-: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
    ]

    # Expected stderr messages
    stderr_msgs = [
        "LD_6021.err:-: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "LD_6021.err:-: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "LD_6021.err:-: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
    ]

    return logger_name, log_level_msgs, stdout_msgs, stderr_msgs
