"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import concurrent.futures
import sys

import pytest

from cotainr.tracing import ConsoleSpinner, StreamWriteProxy, console_lock

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
        assert console_spinner._in_nested_context_count == 0


class TestContext:
    def test_correctly_handling_input(self, factory_mock_input, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input("some_input_6021"))
        with ConsoleSpinner():
            input("please_input_some_text_6021")

        stdout = capsys.readouterr().out
        assert stdout == "please_input_some_text_6021"

    def test_correctly_setting_nested_context_count(self):
        console_spinner = ConsoleSpinner()
        assert not console_lock.locked()
        with ConsoleSpinner() as level_1_spinner:
            assert console_lock.locked()
            assert level_1_spinner._in_nested_context_count == 0
            with console_spinner as outer_spinner:
                assert console_lock.locked()
                assert level_1_spinner._in_nested_context_count == 0
                assert outer_spinner._in_nested_context_count == 1
                with console_spinner:
                    assert console_lock.locked()
                    assert level_1_spinner._in_nested_context_count == 0
                    assert outer_spinner._in_nested_context_count == 2
                    with ConsoleSpinner() as level_2_spinner:
                        assert console_lock.locked()
                        assert level_1_spinner._in_nested_context_count == 0
                        assert outer_spinner._in_nested_context_count == 2
                        assert level_2_spinner._in_nested_context_count == 1

                    assert console_lock.locked()
                    assert level_1_spinner._in_nested_context_count == 0
                    assert outer_spinner._in_nested_context_count == 2

                assert console_lock.locked()
                assert level_1_spinner._in_nested_context_count == 0
                assert outer_spinner._in_nested_context_count == 1

            assert console_lock.locked()
            assert level_1_spinner._in_nested_context_count == 0

        assert not console_lock.locked()

    @pytest.mark.parametrize("spins", [1])
    def test_correctly_spinning_stdout_msg(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        with ConsoleSpinner():
            sys.stdout.write("test_6021")

        stdout = capsys.readouterr().out
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert stdout == spin_and_final_line

    @pytest.mark.parametrize("spins", [1])
    def test_correctly_spinning_stderr_msg(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        with ConsoleSpinner():
            sys.stderr.write("test_6021")

        stderr = capsys.readouterr().err
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert stderr == spin_and_final_line

    @pytest.mark.parametrize("spins", [1])
    def test_create_entering_multiple_context_swap(
        self,
        spins,
        capsys,
        monkeypatch,
        factory_mock_input,
        patch_fix_number_of_message_spins,
    ):
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        monkeypatch.setattr("builtins.input", factory_mock_input())
        console_spinner_1 = ConsoleSpinner()
        console_spinner_2 = ConsoleSpinner()
        with console_spinner_2:
            sys.stdout.write("test_6021_level_1")
            with console_spinner_1:
                input("level_5_test_input_6021")
                sys.stdout.write("test_6021_level_2")

        stdout = capsys.readouterr().out
        level_1_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_level_1..." + "\r\x1b[2Ktest_6021_level_1\n"
        )
        level_2_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_level_2..." + "\r\x1b[2Ktest_6021_level_2\n"
        )
        assert stdout == (
            level_1_spin_and_final_line
            + "level_5_test_input_6021"
            + level_2_spin_and_final_line
        )

    @pytest.mark.parametrize("spins", [1])
    def test_entering_multiple_context(
        self,
        spins,
        capsys,
        monkeypatch,
        factory_mock_input,
        patch_fix_number_of_message_spins,
    ):
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        monkeypatch.setattr("builtins.input", factory_mock_input())
        console_spinner = ConsoleSpinner()
        with ConsoleSpinner():
            sys.stdout.write("test_6021_level_1")
            with console_spinner:
                sys.stdout.write("test_6021_level_2")
                with console_spinner:
                    with ConsoleSpinner():
                        sys.stdout.write("test_6021_level_4")
                        with ConsoleSpinner():
                            input("level_5_test_input_6021")
                            with ConsoleSpinner(), console_spinner:
                                sys.stdout.write("test_6021_level_7")

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
        level_7_spin_and_final_line = (
            "\r\x1b[2K⣾ test_6021_level_7..." + "\r\x1b[2Ktest_6021_level_7\n"
        )
        assert stdout == (
            level_1_spin_and_final_line
            + level_2_spin_and_final_line
            + level_4_spin_and_final_line
            + "level_5_test_input_6021"
            + level_7_spin_and_final_line
        )

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
    def test_switching_from_stdout_to_stderr(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
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
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
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

    @pytest.mark.parametrize(
        ["spins", "num_tasks"], [(1, 1), (1, 5), (1, 10), (1, 20), (1, 100), (1, 200)]
    )
    def test_threadpool_console_spinner_race_condition(
        self, spins, num_tasks, capsys, patch_fix_number_of_message_spins
    ):
        # This is a bit of a wacky test for the case where one starts multiple
        # threads with individual ConsoleSpinner objects. Only one
        # ConsoleSpinner object can control the stdout manipulation, so when
        # this "main" context is exited in one thread, the spinner disappears
        # in all other threads as well if they haven't managed to start the
        # spinning message yet. This creates a race condition which we only
        # handle by making sure that the message is indeed still printed,
        # though without a spinner. The number of threads that don't get to
        # have a spinner becomes random which is why we test multiple values
        # for the number of tasks in the hope that at least one of them trigger
        # this race condition.

        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        def spin_msg_func():
            with ConsoleSpinner():
                sys.stdout.write("test_6021")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_tasks, thread_name_prefix="console_spinner_thread"
        ) as executor:
            futures = [executor.submit(spin_msg_func) for _ in range(num_tasks)]

        stdout = capsys.readouterr().out
        stdout_lines = stdout.split("\n")
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021"
        assert all(future.exception() is None for future in futures)
        for line in stdout_lines[:-1]:
            assert line == spin_and_final_line
        assert stdout_lines[-1] == "test_6021" * (num_tasks - (len(stdout_lines) - 1))

    @pytest.mark.parametrize(["spins", "num_tasks"], [(1, 1), (1, 5), (1, 10)])
    def test_threadpool_same_console_spinner(
        self, spins, num_tasks, capsys, patch_fix_number_of_message_spins
    ):
        # Having all these ConsoleSpinnner context wrap each other get very
        # costly in terms of lock acquiring times which is why limit ourself to
        # 10 tasks max in this unit test.

        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        def spin_msg_func():
            with ConsoleSpinner():
                sys.stdout.write("test_6021")

        with ConsoleSpinner():
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=num_tasks, thread_name_prefix="console_spinner_thread"
            ) as executor:
                futures = [executor.submit(spin_msg_func) for _ in range(num_tasks)]

        stdout = capsys.readouterr().out
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert all(future.exception() is None for future in futures)
        assert stdout == spin_and_final_line * num_tasks

    @pytest.mark.parametrize("spins", [1])
    def test_updating_via_print_function(
        self, spins, capsys, patch_fix_number_of_message_spins
    ):
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.

        # print() works by making two writes to the file/stream:
        # 1. The actual message to write
        # 2. The `end` keyword
        with ConsoleSpinner():
            print("test_6021")

        stdout = capsys.readouterr().out
        spin_and_final_line = "\r\x1b[2K⣾ test_6021..." + "\r\x1b[2Ktest_6021\n"
        assert stdout == spin_and_final_line


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
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        with console_lock:
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
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        with console_lock:
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
        # The `spins` parameter is passed automagically to the
        # `patch_fix_number_of_message_spins` fixture.
        with console_lock:
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

    def test_updating_message_outside_console_lock(self, capsys):
        console_spinner = ConsoleSpinner()
        console_spinner._update_spinner_msg("test_6021", stream=sys.stdout)
        stdout = capsys.readouterr().out
        assert stdout == "test_6021"


class Test_ThreadSafeInput:
    def test_lock(self):
        console_spinner = ConsoleSpinner()
        console_spinner._lock = RaiseOnEnterContext()
        wrapped_input_func = console_spinner._thread_safe_input(lambda: None)
        with pytest.raises(NotImplementedError, match=r"^Entered context$"):
            wrapped_input_func()

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
