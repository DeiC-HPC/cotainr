"""
Command line interface for Cotainr
Created by DeiC, deic.dk

The classes in this module implements the command line main command and
subcommands.

Classes
-------
CotainrSubcommand(ABC)
    Abstract base class for `CotainrCLI` subcommands.
CotainrCLI
    Build Apptainer/Singularity containers for HPC systems in user space. (The
    main CLI command.)
Build
    Build a container. (The "build" subcommand.)
Info
    Obtain info about the state of all required dependencies for building a
    container. (The "info" subcommand.)

Functions
---------
main(\*args, \*\*kwargs)
    Main CLI entrypoint.
"""

from abc import ABC, abstractmethod
import argparse
from pathlib import Path
import shutil
import sys

from . import container
from . import pack


class CotainrSubcommand(ABC):
    """Abstract base class for `CotainrCLI` subcommands."""

    @classmethod
    def add_arguments(cls, *, parser):
        """
        Add command line arguments to arguments `parser`.

        Parameters
        ----------
        parser : :class:`argparse.ArgumentParser`
            The argument parser to add arguments to.
        """
        pass

    @abstractmethod
    def execute(self):
        """Execute the subcommand."""
        pass


class Build(CotainrSubcommand):
    """
    Build a container.

    The "build" subcommand.

    Parameters
    ----------
    image_path : :class:`os.PathLike`
        Path to the built container image.
    base_image : str
        Base image to use for the container which may be any valid
        Apptainer/Singularity <BUILD SPEC>.
    conda_env : :class:`os.PathLike`, optional
        Path to a Conda environment.yml file to install and activate in the
        container.
    """

    def __init__(self, *, image_path, base_image, conda_env=None):
        self.image_path = Path(image_path).resolve()
        if self.image_path.exists():
            val = input(
                f"{self.image_path} already exists. Would you like to overwrite it? (y/N) "
            ).lower()
            if val != "y":
                sys.exit(0)

        self.base_image = base_image
        if conda_env is not None:
            self.conda_env = Path(conda_env).resolve()
            if not self.conda_env.exists():
                raise FileNotFoundError(
                    f"The provided Conda env file '{self.conda_env}' does not exist."
                )
        else:
            self.conda_env = None

    @classmethod
    def add_arguments(cls, *, parser):
        parser.add_argument(
            "image_path",
            help=_extract_help_from_docstring(arg="image_path", docstring=cls.__doc__),
            type=Path,
        )
        parser.add_argument(
            "--base-image",
            required=True,
            help=_extract_help_from_docstring(arg="base_image", docstring=cls.__doc__),
        )
        parser.add_argument(
            "--conda-env",
            help=_extract_help_from_docstring(arg="conda_env", docstring=cls.__doc__),
            type=Path,
        )

    def execute(self):
        with container.SingularitySandbox(base_image=self.base_image) as sandbox:
            if self.conda_env is not None:
                # Install supplied conda env
                conda_env_name = "conda_container_env"
                conda_env_file = sandbox.sandbox_dir / self.conda_env.name
                shutil.copyfile(self.conda_env, conda_env_file)
                conda_install = pack.CondaInstall(sandbox=sandbox)
                conda_install.add_environment(path=conda_env_file, name=conda_env_name)
                sandbox.add_to_env(shell_script=f"conda activate {conda_env_name}")
                conda_install.cleanup_unused_files()

            sandbox.build_image(path=self.image_path)


class Info(CotainrSubcommand):
    """
    Obtain info about the state of all required dependencies for building a container.

    The "info" subcommand.
    """

    def execute(self):
        print("Sorry, no information about your system is available at this time.")


class _NoSubcommand(CotainrSubcommand):
    """A subcommand that simply prints the `parser` help message and exits."""

    def __init__(self, *, parser):
        self.parser = parser

    def execute(self):
        self.parser.print_help()
        sys.exit(0)


class CotainrCLI:
    """
    Build Apptainer/Singularity containers for HPC systems in user space.

    The main cotainr CLI command.

    Parameters
    ----------
    args : list of str, optional
        The input arguments to the CLI (the default is `None`, which implies
        that the input arguments are taken from `sys.argv`).

    Attributes
    ----------
    args : :class:`types.SimpleNamespace`
        The namespace holding the converted arguments parsed to the CLI.
    subcommand : :class:`CotainrSubcommand`
        The subcommand to run.
    """

    _subcommands = [Build, Info]

    def __init__(self, *, args=None):
        """Create a command line interface for the container builder."""
        # Sanity check subcommands
        for sub_cmd in self._subcommands:
            if not issubclass(sub_cmd, CotainrSubcommand):
                raise TypeError(f"{sub_cmd=} must be a cotainr.cli.CotainrSubcommand")

        # Setup main command parser
        builder_cli_doc_summary = self.__doc__.strip().splitlines()[0]
        parser = argparse.ArgumentParser(
            prog="cotainr", description=builder_cli_doc_summary
        )

        # Add subcommands parsers
        if self._subcommands:
            subparsers = parser.add_subparsers(title="subcommands")
            for subcommand_cls in self._subcommands:
                subcommand_doc_summary = (
                    subcommand_cls.__doc__.strip().splitlines()[0]
                    if subcommand_cls.__doc__
                    else ""
                )
                sub_parser = subparsers.add_parser(
                    name=subcommand_cls.__name__.lower(),
                    help=subcommand_doc_summary,
                    description=subcommand_doc_summary,
                )
                subcommand_cls.add_arguments(parser=sub_parser)
                sub_parser.set_defaults(subcommand_cls=subcommand_cls)

        # Parse args
        self.args = parser.parse_args(args=args)
        subcommand_args = {
            key: val for key, val in vars(self.args).items() if key != "subcommand_cls"
        }

        try:
            self.subcommand = self.args.subcommand_cls(**subcommand_args)
        except AttributeError:
            # Print help and exit if no subcommand was given
            self.subcommand = _NoSubcommand(parser=parser)


def main(*args, **kwargs):
    """Main CLI entrypoint."""
    # Create CotainrCLI to parse command line args and run the specified
    # subcommand
    cli = CotainrCLI()
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
                arg_desc.extend([line.strip(), " "])
        elif f"{arg} : " in line:
            # We found the requested arg in the docstring
            arg_found = True
    else:
        # We didn't find the arg in the docstring
        raise KeyError(f"The docstring does not include {arg=}")
