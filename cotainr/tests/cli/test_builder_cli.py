import pytest

from cotainr.cli import BuilderCLI
from .stubs import StubValidSubcommand, StubInvalidSubcommand


class TestConstructor:
    def test_adding_subcommand(self, capsys, monkeypatch, argparse_options_line):
        monkeypatch.setattr(BuilderCLI, "_subcommands", [StubValidSubcommand])
        with pytest.raises(SystemExit):
            BuilderCLI(args=["stubvalidsubcommand", "-h"])
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
            [StubInvalidSubcommand] + BuilderCLI._subcommands,
            BuilderCLI._subcommands + [StubInvalidSubcommand],
        ),
    )
    def test_invalid_subcommands(self, subcommands, monkeypatch):
        monkeypatch.setattr(BuilderCLI, "_subcommands", subcommands)
        with pytest.raises(TypeError, match="must be a cotainr.cli.BuilderSubcommand"):
            BuilderCLI(args=[])

    def test_no_subcommands(self, capsys, monkeypatch):
        monkeypatch.setattr(BuilderCLI, "_subcommands", [])
        with pytest.raises(SystemExit):
            BuilderCLI(args=[]).subcommand.execute()
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
        monkeypatch.setattr(BuilderCLI, "_subcommands", [StubValidSubcommand])
        cli = BuilderCLI(args=["stubvalidsubcommand", f"{arg}", f"--kw-arg={kwarg}"])
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

    def test_main_help(self, capsys, argparse_options_line):
        with pytest.raises(SystemExit):
            BuilderCLI(args=["--help"])
        stdout = capsys.readouterr().out
        assert stdout == self.cotainr_main_help_msg.format(
            argparse_options_line=argparse_options_line
        )

    def test_subcommand_help(self, capsys, argparse_options_line):
        with pytest.raises(SystemExit):
            BuilderCLI(args=["build", "--help"])
        stdout = capsys.readouterr().out
        assert stdout == (
            # Capsys apparently assumes an 80 char terminal (?) - thus extra '\n'
            "usage: cotainr build [-h] --base-image BASE_IMAGE [--conda-env CONDA_ENV]\n"
            "                     image_path\n\n"
            "Build a container.\n\n"
            "positional arguments:\n"
            "  image_path            path to the built container image\n\n"
            f"{argparse_options_line}"
            "  -h, --help            show this help message and exit\n"
            "  --base-image BASE_IMAGE\n"
            "                        base image to use for the container which may be any\n"
            "                        valid apptainer/singularity <build spec>\n"
            "  --conda-env CONDA_ENV\n"
            "                        path to a conda environment.yml file to install and\n"
            "                        activate in the container\n"
        )

    def test_missing_subcommand(self, capsys, argparse_options_line):
        with pytest.raises(SystemExit):
            BuilderCLI(args=[]).subcommand.execute()
        stdout = capsys.readouterr().out
        assert stdout == self.cotainr_main_help_msg.format(
            argparse_options_line=argparse_options_line
        )
