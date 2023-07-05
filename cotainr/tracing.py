import collections
import itertools
import logging
import queue
import shutil
import sys
import threading
import time

io_lock = threading.Lock()
console_msg_queue = queue.Queue()  # TODO: handle global


class QueuedStreamHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a queue.
    """

    def __init__(self, stream=None):
        """
        Initialize the handler.
        """
        super().__init__()
        if stream is None:
            stream = sys.stderr
        self.queue = console_msg_queue
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


class ProgressHandler:
    def __init__(self):
        """Construct the progress handler"""
        self._queue = console_msg_queue  # TODO: handle global
        self._spinner_cycle = itertools.cycle("⣾⣷⣯⣟⡿⢿⣻⣽")
        self._spinner_thread = threading.Thread(target=self._spinner_run_sequence)
        self._stop = threading.Event()
        self._sleep_interval = 0.1
        self._print_width = shutil.get_terminal_size()[0] - 2

    def start(self):
        """
        Start the process of printing out the latest message.
        It will run until the stop function is being called.
        """
        self._spinner_thread.start()

    def _spinner_run_sequence(self):
        current_item = None
        while not self._stop.is_set() and current_item is None:
            # Poll for first SteamMsg on queue
            try:
                current_item = self._queue.get_nowait()
            except queue.Empty:
                pass

            time.sleep(self._sleep_interval)

        while not self._stop.is_set():
            # Check for new SteamMsg
            try:
                new_item = self._queue.get_nowait()
                with io_lock:
                    # Print old StreamMsg
                    # \033[2K erases the old line to avoid the extra two
                    # characters at the end of the line stemming from the shift
                    # of the line due to the spinner character and a whitespace
                    print(
                        f"\033[2K{current_item.msg}",
                        file=current_item.stream,
                        flush=True,
                    )
                current_item = new_item
            except queue.Empty:
                pass

            # Update spinner
            with io_lock:
                print(
                    f"{next(self._spinner_cycle)} {current_item.msg[:self._print_width]}",
                    end="\r",
                    file=current_item.stream,
                    flush=True,
                )

            time.sleep(self._sleep_interval)

        if current_item is not None:
            # Print final StreamMsg (if any arrived)
            with io_lock:
                print(
                    f"\033[2K{current_item.msg}", file=current_item.stream, flush=True)

    def stop(self):
        """Stop the printing process"""
        self._stop.set()
        self._spinner_thread.join()


console_progress_handler = ProgressHandler()
console_progress_handler.start() # TODO


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
        console_stdout_handler = QueuedStreamHandler(stream=sys.stdout)
        console_stdout_handler.setLevel(log_level)
        console_stdout_handler.setFormatter(console_log_formatter)
        console_stderr_handler = QueuedStreamHandler(stream=sys.stderr)
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
