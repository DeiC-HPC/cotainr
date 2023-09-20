"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

from pathlib import Path

from cotainr.cli import CotainrSubcommand
from cotainr.tracing import LogSettings


class StubDummyCLI:
    class DummySubcommand:
        def execute(self):
            print("Executed dummy subcommand.")

    def __init__(self, *, args=None):
        self.subcommand = self.DummySubcommand()
        print("Initialized DummyCLI.")


class StubInvalidSubcommand:
    pass


class StubLogSettingsSubcommand(CotainrSubcommand):
    def __init__(self, *, verbosity, log_file_path, no_color):
        self.log_settings = LogSettings(
            verbosity=verbosity, log_file_path=log_file_path, no_color=no_color
        )

    @classmethod
    def add_arguments(cls, *, parser):
        parser.add_argument("--verbosity", type=int)
        parser.add_argument("--log-file-path", type=Path, default=None)
        parser.add_argument("--no-color", action="store_true")

    def execute(self):
        pass


class StubValidSubcommand(CotainrSubcommand):
    def __init__(self, *, pos_arg, kw_arg=None):
        self.pos_arg = pos_arg
        self.kw_arg = kw_arg

    @classmethod
    def add_arguments(cls, *, parser):
        parser.add_argument("pos_arg")
        parser.add_argument("--kw-arg")

    def execute(self):
        print(
            f"Executed: '{self.__class__.__name__.lower()} "
            f"{self.pos_arg} --kw-arg={self.kw_arg}'",
            end="",
        )
