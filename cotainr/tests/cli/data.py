"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest


@pytest.fixture
def data_cotainr_critical_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the CotainrCLI logging machinery at CRITICAL level.
    """
    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected stdout messages
    stdout_msgs = [""]

    # Expected stderr messages
    stderr_msgs = [
        "Cotainr:-:CRITICAL: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
    ]

    return log_level_msgs, stdout_msgs, stderr_msgs


@pytest.fixture
def data_cotainr_debug_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the CotainrCLI logging machinery at DEBUG level.
    """
    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected ending of stdout messages
    # (debug messages are prepended with a time stamp)
    stdout_msgs = [
        "Cotainr:-:INFO: Log INFO 6021",
        "Cotainr:-:DEBUG: \x1b[38;5;8mLog DEBUG 6021\x1b[0m",
    ]

    # Expected ending of stderr messages
    # (debug messages are prepended with a time stamp)
    stderr_msgs = [
        "Cotainr:-:CRITICAL: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "Cotainr:-:ERROR: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "Cotainr:-:WARNING: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
    ]

    return log_level_msgs, stdout_msgs, stderr_msgs


@pytest.fixture
def data_cotainr_info_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the CotainrCLI logging machinery at INFO level.
    """
    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected stdout messages
    stdout_msgs = ["Cotainr:-: Log INFO 6021"]

    # Expected stderr messages
    stderr_msgs = [
        "Cotainr:-:CRITICAL: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "Cotainr:-:ERROR: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "Cotainr:-:WARNING: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
    ]

    return log_level_msgs, stdout_msgs, stderr_msgs


@pytest.fixture
def data_cotainr_info_no_color_log_messages(data_log_level_names_mapping):
    """
    Log messages for standard log levels and their expected output to
    stdout/stderr for the CotainrCLI logging machinery at INFO level - without
    message coloring.
    """
    # Messages to log at the different standard log levels
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # Expected stdout messages
    stdout_msgs = ["Cotainr:-: Log INFO 6021"]

    # Expected stderr messages
    stderr_msgs = [
        "Cotainr:-:CRITICAL: Log CRITICAL 6021",
        "Cotainr:-:ERROR: Log ERROR 6021",
        "Cotainr:-:WARNING: Log WARNING 6021",
    ]

    return log_level_msgs, stdout_msgs, stderr_msgs
