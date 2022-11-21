from cotainr.cli import CotainrSubcommand


class StubDummyCLI:
    class DummySubcommand:
        def execute(self):
            print("Executed dummy subcommand.")

    def __init__(self, *, args=None):
        self.subcommand = self.DummySubcommand()
        print("Initialized DummyCLI.")


class StubInvalidSubcommand:
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
