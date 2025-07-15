"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest

from cotainr.util import answer_is_yes


class TestAnswerYes:
    @pytest.mark.parametrize("input_text", ["no", "No", "nO", "NO"])
    def test_answering_no(self, input_text, factory_mock_input, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(input_text))
        assert not answer_is_yes("some_answer_prompt")

    @pytest.mark.parametrize(
        "input_text", ["yes", "Yes", "yEs", "yeS", "YEs", "YeS", "yES", "YES"]
    )
    def test_answering_yes(self, input_text, factory_mock_input, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(input_text))
        assert answer_is_yes("some_answer_prompt")

    @pytest.mark.parametrize(
        "input_text",
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
            "n",
            "N",
            "nope",
            "NO!",
            "Not gonna happen",
            "y",
            "Y",
        ],
    )
    def test_not_recognized(self, capsys, input_text, factory_mock_input, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(input_text))
        assert not answer_is_yes("some_answer_prompt", max_attempts=2)
        assert (
            f'You answered "{input_text}". Please answer yes or no.\n>>> '
            in capsys.readouterr().out
        )

    @pytest.mark.parametrize("max_attempts", [1, 2, 10, 1000])
    def test_too_many_attempts(
        self, max_attempts, factory_mock_input_sequence, monkeypatch, caplog
    ):
        input_sequence = ["Why do I keep answering this question?"] * max_attempts + [
            "yes"
        ]
        monkeypatch.setattr(
            "builtins.input", factory_mock_input_sequence(input_sequence)
        )
        assert not answer_is_yes("some_answer_prompt", max_attempts=max_attempts)
        assert (
            f'You provided an invalid answer {max_attempts} times in a row. Now assuming you meant "no".'
            in caplog.text
        )
