"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""
import contextlib
import sys

import pytest

import cotainr.tracing
from cotainr.tracing import ConsoleSpinner, StreamWriteProxy
from .patches import patch_fix_number_of_message_spins
from .stubs import RaiseOnEnterContext


class TestConstructor:
    def test_attributes(self):
        console_spinner = ConsoleSpinner()
        assert isinstance(console_spinner._stdout_proxy, StreamWriteProxy)
        assert console_spinner._stdout_proxy._stream is sys.stdout
        assert isinstance(console_spinner._stderr_proxy, StreamWriteProxy)
        assert console_spinner._stderr_proxy._stream is sys.stderr
        assert console_spinner._true_input_func is input
        assert console_spinner._spinning_msg is None
        assert not console_spinner._nested_context


class TestContext:
    def test_correctly_handling_input(self, factory_mock_input, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input("some_input_6021"))
        with ConsoleSpinner():
            input("please_input_some_text_6021")

        stdout = capsys.readouterr().out
        assert stdout == "please_input_some_text_6021"

    def test_correctly_setting_nested_context_flag(self):
        with ConsoleSpinner() as level_1_spinner:
            assert not level_1_spinner._nested_context
            with ConsoleSpinner() as level_2_spinner:
                assert not level_1_spinner._nested_context
                assert level_2_spinner._nested_context

            assert not level_1_spinner._nested_context

    def test_correctly_setting_within_context_flag(self):
        assert not cotainr.tracing._within_console_spinner_context
        with ConsoleSpinner():
            assert cotainr.tracing._within_console_spinner_context
        assert not cotainr.tracing._within_console_spinner_context

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

    def test_exiting_context_with_spinning_msg(self, capsys):
        with ConsoleSpinner():
            sys.stdout.write("test_6021")

        stdout, stderr = capsys.readouterr()
        assert stdout.endswith("\r\x1b[2Ktest_6021\n")
        assert not stderr

    def test_exiting_context_without_spinning_msg(self, capsys):
        with ConsoleSpinner():
            pass

        stdout, stderr = capsys.readouterr()
        assert not stdout
        assert not stderr

    def test_lock_enter(self):
        console_spinner = ConsoleSpinner()
        console_spinner._lock = RaiseOnEnterContext()
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            console_spinner.__enter__()

    def test_lock_exit(self):
        console_spinner = ConsoleSpinner()
        console_spinner._lock = RaiseOnEnterContext()
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            console_spinner.__exit__(None, None, None)

    def test_return_self(self):
        with ConsoleSpinner() as console_spinner:
            assert isinstance(console_spinner, ConsoleSpinner)

    @pytest.mark.parametrize("spins", [1])
    def test_reentering_context(
        self,
        spins,
        capsys,
        monkeypatch,
        factory_mock_input,
        patch_fix_number_of_message_spins,
    ):
        monkeypatch.setattr("builtins.input", factory_mock_input())
        with ConsoleSpinner():
            sys.stdout.write("test_6021_level_1")
            with ConsoleSpinner():
                sys.stdout.write("test_6021_level_2")
                with ConsoleSpinner():
                    with ConsoleSpinner():
                        sys.stdout.write("test_6021_level_4")
                        with ConsoleSpinner():
                            input("level_5_test_input_6021")

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
            + "level_5_test_input_6021"
        )

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


class Test_Disable:
    def test_lock(self):
        console_spinner = ConsoleSpinner()
        console_spinner._lock = RaiseOnEnterContext()
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            with console_spinner._disable():
                pass

    def test_correctly_disabling_spinner(self, capsys):
        with ConsoleSpinner() as console_spinner:
            with console_spinner._disable():
                sys.stdout.write("test_6021")

        stdout = capsys.readouterr().out
        assert stdout == "test_6021"

    def test_raise_on_disable_outside_context(self):
        console_spinner = ConsoleSpinner()
        with pytest.raises(
            ValueError,
            match=(
                r"^Disabling the spinner is only allowed inside "
                r"the ConsoleSpinner context.$"
            ),
        ):
            with console_spinner._disable():
                pass


class Test_UpdateSpinnerMsg:
    def test_lock(self):
        console_spinner = ConsoleSpinner()
        console_spinner._lock = RaiseOnEnterContext()
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
    def test_lock(self):
        console_spinner = ConsoleSpinner()
        console_spinner._lock = RaiseOnEnterContext()
        wrapped_input_func = console_spinner._thread_safe_input(lambda: None)
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            wrapped_input_func()

    def test_disable_console_spinner(self, monkeypatch):
        @contextlib.contextmanager
        def raise_on_disable():
            raise NotImplementedError("Entered disable context!")

        console_spinner = ConsoleSpinner()
        console_spinner._disable = raise_on_disable
        with pytest.raises(NotImplementedError, match=r"^Entered disable context!$"):
            console_spinner._thread_safe_input(input)()

    def test_stop_spinning_msg(self):
        class DummyMsg:
            def stop(self):
                pass

        console_spinner = ConsoleSpinner()
        console_spinner._spinning_msg = DummyMsg()
        with console_spinner:
            console_spinner._thread_safe_input(lambda: None)()
            assert console_spinner._spinning_msg is None

    def test_wrap_input_func(self):
        def my_input_func():
            return "test_6021"

        with ConsoleSpinner() as console_spinner:
            assert console_spinner._thread_safe_input(my_input_func)() == "test_6021"
