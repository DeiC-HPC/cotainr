"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest
import cotainr.util


class TestAnswerYes:
    def test_empty(self, capsys, factory_mock_input,monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(""))
        answer = cotainr.util.answer_yes("")

        assert not answer

    @pytest.mark.parametrize("outp", ["Test!","Test\nTest","Whoop!","\n","\nTest!"])
    @pytest.mark.parametrize("inp", ["Test!","no", "!", "NO!", "Whoop", "Everybody!","YES!"])
    def test_non_yes(self, capsys, outp, inp, factory_mock_input,monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(inp))

        answer = cotainr.util.answer_yes(outp)
        stdout = capsys.readouterr().out

        assert outp in stdout
        assert not answer

    @pytest.mark.parametrize("outp", ["Test!","Test\nTest","Whoop!","\n","\nTest!"])
    @pytest.mark.parametrize("inp", ["YES","YEs", "Yes", "YeS", "yes", "yES","yeS"])
    def test_yes(self, capsys, outp, inp, factory_mock_input,monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(inp))

        answer = cotainr.util.answer_yes(outp)
        stdout = capsys.readouterr().out

        assert outp in stdout
        assert answer
