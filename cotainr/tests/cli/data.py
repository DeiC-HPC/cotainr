"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest


@pytest.fixture
def data_cotainr_info_color_log_messages(data_log_level_names_mapping):
    """"""
    # log messages
    log_level_msgs = {
        level: f"Log {level_name} 6021"
        for level, level_name in data_log_level_names_mapping.items()
    }

    # stdout
    stdout_msgs = ["Cotainr:-: Log INFO 6021"]

    # stderr
    stderr_msgs = [
        "Cotainr:-:CRITICAL: \x1b[38;5;160mLog CRITICAL 6021\x1b[0m",
        "Cotainr:-:ERROR: \x1b[38;5;1mLog ERROR 6021\x1b[0m",
        "Cotainr:-:WARNING: \x1b[38;5;3mLog WARNING 6021\x1b[0m",
    ]

    return log_level_msgs, stdout_msgs, stderr_msgs
