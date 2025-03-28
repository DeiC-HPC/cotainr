"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import io
import shutil
import time

import pytest

from cotainr.tracing import MessageSpinner

from .stubs import FixedNumberOfSpinsEvent


@pytest.fixture()
def safe_MessageSpinner(msg, stream):
    """
    Setup a MessageSpinner and make sure to stop it during teardown.

    The parameters `msg` and `stream` must be passed to the fixture using a
    pytest parameterization.
    """
    safe_MessageSpinner = MessageSpinner(msg=msg, stream=stream)
    yield safe_MessageSpinner
    safe_MessageSpinner.stop()


class TestStart:
    @pytest.mark.parametrize(["msg", "stream"], [("test 6021", io.StringIO())])
    def test_correct_start(self, msg, stream, safe_MessageSpinner):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        assert not safe_MessageSpinner._running
        assert not safe_MessageSpinner._spinner_thread.is_alive()
        safe_MessageSpinner.start()
        assert safe_MessageSpinner._running
        assert safe_MessageSpinner._spinner_thread.is_alive()

    @pytest.mark.parametrize(["msg", "stream"], [("test 6021", io.StringIO())])
    def test_spinning_started(self, msg, stream, safe_MessageSpinner):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        safe_MessageSpinner.start()
        for _ in range(5):
            # wait for something to be written to the stream
            stream_msg = stream.getvalue()
            if stream_msg:
                break
            else:
                time.sleep(0.2)
        else:
            raise RuntimeError("No message seems to be spinning")

        assert msg in stream_msg


class TestStop:
    @pytest.mark.parametrize(["msg", "stream"], [("test 6021", io.StringIO())])
    def test_stop_before_having_started(self, msg, stream, safe_MessageSpinner):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        assert not safe_MessageSpinner._running
        assert not safe_MessageSpinner._spinner_thread.is_alive()
        safe_MessageSpinner.stop()
        assert not safe_MessageSpinner._running
        assert not safe_MessageSpinner._spinner_thread.is_alive()

    @pytest.mark.parametrize(["msg", "stream"], [("test 6021", io.StringIO())])
    def test_stop_when_running(self, msg, stream, safe_MessageSpinner):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        assert not safe_MessageSpinner._running
        assert not safe_MessageSpinner._spinner_thread.is_alive()
        safe_MessageSpinner.start()
        assert safe_MessageSpinner._running
        assert safe_MessageSpinner._spinner_thread.is_alive()
        safe_MessageSpinner.stop()
        assert not safe_MessageSpinner._running
        assert not safe_MessageSpinner._spinner_thread.is_alive()


