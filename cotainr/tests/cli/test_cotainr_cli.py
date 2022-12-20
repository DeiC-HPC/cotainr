"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest

from cotainr.cli import CotainrCLI
from .stubs import StubValidSubcommand, StubInvalidSubcommand


class TestConstructor:
    def test_adding_subcommand(self, argparse_options_line, capsys, monkeypatch):
        monkeypatch.setattr(CotainrCLI, "_subcommands", [StubValidSubcommand])
        with pytest.raises(SystemExit):
            CotainrCLI(args=["stubvalidsubcommand", "-h"])
        stdout = capsys.readouterr().out
        assert stdout == (
            "usage: cotainr stubvalidsubcommand [-h] [--kw-arg KW_ARG] pos_arg\n\n"
            "positional arguments:\n"
            "  pos_arg\n\n"
            f"{argparse_options_line}"
            "  -h, --help       show this help message and exit\n"
            "  --kw-arg KW_ARG\n"
        )

    @pytest.mark.parametrize(
        "subcommands",
        (
            [StubInvalidSubcommand],
            [StubInvalidSubcommand] + CotainrCLI._subcommands,
            CotainrCLI._subcommands + [StubInvalidSubcommand],
        ),
    )
    def test_invalid_subcommands(self, subcommands, monkeypatch):
        monkeypatch.setattr(CotainrCLI, "_subcommands", subcommands)
        with pytest.raises(TypeError, match="must be a cotainr.cli.CotainrSubcommand"):
            CotainrCLI(args=[])

    def test_no_subcommands(self, capsys, monkeypatch):
        monkeypatch.setattr(CotainrCLI, "_subcommands", [])
        with pytest.raises(SystemExit):
            CotainrCLI(args=[]).subcommand.execute()
        stdout = capsys.readouterr().out
        assert stdout.startswith("usage: cotainr [-h]\n")
        assert "subcommands:" not in stdout

    @pytest.mark.parametrize(
        "arg, kwarg",
        [
            ("", ""),
            ("another_pos_arg", ""),
            ("", "some_kwarg"),
            ("some_pos_arg", 6021),
        ],
    )
    def test_subcommand_arg_parsing(self, arg, kwarg, capsys, monkeypatch):
        monkeypatch.setattr(CotainrCLI, "_subcommands", [StubValidSubcommand])
        cli = CotainrCLI(args=["stubvalidsubcommand", f"{arg}", f"--kw-arg={kwarg}"])
        cli.subcommand.execute()
        stdout = capsys.readouterr().out
        assert stdout == f"Executed: 'stubvalidsubcommand {arg} --kw-arg={kwarg}'"


class TestHelpMessage:
    cotainr_main_help_msg = (
        # Capsys apparently assumes an 80 char terminal (?) - thus extra '\n'
        "usage: cotainr [-h] {{build,info}} ...\n\n"
        "Build Apptainer/Singularity containers for HPC systems in user space.\n\n"
        "{argparse_options_line}"
        "  -h, --help    show this help message and exit\n\n"
        "subcommands:\n  {{build,info}}\n"
        "    build       Build a container.\n"
        "    info        Obtain info about the state of all required dependencies for\n"
        "                building a container.\n"
    )

    def test_main_help(self, argparse_options_line, capsys):
        with pytest.raises(SystemExit):
            CotainrCLI(args=["--help"])
        stdout = capsys.readouterr().out
        assert stdout == self.cotainr_main_help_msg.format(
            argparse_options_line=argparse_options_line
        )

    def test_missing_subcommand(self, argparse_options_line, capsys):
        with pytest.raises(SystemExit):
            CotainrCLI(args=[]).subcommand.execute()
        stdout = capsys.readouterr().out
        assert stdout == self.cotainr_main_help_msg.format(
            argparse_options_line=argparse_options_line
        )
