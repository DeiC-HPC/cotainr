import pytest

from cotainr.cli import BuilderCLI


class TestConstructor:
    class StubInvalidSubcommand:  # TODO: move to stubs.py module
        pass

    class StubValidSubcommand:
        pass

    def test_adding_subparser(self):
        # able to run a valid subcommand added to the list of subcommands
        raise NotImplementedError("Test not implemented'")

    @pytest.mark.parametrize(
        "subcommands",
        (
            [],
            [StubInvalidSubcommand],
            [StubInvalidSubcommand] + BuilderCLI.subcommands,
            BuilderCLI.subcommands + [StubInvalidSubcommand],
        ),
    )
    def test_invalid_subparser(self, subcommands, monkeypatch):
        # reasonable failure on specifying invalid subcommmand list
        # TODO: convert to a parametrized patch
        monkeypatch.setattr(BuilderCLI, "subcommands", subcommands)
        raise NotImplementedError("Test not implemented'")

    def test_subcommand_arg_parsing(self):
        # all arguments are passed on to sub-command
        raise NotImplementedError("Test not implemented'")


class TestHelpMessage:
    def test_main_help(self):
        # program name
        # description
        # listing of subcommands
        raise NotImplementedError("Test not implemented'")

    def test_subcommand_help(self):
        # name
        # description
        # help
        raise NotImplementedError("Test not implemented'")

    def test_missing_subcommand(self):
        # help for main command is showed when no subcommand given
        raise NotImplementedError("Test not implemented'")