class Test_SpinMsg:
    @pytest.mark.parametrize(
        ["msg", "stream", "no_ansi_msg"],
        [
            (
                # non SGR escape codes
                "\033[Asome_long\x1b[A_message_w\x1b[2;Eith_a_\x1b[5;3;Hlot_of_"
                "AN\x1b[KSI_codes_\x1b[B6021",
                io.StringIO(),
                "some_long_message_with_a_lot_of_ANSI_codes_6021",
            ),
            (
                # "message_with_SGRs"
                "\x1b[38;5;8mmess\x1b[38;5;8mage_with\x1b[38;5;1m_\x1b[38;5;160mSGRs"
                "\x1b[0m",
                io.StringIO(),
                "\x1b[38;5;8mmess\x1b[38;5;8mage_with\x1b[38;5;1m_\x1b[38;5;160mSGRs"
                "\x1b[0m",
            ),
        ],
    )
    def test_ansi_escape_codes_removal(
        self, msg, stream, no_ansi_msg, safe_MessageSpinner, monkeypatch
    ):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        monkeypatch.setattr(
            safe_MessageSpinner, "_stop_signal", FixedNumberOfSpinsEvent(spins=0)
        )
        safe_MessageSpinner._spin_msg()

        stream_msg = stream.getvalue().rstrip("\n")
        # This implements stream_msg.removeprefix() which is found in Python >= 3.9
        if stream_msg.startswith(safe_MessageSpinner._clear_line_code):
            stream_msg = stream_msg[len(safe_MessageSpinner._clear_line_code) :]

        assert stream_msg == no_ansi_msg

    @pytest.mark.parametrize(
        ["msg", "stream", "no_newline_msg"],
        [
            ("test 6021\n", io.StringIO(), "test 6021"),
            ("test 6021\n\n", io.StringIO(), "test 6021"),
            ("\ntest\n 60\n21", io.StringIO(), "\ntest\n 60\n21"),
            ("\ntest\n 60\n21\n", io.StringIO(), "\ntest\n 60\n21"),
            (
                "\x1b[38;5;8mtest 6021\x1b[0m\n",
                io.StringIO(),
                "\x1b[38;5;8mtest 6021\x1b[0m",
            ),
            (
                "\x1b[38;5;8mtest 6021\n\x1b[0m",
                io.StringIO(),
                "\x1b[38;5;8mtest 6021\x1b[0m",
            ),
            (
                "\x1b[38;5;8mtest 6021\n\n\x1b[0m",
                io.StringIO(),
                "\x1b[38;5;8mtest 6021\x1b[0m",
            ),
            (
                "\n\x1b[38;5;8m\ntest 60\n21\n\n\x1b[0m",
                io.StringIO(),
                "\n\x1b[38;5;8m\ntest 60\n21\x1b[0m",
            ),
        ],
    )
    def test_newline_at_end_removal(
        self, msg, stream, no_newline_msg, safe_MessageSpinner, monkeypatch
    ):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        monkeypatch.setattr(
            safe_MessageSpinner, "_stop_signal", FixedNumberOfSpinsEvent(spins=0)
        )
        safe_MessageSpinner._spin_msg()

        stream_msg = stream.getvalue().rstrip("\n")
        # This implements stream_msg.removeprefix() which is found in Python >= 3.9
        if stream_msg.startswith(safe_MessageSpinner._clear_line_code):
            stream_msg = stream_msg[len(safe_MessageSpinner._clear_line_code) :]

        assert stream_msg == no_newline_msg

    @pytest.mark.parametrize(["msg", "stream"], [("test 6021", io.StringIO())])
    def test_spinner_cycle(self, msg, stream, safe_MessageSpinner, monkeypatch):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        monkeypatch.setattr(
            safe_MessageSpinner,
            "_stop_signal",
            FixedNumberOfSpinsEvent(spins=16),  # Two full cycles
        )
        expected_spin_output = (
            "\r\x1b[2K⣾ test 6021..."
            "\r\x1b[2K⣷ test 6021..."
            "\r\x1b[2K⣯ test 6021..."
            "\r\x1b[2K⣟ test 6021..."
            "\r\x1b[2K⡿ test 6021..."
            "\r\x1b[2K⢿ test 6021..."
            "\r\x1b[2K⣻ test 6021..."
            "\r\x1b[2K⣽ test 6021..."
        ) * 2 + "\r\x1b[2Ktest 6021\n"
        safe_MessageSpinner._spin_msg()
        stream_msg = stream.getvalue()
        assert stream_msg == expected_spin_output

    @pytest.mark.parametrize(
        ["msg", "stream"],
        [
            (
                "some_message_longer_than_terminal_width"
                + "!" * shutil.get_terminal_size()[0],
                io.StringIO(),
            )
        ],
    )
    def test_one_line_msg(self, msg, stream, safe_MessageSpinner, monkeypatch):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        monkeypatch.setattr(
            safe_MessageSpinner, "_stop_signal", FixedNumberOfSpinsEvent(spins=1)
        )
        exclamation_marks = shutil.get_terminal_size()[0] - len(
            "⣾ some_message_longer_than_terminal_width..."
        )
        expected_one_line_msg = (
            f"⣾ some_message_longer_than_terminal_width{'!' * exclamation_marks}..."
        )
        safe_MessageSpinner._spin_msg()
        one_line_stream_msg = stream.getvalue().split("\r\x1b[2K")[1]
        assert one_line_stream_msg == expected_one_line_msg

    @pytest.mark.parametrize(
        ["msg", "stream"],
        [
            (
                "some_message_longer_than_terminal_width"
                + "!" * shutil.get_terminal_size()[0],
                io.StringIO(),
            )
        ],
    )
    def test_print_final_full_message(
        self, msg, stream, safe_MessageSpinner, monkeypatch
    ):
        # The `msg` and `stream` parameters are passed automagically to the
        # `safe_MessageSpinner` fixture.
        monkeypatch.setattr(
            safe_MessageSpinner, "_stop_signal", FixedNumberOfSpinsEvent(spins=1)
        )
        safe_MessageSpinner._spin_msg()
        final_stream_msg = stream.getvalue().split("\r\x1b[2K")[-1]
        assert final_stream_msg == msg + "\n"
