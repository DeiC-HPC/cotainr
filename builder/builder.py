import argparse

# design
# error early
# self decribe commands and options
# simple. Let the works do the work and keep this file only to add options and write help text.
# Wrokers will have an init, verify and a run.


class Build:
    def __init__(self, *, base_image=None, conda_env=None):
        self.base_image = base_image
        self.conda_env = conda_env

        #TODO: custom verification goes here

    def execute(self):
        pass

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--base-image", help="Base image to use for the container."
        )
        parser.add_argument(
            "--conda-env",
            help="Conda environment to install and activate in the container.",
            # type=path
        )


class Info:
    def __init__(self):
        pass

    def execute(self):
        pass

    @staticmethod
    def add_arguments(parser):
        pass


class BuilderCLI:
    def __init__(self):
        # Main command
        parser = argparse.ArgumentParser(
            description="Build containers for running Python on HPC systems."
        )
        subparsers = parser.add_subparsers()

        # TODO: wrap in loop
        # Add build subcommand
        build_parser = subparsers.add_parser("build", help="Build a container.")  # TODO: define help message in Build class
        Build.add_arguments(build_parser)
        build_parser.set_defaults(cmd_class=Build)

        # Add info subcommand
        info_parser = subparsers.add_parser(
            "info",
            help="Obtain info about the state of all required dependencies for building a container.",
        )
        Info.add_arguments(info_parser)
        info_parser.set_defaults(cmd_class=Info)

        # Parse args
        self.args = parser.parse_args()
        cmd_class = self.args.cmd_class
        del self.args.cmd_class
        self.subcommand = cmd_class(**vars(self.args))

    def execute_subcommand(self):
        #return self.subcommand.execute()
        print(self.subcommand.__dict__)


if __name__ == "__main__":
    cli = BuilderCLI()
    cli.execute_subcommand()
