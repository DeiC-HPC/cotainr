"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements functionality for tracing and logging console messages.

Classes
-------
ColoredOutputFormatter(logging.Formatter)
    A log formatter for coloring log messages based on log level.
ConsoleSpinner
    A console messages spinner context manager.
StreamWriteProxy
    A proxy for manipulating the write methods of streams.
LogDispatcher
    A dispatcher for configuring and handling log messages.
LogSettings
    Dataclass containing settings for a LogDispatcher.
MessageSpinner
    A spinner for console messages.
"""
import builtins
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

    Attributes
    ----------
    log_level_fg_colors : dict
        Mapping of log level to ANSI escape color codes.
    reset_color : str
        The ANSI escape code to reset (color) formatting.
    """

    log_level_fg_colors = {
        # https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit
        logging.DEBUG: "\x1b[38;5;8m",  # gray
        logging.INFO: "",  # no special color
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
    """
    A console messages spinner context manager.

    Creates a context in which messages to `sys.stdout` and `sys.stderr` are
    prepended with a spinner to indicate that the program is still progressing
    while we are waiting for the next message to be displayed on the console.

    Notes
    -----
    The :class:`ConsoleSpinner` is implemented by monkeypatching
    :py:data:`sys.stdout`, :py:data:`sys.stderr`, and :py:func:`input`.

    The :py:meth:`sys.stdout.write` and :py:meth:`sys.stderr.write` methods are
    replaced by the :meth:`_update_spinner_msg` method which starts a new
    :class:`~cotainr.tracing.MessageSpinner` thread every time a new message is
    written to `stdout` / `stderr`. In order to avoid an infinite recursion
    when the text is actually written to the console, `sys.stdout` and
    `sys.stderr` are wrapped by :class:`~cotainr.tracing.StreamWriteProxy`
    instances.

    The :py:func:`input` function is wrapped to make sure that the spinner is
    stopped while waiting for the user to provide their input.

    Nothing is done to handle the use of the :py:mod:`readline` module. It may
    or may not work in a :class:`ConsoleSpinner` context.

    This :class:`ConsoleSpinner` class is only intended to be used with the
    :py:mod:`threading` module. It doesn't support :py:mod:`multiprocessing`.
    """

    def __init__(self):
        """Construct the ConsoleSpinner context manager."""
        self._stdout_proxy = StreamWriteProxy(stream=sys.stdout)
        self._stderr_proxy = StreamWriteProxy(stream=sys.stderr)
        self._true_input_func = builtins.input
        self._as_atomic = threading.Lock()
        self._spinning_msg = None

    def __enter__(self):
        """Setup the console spinner context."""
        with self._as_atomic:
            # Wrap stdout, stderr, and input to prepend spinner to all console
            # messages
            sys.stdout.write = functools.partial(
                self._update_spinner_msg, stream=self._stdout_proxy
            )
            sys.stderr.write = functools.partial(
                self._update_spinner_msg, stream=self._stderr_proxy
            )
            builtins.input = self._thread_safe_input(builtins.input)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Tear down the console spinner context."""
        with self._as_atomic:
            if self._spinning_msg is not None:
                # Stop currently spinning message
                self._spinning_msg.stop()
                self._spinning_msg = None

            # Restore true stdout, stderr, and input
            sys.stdout.write = self._stdout_proxy.true_stream_write
            sys.stderr.write = self._stderr_proxy.true_stream_write
            builtins.input = self._true_input_func

    def _update_spinner_msg(self, s, /, *, stream):
        """
        Update the spinning message.

        Stops the current spinning messages thread and starts a new
        :class:`~cotainr.tracing.MessageSpinner` thread for the new message.

        Parameters
        ----------
        s : str
            The new message to prepend with a spinner.
        stream : :py:class:`io.TextIOWrapper`
            The text stream on which to spin the message.
        """
        with self._as_atomic:
            if self._spinning_msg is not None:
                # Stop currently spinning message
                self._spinning_msg.stop()

            # Start spinning the new message
            self._spinning_msg = MessageSpinner(msg=s, stream=stream)
            self._spinning_msg.start()

    def _thread_safe_input(self, input_func):
        """
        A decorator to make input stop spinning messages.

        Stops the spinning message prior to calling the :py:func:`input` such
        that the spinning message doesn't interfere with the user input.
        """

        @functools.wraps(input_func)
        def wrapped_input_func(*args, **kwargs):
            with self._as_atomic:
                if self._spinning_msg is not None:
                    self._spinning_msg.stop()
                    self._spinning_msg = None

                return input_func(*args, **kwargs)

        return wrapped_input_func


class LogDispatcher:
    """
    A dispatcher for configuring and handling log messages.

    Sets up the logging machinery and provides methods for logging to the
    relevant log handlers using the correct log level - to be used in
    subprocesses. See the :ref:`cotainr Tracing & Logging documentation page
    <tracing_logging>` for more details.

    Parameters
    ----------
    name : str
        The name to use to identify this log dispatcher in log messages.
    map_log_level_func : Callable
        A callable that maps a message to a log level to use for the message.
    log_settings : :class:`~cotainr.tracing.LogSettings`
        The settings to use when setting up the logging machinery.
    filters : list of :py:class:`logging.Filter`, optional
        The filters to add to the log handlers (the default is None with
        implies that no filters are added to the log handlers).

    Attributes
    ----------
    verbosity : int
        The cotainr verbosity level used by the log dispatcher.
    map_log_level : Callable
        The callable that maps a message to a log level to use for the message.
    log_file_path : :py:class:`pathlib.Path`, optional
        The prefix of the file path to save logs to, if specified.
    no_color : bool
        The indicator of whether or not to disable the coloring of console
        message.
    logger_stdout : :py:class:`logging.Logger`
        The logger used to log to `stdout`.
    logger_stderr : :py:class:`logging.Logger`
        The logger used to log to `stderr`.
    """

    def __init__(
        self,
        *,
        name,
        map_log_level_func,
        log_settings,
        filters=None,
    ):
        """Setup the log dispatcher."""
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

    def log_to_stderr(self, msg):
        """
        Log a message to `stderr`.

        Determines the log level based on the `map_log_level` function and logs
        the `msg` to `stderr` using that log level.

        Parameters
        ----------
        msg : str
            The message to log.
        """
        self.logger_stderr.log(level=self.map_log_level(msg), msg=msg.strip())

    def log_to_stdout(self, msg):
        """
        Log a message to `stdout`.

        Determines the log level based on the `map_log_level` function and logs
        the `msg` to `stdout` using that log level.

        Parameters
        ----------
        msg : str
            The message to log.
        """
        self.logger_stdout.log(level=self.map_log_level(msg), msg=msg.strip())

    @contextlib.contextmanager
    def prefix_stderr_name(self, *, prefix):
        """
        A context manager for prefixing the `stderr` logger name.

        When inside the context, the name of the `stderr` logger is changed to
        be prefixed by "`prefix`/".

        Parameters
        ----------
        prefix : str
            The prefix add to the `stderr` logger name.
        """
        logger_stderr_name = self.logger_stderr.name
        self.logger_stderr.name = prefix + "/" + logger_stderr_name
        yield
        self.logger_stderr.name = logger_stderr_name

    @staticmethod
    def _determine_log_level(*, verbosity):
        """
        Map cotainr verbosity level to a logger and handler log level.

        Parameters
        ----------
        verbosity : int
            The cotainr verbosity level used by the log dispatcher.

        Returns
        -------
        log_level : int
            One of the standard log levels (DEBUG, INFO, WARNING, ERROR, or
            CRITICAL).
        """
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
    """
    Dataclass containing settings for a LogDispatcher.

    Attributes
    ----------
    verbosity : int, default=0
        The cotainr verbosity level used by the log dispatcher.
    log_file_path : :py:class:`pathlib.Path`, default=None
        The prefix of the file path to save logs to, if specified.
    no_color : bool, default=False
        The indicator of whether or not to disable the coloring of console
        message.
    """

    verbosity: int = 0
    log_file_path: typing.Optional[pathlib.Path] = None
    no_color: bool = False


class MessageSpinner:
    """
    A spinner for console messages.

    Creates a thread that continuously updates a prepended spinner to `msg` on
    `stream`. While the spinner is active, the `msg` is truncated to fit within
    a single line. When the spinner is stopped, the full `msg` (without
    spinner) is written to the `stream`.

    Parameters
    ----------
    msg : str
        The message to prepend with a spinner.
    stream : :py:class:`io.TextIOWrapper`
        The text stream on which to spin the message.

    Notes
    -----
    The spinner is added by continuously rewriting the current console line to
    update the spinning character prepended to `msg`. This is done using CR and
    ANSI escape codes. To avoid interfering with our manipulation of the
    console line, trailing newlines and ANSI codes, except "Select Graphics
    Rendition (SGR)" codes used for coloring console lines, are stripped from
    `msg` before it is displayed on the console.
    """

    def __init__(self, *, msg, stream):
        """Construct the message spinner."""
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
        """Start the message spinner thread."""
        self._spinner_thread.start()
        self._running = True

    def stop(self):
        """Stop the message spinner thread"""
        if self._running:
            self._stop_signal.set()
            self._spinner_thread.join()
            self._running = False

    def _spin_msg(self):
        """
        Spin the message.

        This is the method that the thread is running to continuously update
        the spinnner.
        """
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
                f"{one_line_msg}",  # possibly truncated message
                end="",  # keep overwriting current line
                file=self._stream,
            )
            time.sleep(self._spinner_sleep_interval)

        # Print message without spinner (incl. trailing newline)
        print(f"{self._clear_line_code}{msg}", file=self._stream)


class StreamWriteProxy:
    """
    A proxy for manipulating the write methods of streams.

    Provides a `write` method that guarantees to use the true `stream.write`
    method in case `stream.write` is later monkeypatched. All other method
    calls to this class are delegated to the corresponding (potentially
    monkeypatched) methods implemented by `stream`.

    Parameters
    ----------
    stream : :py:class:`io.TextIOWrapper`
        The text stream to provide a proxy for.

    Notes
    -----
    This provides a way for keeping references to the true
    :py:meth:`sys.stdout.write` and :py:meth:`sys.stderr.write` methods. This
    is useful in code that monkeypatches these methods since it is not possible
    in Python to copy :py:data:`sys.stdout` and :py:data:`sys.stderr` such that
    they can later be restored.
    """

    def __init__(self, *, stream):
        """Construct the stream write proxy."""
        self._stream = stream
        self.true_stream_write = stream.write

    def write(self, s, /):
        """
        Write a string to the stream using the true `stream.write` method and
        return the number of characters written.

        Parameters
        ----------
        s : str
            The string to write.
        """
        return self.true_stream_write(s)

    def __getattr__(self, name):
        """Delegate all other attribute and method calls."""
        return getattr(self._stream, name)
