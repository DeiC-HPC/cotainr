"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import cotainr.cli

from .stubs import StubDummyCLI


class TestMain:
    def test_main(self, capsys, monkeypatch):
        monkeypatch.setattr(cotainr.cli, "CotainrCLI", StubDummyCLI)
        cotainr.cli.main()
        cli_init, subcommand_run = capsys.readouterr().out.strip().split("\n")
        assert cli_init == "Initialized DummyCLI."
        assert subcommand_run == "Executed dummy subcommand."
