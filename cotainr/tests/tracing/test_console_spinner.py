"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""
import sys

import pytest

from cotainr.tracing import ConsoleSpinner, StreamWriteProxy
from .stubs import RaiseOnEnterContext


class TestConstructor:
    def test_attributes(self):
        spinner = ConsoleSpinner()
        assert isinstance(spinner._stdout_proxy, StreamWriteProxy)
        assert spinner._stdout_proxy._stream is sys.stdout
        assert isinstance(spinner._stderr_proxy, StreamWriteProxy)
        assert spinner._stderr_proxy._stream is sys.stderr
        assert spinner._true_input_func is input
        assert spinner._spinning_msg is None


class TestContext:
    def test_as_atomic_enter(self):
        console_spinner = ConsoleSpinner()
        console_spinner._as_atomic = RaiseOnEnterContext()
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            console_spinner.__enter__()

    def test_as_atomic_exit(self):
        console_spinner = ConsoleSpinner()
        console_spinner._as_atomic = RaiseOnEnterContext()
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            console_spinner.__exit__(None, None, None)

    def test_correctly_handling_input(self):
        1 / 0

    def test_correctly_spinning_stdout_msg(self):
        1 / 0

    def test_correctly_spinning_stderr_msg(self):
        1 / 0

    def test_exiting_context_with_spinning_msg(self):
        1 / 0

    def test_exiting_context_without_spinnnig_msg(self):
        1 / 0

    def test_reentering_context(self):
        1 / 0


class Test_UpdateSpinnerMsg:
    def test_as_atomic(self):
        console_spinner = ConsoleSpinner()
        console_spinner._as_atomic = RaiseOnEnterContext()
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            console_spinner._update_spinner_msg("", stream=None)

    def test_first_message_correctly_started(self):
        1 / 0

    def test_message_correctly_updated(self):
        1 / 0


class Test_ThreadSafeInput:
    def test_as_atomic(self):
        console_spinner = ConsoleSpinner()
        console_spinner._as_atomic = RaiseOnEnterContext()
        wrapped_input_func = console_spinner._thread_safe_input(lambda: None)
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            wrapped_input_func()

    def test_stop_spinning_msg(self):
        1 / 0

    def test_wrap_input_func(self):
        1 / 0
