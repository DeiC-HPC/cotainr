import logging
import sys


class ProgressHandler:
    # TODO: Add consistent spinner...
    stdout = sys.stdout
    stderr = sys.stderr


console_progress_handler = ProgressHandler()


def get_cotainr_log_level(verbosity=None):
    # TODO: Include this in LogDispatcher?
    if verbosity == -1:
        level = logging.CRITICAL  # TODO
    elif verbosity == 0:
        level = logging.NOTSET  # TODO: custom cotainr level?
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    return level


class LogDispatcher:
    # TODO: Cleanup and document
    def __init__(
        self,
        *,
        name,
        map_log_level_func,
        verbosity
    ):
        log_level = get_cotainr_log_level(verbosity=verbosity)

        console_log_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )  # TODO: set based on CLI args
        console_stdout_handler = logging.StreamHandler(stream=console_progress_handler.stdout)
        console_stdout_handler.setLevel(log_level)
        console_stdout_handler.setFormatter(console_log_formatter)
        console_stderr_handler = logging.StreamHandler(stream=console_progress_handler.stderr)
        console_stderr_handler.setLevel(log_level)
        console_stderr_handler.setFormatter(console_log_formatter)

        self.logger_stdout = logging.getLogger(f"{name}.stdout")
        self.logger_stdout.addHandler(console_stdout_handler)
        self.logger_stdout.setLevel(log_level)
        self.logger_stderr = logging.getLogger(f"{name}.stderr")
        self.logger_stderr.addHandler(console_stderr_handler)
        self.logger_stderr.setLevel(log_level)
        self.map_log_level = map_log_level_func

    def log_to_stdout(self, msg):
        self.logger_stdout.log(level=self.map_log_level(msg), msg=msg.strip())

    def log_to_stderr(self, msg):
        self.logger_stderr.log(level=self.map_log_level(msg), msg=msg.strip())


def setup_log_handlers(*, verbosity=None):
    # Setup logging
    # TODO: Fully remove this?
    console_log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )  # TODO: set based on CLI args
    console_stdout_handler = logging.StreamHandler(stream=console_progress_handler.stdout)
    console_stdout_handler.setLevel(logging.DEBUG)  # TODO: set based on CLI args
    console_stdout_handler.setFormatter(console_log_formatter)
    console_stderr_handler = logging.StreamHandler(stream=console_progress_handler.stderr)
    console_stderr_handler.setLevel(logging.DEBUG)  # TODO: set based on CLI args
    console_stderr_handler.setFormatter(console_log_formatter)
    # TODO: Add FileHandler(s)

