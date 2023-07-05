import logging
import sys


class ProgressHandler:
    # TODO: Add consistent spinner...
    stdout = sys.stdout
    stderr = sys.stderr


console_progress_handler = ProgressHandler()


class LogDispatcher:
    # TODO: Cleanup and document
    def __init__(self, *, name, map_log_level_func, verbosity):
        log_level = self._determine_log_level(verbosity=verbosity)

        # Setup cotainr log format
        if verbosity >= 2:
            console_log_formatter = logging.Formatter(
                "%(asctime)s - %(name)s:%(levelname)s$ %(message)s"
            )
        else:
            console_log_formatter = logging.Formatter(f"{name}$ %(message)s")

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

    @staticmethod
    def _determine_log_level(*, verbosity):
        if verbosity == -1:
            log_level = logging.CRITICAL
        elif verbosity == 0:
            log_level = logging.WARNING
        elif verbosity == 1:
            log_level = logging.INFO
        elif verbosity >= 2:
            log_level = logging.DEBUG

        return log_level
