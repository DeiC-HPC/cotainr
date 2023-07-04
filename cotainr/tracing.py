import logging
import sys


COTAINR_CLI_INFO = 25


class ProgressHandler:
    # TODO: Add consistent spinner...
    stdout = sys.stdout
    stderr = sys.stderr


console_progress_handler = ProgressHandler()


def get_cotainr_log_level(verbosity=None):
    # TODO: Include this in LogDispatcher?
    if verbosity == -1:
        level = logging.CRITICAL
    elif verbosity == 0:
        level = logging.NOTSET
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    return level


class LogDispatcher:
    # TODO: Cleanup and document
    def __init__(self, *, name, map_log_level_func, verbosity):
        log_level = get_cotainr_log_level(verbosity=verbosity)

        # Setup cotainr log format
        if verbosity >= 2:
            console_log_formatter = logging.Formatter(
                f"%(asctime)s - %(name)s:%(levelname)s$ %(message)s"
            )
        else:
            console_log_formatter = logging.Formatter(
                f"{name}$ %(message)s"
            )

        # Setup log handlers
        console_stdout_handler = logging.StreamHandler(
            stream=console_progress_handler.stdout
        )
        console_stdout_handler.setLevel(log_level)
        console_stdout_handler.setFormatter(console_log_formatter)
        console_stderr_handler = logging.StreamHandler(
            stream=console_progress_handler.stderr
        )
        console_stderr_handler.setLevel(log_level)
        console_stderr_handler.setFormatter(console_log_formatter)

        self.logger_stdout = logging.getLogger(f"{name}.stdout")
        self.logger_stdout.addHandler(console_stdout_handler)
        self.logger_stdout.setLevel(log_level)
        self.logger_stderr = logging.getLogger(f"{name}.stderr")
        self.logger_stderr.addHandler(console_stderr_handler)
        self.logger_stderr.setLevel(log_level)
        self.map_log_level = map_log_level_func
        # TODO: Add FileHandler

    def log_to_stdout(self, msg):
        self.logger_stdout.log(level=self.map_log_level(msg), msg=msg.strip())

    def log_to_stderr(self, msg):
        self.logger_stderr.log(level=self.map_log_level(msg), msg=msg.strip())


def setup_cotainr_cli_logging(*, verbosity):
    #TODO: Move to CotainrCLI?
    if verbosity == 0:
        cotainr_log_level = COTAINR_CLI_INFO
    else:
        cotainr_log_level = get_cotainr_log_level(verbosity=verbosity)

    # Setup cotainr CLI log format
    if verbosity >= 2:
        cotainr_console_log_formatter = logging.Formatter(
            "%(asctime)s - %(name)s::%(funcName)s::%(lineno)d::"
            "Cotainr:%(levelname)s$ %(message)s"
        )
    else:
        cotainr_console_log_formatter = logging.Formatter(
            "Cotainr: %(message)s$"
        )

    # Setup cotainr CLI log handlers
    cotainr_console_handler = logging.StreamHandler(
        stream=console_progress_handler.stdout
    )
    cotainr_console_handler.setLevel(cotainr_log_level)
    cotainr_console_handler.setFormatter(cotainr_console_log_formatter)

    # Define cotainr root logger
    root_logger = logging.getLogger("cotainr")
    root_logger.setLevel(cotainr_log_level)
    root_logger.addHandler(cotainr_console_handler)  # Cotainr logs to stdout
    # TODO: Add FileHandler
