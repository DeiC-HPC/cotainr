"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""
import sys

import pytest

from cotainr.tracing import ConsoleSpinner, StreamWriteProxy
from .patches import patch_fix_number_of_message_spins
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

    @pytest.mark.parametrize("spins", [1])
    def test_correctly_spinning_stdout_msg(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        with ConsoleSpinner():
            sys.stdout.write("test_6021")

        stdout = capsys.readouterr().out
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert stdout == spin_and_final_line

    @pytest.mark.parametrize("spins", [1])
    def test_correctly_spinning_stderr_msg(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        with ConsoleSpinner():
            sys.stderr.write("test_6021")

        stderr = capsys.readouterr().err
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert stderr == spin_and_final_line

    def test_exiting_context_with_spinning_msg(self):
        1 / 0

    def test_exiting_context_without_spinning_msg(self, capsys):
        with ConsoleSpinner():
            pass

        stdout, stderr = capsys.readouterr()
        assert not stdout
        assert not stderr

    @pytest.mark.parametrize("spins", [1])
    def test_reentering_context(self, spins, capsys, patch_fix_number_of_message_spins):
        with ConsoleSpinner():
            sys.stdout.write("test_6021_level_1")
            with ConsoleSpinner():
                sys.stdout.write("test_6021_level_2")
                with ConsoleSpinner():
                    with ConsoleSpinner():
                        sys.stdout.write("test_6021_level_4")

        stdout = capsys.readouterr().out
        level_1_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_level_1..." + "\r\x1b[2Ktest_6021_level_1\n"
        )
        level_2_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_level_2..." + "\r\x1b[2Ktest_6021_level_2\n"
        )
        level_4_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_level_4..." + "\r\x1b[2Ktest_6021_level_4\n"
        )
        assert stdout == (
            level_1_spin_and_final_line
            + level_2_spin_and_final_line
            + level_4_spin_and_final_line
        )

    def test_return_self(self):
        1/0

    @pytest.mark.parametrize("spins", [1])
    def test_switching_from_stdout_to_stderr(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        with ConsoleSpinner():
            sys.stdout.write("test_6021_stdout")
            sys.stderr.write("test_6021_stderr")

        stdout, stderr = capsys.readouterr()
        stdout_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_stdout..." + "\r\x1b[2Ktest_6021_stdout\n"
        )
        stderr_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_stderr..." + "\r\x1b[2Ktest_6021_stderr\n"
        )
        assert stdout == stdout_spin_and_final_line
        assert stderr == stderr_spin_and_final_line

    @pytest.mark.parametrize("spins", [1])
    def test_switching_from_stderr_to_stdout(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        with ConsoleSpinner():
            sys.stderr.write("test_6021_stderr")
            sys.stdout.write("test_6021_stdout")

        stdout, stderr = capsys.readouterr()
        stdout_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_stdout..." + "\r\x1b[2Ktest_6021_stdout\n"
        )
        stderr_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_stderr..." + "\r\x1b[2Ktest_6021_stderr\n"
        )
        assert stdout == stdout_spin_and_final_line
        assert stderr == stderr_spin_and_final_line

    @pytest.mark.parametrize("spins", [1])
    def test_updating_via_print_function(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        # print() works by making two writes to the file/stream:
        # 1. The actual message to write
        # 2. The `end` keyword
        with ConsoleSpinner():
            print("test_6021")

        stdout = capsys.readouterr().out
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert stdout == spin_and_final_line


class Test_UpdateSpinnerMsg:
    def test_as_atomic(self):
        console_spinner = ConsoleSpinner()
        console_spinner._as_atomic = RaiseOnEnterContext()
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            console_spinner._update_spinner_msg("", stream=None)

    @pytest.mark.parametrize("spins", [1])
    def test_first_message_correctly_started(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        console_spinner = ConsoleSpinner()
        console_spinner._update_spinner_msg("test_6021", stream=sys.stdout)
        console_spinner._spinning_msg.stop()

        stdout = capsys.readouterr().out
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert stdout == spin_and_final_line

    @pytest.mark.parametrize("spins", [1])
    def test_message_correctly_updated(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        console_spinner = ConsoleSpinner()
        console_spinner._update_spinner_msg("test_6021_line_1", stream=sys.stdout)
        console_spinner._update_spinner_msg("test_6021_line_2", stream=sys.stdout)
        console_spinner._spinning_msg.stop()

        stdout = capsys.readouterr().out
        msg_1_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_line_1..." + "\r\x1b[2Ktest_6021_line_1\n"
        )
        msg_2_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_line_2..." + "\r\x1b[2Ktest_6021_line_2\n"
        )
        assert stdout == msg_1_spin_and_final_line + msg_2_spin_and_final_line

    @pytest.mark.parametrize("spins", [1])
    def test_not_updating_on_empty_message(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        console_spinner = ConsoleSpinner()
        console_spinner._update_spinner_msg("test_6021", stream=sys.stdout)
        console_spinner._update_spinner_msg("", stream=sys.stdout)
        console_spinner._update_spinner_msg("\n", stream=sys.stdout)
        console_spinner._update_spinner_msg("\t", stream=sys.stdout)
        console_spinner._update_spinner_msg("      ", stream=sys.stdout)
        console_spinner._spinning_msg.stop()

        stdout = capsys.readouterr().out
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert stdout == spin_and_final_line


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
