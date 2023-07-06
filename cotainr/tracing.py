import collections
import itertools
import logging
import queue
import shutil
import sys
import threading
import time


class QueuedStreamHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a queue.
    """

    def __init__(self, *, queue, stream=None):
        """
        Initialize the handler.
        """
        super().__init__()
        self.queue = queue
        if stream is None:
            self.stream = sys.stderr
        else:
            self.stream = stream

        self.StreamMsg = collections.namedtuple("StreamMsg", ["msg", "stream"])

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """

        try:
            msg = self.format(record)
            self.queue.put(self.StreamMsg(msg=msg, stream=self.stream))
        except Exception:
            self.handleError(record)

    # TODO: def flush()?


class ConsoleProgressHandler:
    def __init__(self, queue):
        """Construct the progress handler"""
        self._queue = queue
        self._spinner_cycle = itertools.cycle("⣾⣷⣯⣟⡿⢿⣻⣽")
        self._spinner_thread = threading.Thread(target=self._spinner_run_sequence)
        self._stop = threading.Event()
        self._sleep_interval = 0.1
        self._print_width = shutil.get_terminal_size()[0] - 2

        # \033[2K erases the old line to avoid the extra two
        # characters at the end of the line stemming from the shift
        # of the line due to the spinner character and a whitespace
        self._clear_line_code = "\r\033[2K"

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._queue.join()
        self.stop()

    def start(self):
        """
        Start the process of printing out the latest message.
        It will run until the stop function is being called.
        """
        self._spinner_thread.start()

    def _spinner_run_sequence(self):
        current_item = None
        while not self._stop.is_set():
            time.sleep(self._sleep_interval)
            try:
                if current_item is None:
                    # Poll for first SteamMsg on queue
                    current_item = self._queue.get_nowait()
                else:
                    # Check for new SteamMsg
                    new_item = self._queue.get_nowait()

                    # Print old StreamMsg if a new one is ready
                    print(
                        f"{self._clear_line_code}{current_item.msg}",
                        file=current_item.stream,
                        flush=True,
                    )
                    current_item = new_item

                self._queue.task_done()

            except queue.Empty:
                if current_item is None:
                    # 
                    continue

            # Update spinner
            print(
                f"{self._clear_line_code}{next(self._spinner_cycle)} "
                f"{current_item.msg[:self._print_width]}",
                end="",  # no newline to keep overwriting current line
                file=current_item.stream,
                flush=True,
            )

        # Print final StreamMsg without spinner (if any)
        if current_item is not None:
            print(
                f"{self._clear_line_code}{current_item.msg}",
                file=current_item.stream,
                flush=True,
            )

    def stop(self):
        """Stop the printing process"""
        self._stop.set()
        self._spinner_thread.join()


class LogDispatcher:
    # TODO: Cleanup and document
    def __init__(self, *, name, map_log_level_func, verbosity, console_log_msg_queue):
        log_level = self._determine_log_level(verbosity=verbosity)

        # Setup cotainr log format
        if verbosity >= 2:
            console_log_formatter = logging.Formatter(
                "%(asctime)s - %(name)s:%(levelname)s$ %(message)s"
            )
        else:
            console_log_formatter = logging.Formatter(f"{name}:-: %(message)s")

        # Setup log handlers
        console_stdout_handler = QueuedStreamHandler(
            queue=console_log_msg_queue, stream=sys.stdout
        )
        console_stdout_handler.setLevel(log_level)
        console_stdout_handler.setFormatter(console_log_formatter)
        console_stderr_handler = QueuedStreamHandler(
            queue=console_log_msg_queue, stream=sys.stderr
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
