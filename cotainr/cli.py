"""
Command line interface for Cotainr
Created by DeiC, deic.dk

The classes in this module implements the command line main command and
subcommands.

Classes
-------
BuilderSubcommand(ABC):
    Abstract base class for `BuilderCLI` subcommands.
BuilderCLI
    Build Apptainer/Singularity containers for HPC systems in user space. (The
    main CLI command.)
Build
    Build a container. (The "build" subcommand.)
Info
    Obtain info about the state of all required dependencies for building a
    container. (The "info" subcommand.)
"""

from abc import ABC, abstractmethod
import argparse
import pathlib

from . import container
from . import pack


class BuilderSubcommand(ABC):
    """Abstract base class for `BuilderCLI` subcommands."""

    @classmethod
    def add_arguments(cls, *, parser):
        """
        Add command line arguments to arguments `parser`.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The argument parser to add arguments to.
        """
        pass

    @abstractmethod
    def execute(self):
        """Execute the subcommand."""
        pass


class Build(BuilderSubcommand):
    """
    Build a container.

    The "build" subcommand.

    Parameters
    ----------
    image_path : os.PathLike
        Path to the built container image.
    base_image : str
        Base image to use for the container which may be any valid
        Apptainer/Singularity <BUILD SPEC>.
    conda_env : os.PathLike, optional
        Path to a Conda environment.yml file to install and activate in the
        container.
    """

    def __init__(self, *, image_path, base_image=None, conda_env=None):
        self.image_path = image_path.absolute()
        self.base_image = base_image
        if conda_env is not None:
            self.conda_env = conda_env.absolute()
            if not self.conda_env.exists():
                raise FileNotFoundError(
                    f"The provided Conda env file '{self.conda_env}' does not exist."
                )

    @classmethod
    def add_arguments(cls, *, parser):
        parser.add_argument(
            "image_path",
            help=_extract_help_from_docstring(arg="image_path", docstring=cls.__doc__),
            type=pathlib.Path,
        )
        parser.add_argument(
            "--base-image",
            required=True,
            help=_extract_help_from_docstring(arg="base_image", docstring=cls.__doc__),
        )
        parser.add_argument(
            "--conda-env",
            help=_extract_help_from_docstring(arg="conda_env", docstring=cls.__doc__),
            type=pathlib.Path,
        )

    def execute(self):
        with container.SingularitySandbox(base_image=self.base_image) as sandbox:
            if self.conda_env is not None:
                # Install supplied conda env
                conda_install = pack.CondaInstall(sandbox=sandbox)
                conda_env_name = "conda_container_env"
                conda_install.add_environment(path=self.conda_env, name=conda_env_name)
                sandbox.add_to_env(shell_script=f"conda activate {conda_env_name}")
                conda_install.cleanup_unused_files()

            sandbox.build_image(path=self.image_path)


class Info(BuilderSubcommand):
    """
    Obtain info about the state of all required dependencies for building a container.

    The "info" subcommand.
    """

    def execute(self):
        print("Sorry, no information about your system is available at this time.")


class BuilderCLI:
    """
    Build Apptainer/Singularity containers for HPC systems in user space.

    The main CLI command.

    Attributes
    ----------
    args : types.SimpleNamespace
        The parsed arguments to the CLI.
    subcommand : BuilderSubcommand
        The subcommand to run.
    """

    def __init__(self):
        """Create a command line interface for the container builder."""
        # Setup main command parser
        builder_cli_doc_summary = self.__doc__.strip().splitlines()[0]
        parser = argparse.ArgumentParser(description=builder_cli_doc_summary)
        subparsers = parser.add_subparsers(title="subcommands")

        # Add subcommands parsers
        subcommands = [Build, Info]
        for subcommand_cls in subcommands:
            subcommand_doc_summary = subcommand_cls.__doc__.strip().splitlines()[0]
            sub_parser = subparsers.add_parser(
                name=subcommand_cls.__name__.lower(),
                help=subcommand_doc_summary,
                description=subcommand_doc_summary,
            )
            subcommand_cls.add_arguments(parser=sub_parser)
            sub_parser.set_defaults(subcommand_cls=subcommand_cls)

        # Parse args
        self.args = parser.parse_args()
        subcommand_args = {
            key: val for key, val in vars(self.args).items() if key != "subcommand_cls"
        }

        try:
            self.subcommand = self.args.subcommand_cls(**subcommand_args)
        except AttributeError:
            # Print help if no subcommand was given
            class NoSubcommand:
                def execute(self):
                    parser.print_help()

            self.subcommand = NoSubcommand()


def main(*args, **kwargs):
    """Main CLI entrypoint."""
    # Create BuilderCLI to parse command line args and run the specified
    # subcommand
    cli = BuilderCLI()
    cli.subcommand.execute()


def _extract_help_from_docstring(*, arg, docstring):
    """
    Extract the description of `arg` in `string`.

    Parameters
    ----------
    arg : str
        The name of the argument.
    docstring : str
        The numpydoc docstring in which `arg` is documented.

    Raises
    ------
    KeyError
        If the docstring does not include `arg`.
    """
    arg_found = False
    arg_desc = []
    for line in docstring.splitlines():
        if arg_found:
            if " : " in line or line.strip() == "":
                # No more description lines, return the description
                return "".join(arg_desc).strip().lower().rstrip(".")
            else:
                # Extract line as part of arg description
                arg_desc.extend([line, " "])
        elif f"{arg} : " in line:
            # We found the requested arg in the docstring
            arg_found = True
    else:
        # We didn't find the arg in the docstring
        raise KeyError(f"The docstring does not include {arg=}")
