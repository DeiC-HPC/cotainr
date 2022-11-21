import cotainr.cli
from .stubs import StubDummyCLI


class TestMain:
    def test_main(self, capsys, monkeypatch):
        monkeypatch.setattr(cotainr.cli, "CotainrCLI", StubDummyCLI)
        cotainr.cli.main()
        cli_init, subcommand_run = capsys.readouterr().out.strip().split("\n")
        assert cli_init == 'Initialized DummyCLI.'
        assert subcommand_run == "Executed dummy subcommand."
