"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest
import cotainr.util


class TestAnswerYes:
    @pytest.mark.parametrize("outp", ["Test!", "Test\nTest", "Whoop!", "\n", "\nTest!"])
    def test_output(self, capsys, outp, factory_mock_input, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(""))
        answer = cotainr.util.answer_is_yes(outp)
        stdout = capsys.readouterr().out

        assert outp in stdout
        assert not answer

    @pytest.mark.parametrize("inp", ["n", "nope", "no", "NO!", "Not gonna happen"])
    def test_n(self, inp, factory_mock_input, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(inp))

        answer = cotainr.util.answer_is_yes("")

        assert not answer

    @pytest.mark.parametrize(
        "inp",
        [
            "i",
            "!",
            " ",
            "O!",
            "Anbsolutely not",
            "haha",
            "I don't know",
            "yse",
            "You know it",
        ],
    )
    def test_not_recognized(self, capsys, inp, factory_mock_input, monkeypatch):
        inputs = [inp, "yes"]
        monkeypatch.setattr("builtins.input", factory_mock_input(inputs))

        answer = cotainr.util.answer_is_yes("")
        stdout = capsys.readouterr().out

        assert "Did not understand your input. Please answer yes/[N]o" in stdout
        assert answer

    @pytest.mark.parametrize("inp", ["YES", "YEs", "Yes", "YeS", "yes", "yES", "yeS"])
    def test_y(self, inp, factory_mock_input, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(inp))

        answer = cotainr.util.answer_is_yes("")

        assert answer
