"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import functools
import io
import logging
import platform
import subprocess
import sys

import pytest

from cotainr.tracing import LogDispatcher, LogSettings
from cotainr.util import _print_and_capture_stream, stream_subprocess


class TestStreamSubprocess:
    def test_completed_process(self):
        proc_args = [
            sys.executable,
            "-c",
            "import platform; print(platform.python_version())",
        ]
        process = stream_subprocess(args=proc_args)
        assert process.args == proc_args
        assert process.returncode == 0
        assert process.stdout.strip() == platform.python_version()

    def test_check_returncode(self):
        cmd_exit = [sys.executable, "-c", "import sys; sys.exit(1)"]
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            stream_subprocess(args=cmd_exit)

        assert exc_info.value.returncode == 1
        assert exc_info.value.cmd == cmd_exit

    def test_kwargs_passing(self):
        env = {"COTAINR_TEST_ENV_VAR": "6021"}
        process = stream_subprocess(
            args=[
                sys.executable,
                "-c",
                "import os; print(os.environ['COTAINR_TEST_ENV_VAR'])",
            ],
            env=env,
        )
        assert process.stdout.strip() == env["COTAINR_TEST_ENV_VAR"]

    def test_logging_stdout(self, caplog):
        log_level = logging.INFO
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: log_level,
            log_settings=LogSettings(verbosity=1, log_file_path=None, no_color=False),
        )
        stdout_text = """
        Text on line 1

        More text later!
        """

        stream_subprocess(
            args=[
                sys.executable,
                "-c",
                f"import os; os.write(1, {stdout_text.encode()})",
            ],
            log_dispatcher=log_dispatcher,
        )

        stdout_lines = stdout_text.splitlines(keepends=True)
        assert len(stdout_lines) == len(caplog.records)
        for line, rec in zip(stdout_lines, caplog.records):
            assert rec.levelno == log_level
            assert rec.name == "test_dispatcher_6021.out"
            assert rec.msg == line

    def test_logging_stderr(self, caplog):
        log_level = logging.ERROR
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: log_level,
            log_settings=LogSettings(verbosity=0, log_file_path=None, no_color=False),
        )
        stderr_text = """
        An error!
        More breakage...
        """

        stream_subprocess(
            args=[
                sys.executable,
                "-c",
                f"import os; os.write(2, {stderr_text.encode()})",
            ],
            log_dispatcher=log_dispatcher,
        )

        stderr_lines = stderr_text.splitlines(keepends=True)
        assert len(stderr_lines) == len(caplog.records)
        for line, rec in zip(stderr_lines, caplog.records):
            assert rec.levelno == log_level
            assert rec.name == "test_dispatcher_6021.err"
            assert rec.msg == line

    def test_stdout(self):
        stdout_text = """
        Text on line 1

        More text later!
        """
        process = stream_subprocess(
            args=[
                sys.executable,
                "-c",
                f"import os; os.write(1, {stdout_text.encode()})",
            ]
        )
        assert process.stdout == stdout_text

    def test_stderr(self):
        stderr_text = """
        An error!
        More breakage...
        """
        process = stream_subprocess(
            args=[
                sys.executable,
                "-c",
                f"import os; os.write(2, {stderr_text.encode()})",
            ]
        )
        assert process.stderr == stderr_text


class Test_PrintAndCaptureStream:
    def test_print_stdout_roundtrip(self, capsys):
        stdout_lines = ["Test line 1", "Test line 2", "Test line 3"]
        input_stream = io.StringIO("\n".join(stdout_lines))
        print_dispatch = functools.partial(print, end="", file=sys.stdout)
        _print_and_capture_stream(
            stream_handle=input_stream, print_dispatch=print_dispatch
        )
        captured_io = capsys.readouterr()
        assert captured_io.out.split("\n") == stdout_lines

    def test_print_and_capture_equality(self):
        input_text = "Test line 1\nTest line 2"
        input_stream = io.StringIO(input_text)
        output_stream = io.StringIO()
        print_dispatch = functools.partial(print, end="", file=output_stream)
        captured_stream = _print_and_capture_stream(
            stream_handle=input_stream, print_dispatch=print_dispatch
        )
        assert output_stream.getvalue() == "".join(captured_stream)
