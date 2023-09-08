"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements utility functions.

Classes
-------
ColoredOutputFormatter(logging.Formatter)
    A log formatter for coloring log messages based on log level.

"""
import copy
import contextlib
import dataclasses
import functools
import itertools
import logging
import pathlib
import re
import shutil
import sys
import threading
import time
import typing

logger = logging.getLogger(__name__)


class ColoredOutputFormatter(logging.Formatter):
    """
    A log formatter for coloring log messages based on log level.

    Inserts ANSI escape codes to color lines based on their log level:

    - logging.DEBUG : gray
    - logging.WARNING : yellow
    - logging.ERROR : dark read
    - logging.CRITICAL : brighter red
    """

    log_level_fg_colors = {
        # https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit
        logging.DEBUG: "\x1b[38;5;8m",  # gray
        logging.WARNING: "\x1b[38;5;3m",  # yellow
        logging.ERROR: "\x1b[38;5;1m",  # dark red
        logging.CRITICAL: "\x1b[38;5;160m",  # brighter red
    }
    reset_color = "\x1b[0m"

    def format(self, record):
        """Format the specified record as colored text."""
        fg_color = self.log_level_fg_colors.get(record.levelno, "")
        if fg_color:
            color_record = copy.copy(record)
            color_record.msg = fg_color + record.msg + self.reset_color
            return super().format(color_record)
        else:
            return super().format(record)


class ConsoleSpinner:
    def __init__(self):
        # TODO: DOC: Modify true sys.std* to allow for context change at any point in time
        self._stdout_proxy = StreamWriteProxy(stream=sys.stdout)
        self._stderr_proxy = StreamWriteProxy(stream=sys.stderr)
        self._as_atomic = threading.Lock()
        self._spinning_msg = None

    def __enter__(self):
        sys.stdout.write = functools.partial(
            self.update_spinner_msg, stream=self._stdout_proxy
        )
        sys.stderr.write = functools.partial(
            self.update_spinner_msg, stream=self._stderr_proxy
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._spinning_msg is not None:
            self._spinning_msg.stop()

        sys.stdout.write = self._stdout_proxy.true_stream_write
        sys.stderr.write = self._stderr_proxy.true_stream_write

    def update_spinner_msg(self, s, /, *, stream):
        with self._as_atomic:  # make sure that only a single thread at a time can update the spinning message
            if self._spinning_msg is not None:
                # Stop currently spinning message
                self._spinning_msg.stop()

            # Start spinning the new message
            self._spinning_msg = MessageSpinner(msg=s, stream=stream)
            self._spinning_msg.start()


class LogDispatcher:
    def __init__(
        self,
        *,
        name,
        map_log_level_func,
        filters=None,
        log_settings,
    ):
        self.map_log_level = map_log_level_func
        self.verbosity = log_settings.verbosity
        self.log_file_path = log_settings.log_file_path
        self.no_color = log_settings.no_color
        log_level = self._determine_log_level(verbosity=log_settings.verbosity)

        # Setup cotainr log format
        if self.verbosity >= 2:
            log_fmt = "%(asctime)s - %(name)s:%(levelname)s %(message)s"
        else:
            log_fmt = "%(name)s:-: %(message)s"

        # Setup log handlers
        stdout_handlers = [logging.StreamHandler(stream=sys.stdout)]
        stderr_handlers = [logging.StreamHandler(stream=sys.stderr)]

        if self.log_file_path is not None:
            stdout_handlers.append(
                logging.FileHandler(self.log_file_path.with_suffix(".out"))
            )
            stderr_handlers.append(
                logging.FileHandler(self.log_file_path.with_suffix(".err"))
            )
        for handler in stdout_handlers + stderr_handlers:
            handler.setLevel(log_level)
            handler.setFormatter(logging.Formatter(log_fmt))
            if filters is not None:
                for filter in filters:
                    handler.addFilter(filter)

        if not self.no_color:
            # Replace console formatters with one that colors the output
            stdout_handlers[0].setFormatter(ColoredOutputFormatter(log_fmt))
            stderr_handlers[0].setFormatter(ColoredOutputFormatter(log_fmt))

        # Setup loggers
        self.logger_stdout = logging.getLogger(f"{name}.out")
        self.logger_stdout.setLevel(log_level)
        for handler in stdout_handlers:
            self.logger_stdout.addHandler(handler)

        self.logger_stderr = logging.getLogger(f"{name}.err")
        self.logger_stderr.setLevel(log_level)
        for handler in stderr_handlers:
            self.logger_stderr.addHandler(handler)

        logger.debug(
            "LogDispatcher: %s, LEVEL: %s, STDOUT handlers: %s, STDERR handlers: %s",
            name,
            log_level,
            self.logger_stdout.handlers,
            self.logger_stderr.handlers,
        )

    def log_to_stdout(self, msg):
        self.logger_stdout.log(level=self.map_log_level(msg), msg=msg.strip())

    def log_to_stderr(self, msg):
        self.logger_stderr.log(level=self.map_log_level(msg), msg=msg.strip())

    @contextlib.contextmanager
    def prefix_stderr_name(self, *, prefix):
        logger_stderr_name = self.logger_stderr.name
        self.logger_stderr.name = prefix + "/" + logger_stderr_name
        yield
        self.logger_stderr.name = logger_stderr_name

    @staticmethod
    def _determine_log_level(*, verbosity):
        if verbosity == -1:
            log_level = logging.CRITICAL
        elif verbosity == 0:
            log_level = logging.WARNING
        elif verbosity in [1, 2]:
            log_level = logging.INFO
        elif verbosity >= 3:
            log_level = logging.DEBUG

        return log_level


@dataclasses.dataclass
class LogSettings:
    verbosity: int = 0
    log_file_path: typing.Optional[pathlib.Path] = None
    no_color: bool = False


class MessageSpinner:
    def __init__(self, *, msg, stream):
        self._msg = msg
        self._stream = stream

        self._spinner_cycle = itertools.cycle("⣾⣷⣯⣟⡿⢿⣻⣽")
        self._spinner_thread = threading.Thread(target=self._spin_msg)
        self._spinner_sleep_interval = 0.1
        self._spinner_delay_time = 0.025
        self._stop_signal = threading.Event()
        self._print_width = (
            # account for leading spinner + whitespace (2 chars)
            # and trailing dots (3 chars)
            shutil.get_terminal_size()[0]
            - 5
        )
        self._ansi_escape_re = re.compile(
            # Based on r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])" from
            # https://stackoverflow.com/a/14693789 with all "Select Graphics
            # Rendition (SGR)" codes (those ending with "m") passed through.
            # See also: https://notes.burke.libbey.me/ansi-escape-codes/
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*([@-l]|[n-~]))"
        )
        self._running = False

        # \033[2K erases the old line to avoid the extra two characters at the
        # end of the line stemming from the shift of the line due to the
        # leading spinner character and a whitespace
        self._clear_line_code = "\r" + "\x1B[2K"
        self._reset_SGR = "\x1b[0m"

    def start(self):
        self._spinner_thread.start()
        self._running = True

    def stop(self):
        if self._running:
            self._stop_signal.set()
            self._spinner_thread.join()
            self._running = False

    def _spin_msg(self):
        # Delay spinning a bit to avoid flaky message updates when new messages
        # arrive promptly
        time.sleep(self._spinner_delay_time)

        # Strip any newlines and ANSI escape codes that may interfere with
        # our manipulation of the console (not SGRs, though)
        msg = self._msg.rstrip("\n")
        msg = self._ansi_escape_re.sub("", msg)

        # Construct a messages that is guaranteed to fit on one line with the spinner
        one_line_msg = (
            # Make room for the spinner and 3 trailing dots and make sure to
            # keep the "reset SGR" code if its present
            msg[: (self._print_width - len(self._reset_SGR))] + self._reset_SGR
            if msg.endswith(self._reset_SGR)
            else msg[: self._print_width]
        ) + "..."

        # Start spinning
        while not self._stop_signal.is_set():
            # Update spinner
            print(
                f"{self._clear_line_code}{next(self._spinner_cycle)} "  # spinner
                f"{one_line_msg}",
                end="",  # keep overwriting current line
                file=self._stream,
            )
            time.sleep(self._spinner_sleep_interval)

        # Print message without spinner (incl. trailing newline)
        print(f"{self._clear_line_code}{msg}", file=self._stream)


class StreamWriteProxy:
    # TODO: DOC: Unable to copy sys.stdout
    def __init__(self, *, stream):
        self._stream = stream
        self.true_stream_write = stream.write

    def write(self, s, /):
        self.true_stream_write(s)

    def __getattr__(self, name):
        return getattr(self._stream, name)
