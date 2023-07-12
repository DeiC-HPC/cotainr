import contextlib
import functools
import itertools
import logging
import re
import shutil
import sys
import threading
import time

logger = logging.getLogger(__name__)


class StreamWriteProxy:
    # TODO: DOC: Unable to copy sys.stdout
    def __init__(self, *, stream):
        self.stream = stream
        self.true_stream_write = stream.write

    def write(self, s, /):
        self.true_stream_write(s)

    def __getattr__(self, name):
        return getattr(self.stream, name)


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


class MessageSpinner:
    def __init__(self, *, msg, stream):
        self._msg = msg
        self._stream = stream

        self._spinner_cycle = itertools.cycle("⣾⣷⣯⣟⡿⢿⣻⣽")
        self._spinner_thread = threading.Thread(target=self._spin_msg)
        self._stop_signal = threading.Event()
        self._sleep_interval = 0.075
        self._print_width = (
            shutil.get_terminal_size()[0] - 2
        )  # account for spinner + whitespace
        self._ansi_escape_re = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self._running = False

        # \033[2K erases the old line to avoid the extra two
        # characters at the end of the line stemming from the shift
        # of the line due to the leading spinner character and a whitespace
        self._clear_line_code = "\r\033[2K"

    def start(self):
        self._spinner_thread.start()
        self._running = True

    def stop(self):
        if self._running:
            self._stop_signal.set()
            self._spinner_thread.join()
            self._running = False

    def _spin_msg(self):
        # strip any newlines and ANSI escape codes that may interfere with
        # our manipulation of the console
        msg = self._msg.rstrip("\n")
        msg = self._ansi_escape_re.sub(
            "", msg
        )  # TODO: does this remove colors as well?
        while not self._stop_signal.is_set():
            # Update spinner
            print(
                f"{self._clear_line_code}{next(self._spinner_cycle)} "
                f"{msg[:self._print_width]}",  # restrict output to terminal width
                end="",  # keep overwriting current line
                file=self._stream,
            )
            time.sleep(self._sleep_interval)

        # Print message without spinner (incl. trailing newline)
        print(f"{self._clear_line_code}{msg}", file=self._stream)


class LogDispatcher:
    # TODO: Cleanup and document
    def __init__(self, *, name, map_log_level_func, verbosity, log_file_path=None):
        log_level = self._determine_log_level(verbosity=verbosity)
        self.map_log_level = map_log_level_func

        # Setup cotainr log format
        if verbosity >= 2:
            log_formatter = logging.Formatter(
                "%(asctime)s - %(name)s:%(levelname)s %(message)s"
            )
        else:
            log_formatter = logging.Formatter("%(name)s:-: %(message)s")

        # Setup log handlers
        stdout_handlers = [logging.StreamHandler(stream=sys.stdout)]
        stderr_handlers = [logging.StreamHandler(stream=sys.stderr)]
        if log_file_path is not None:
            stdout_handlers.append(
                logging.FileHandler(log_file_path.with_suffix(".out"))
            )
            stderr_handlers.append(
                logging.FileHandler(log_file_path.with_suffix(".err"))
            )
        for handler in stdout_handlers + stderr_handlers:
            handler.setLevel(log_level)
            handler.setFormatter(log_formatter)

        # Setup loggers
        self.logger_stdout = logging.getLogger(f"{name}.out")
        self.logger_stdout.setLevel(log_level)
        for handler in stdout_handlers:
            self.logger_stdout.addHandler(handler)

        self.logger_stderr = logging.getLogger(f"{name}.err")
        self.logger_stderr.setLevel(log_level)
        for handler in stderr_handlers:
            self.logger_stderr.addHandler(handler)

        # TODO: implement filters

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
        elif verbosity == 1:
            log_level = logging.INFO
        elif verbosity >= 2:
            log_level = logging.DEBUG

        return log_level
