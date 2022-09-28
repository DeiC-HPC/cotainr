"""
User space Apptainer/Singularity container builder.

Created by DeiC, deic.dk
"""

import argparse
import pathlib


class Build:
    """
    Build a container.

    Implements the "build" subcommand.
    """

    def __init__(self, *, image_path=None, base_image=None, conda_env=None):
        """
        Create the "build" subcommand.

        Parameters
        ----------
        image_path : pathlike
            Path to the built container image.
        base_image : str
            Base image to use for the container which may be any valid
            Apptainer/Singularity <BUILD SPEC>.
        conda_env : pathlike, optional
            Path to a Conda environment.yml file to install and activate in the
            container.

        """
        self.image_path = image_path
        self.base_image = base_image
        self.conda_env = conda_env

    @classmethod
    def add_arguments(cls, parser):
        """
        Add command line arguments to arguments parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The argument parser to add arguments to.
        """
        parser.add_argument(
            "image_path",
            help=_extract_help_from_docstring("image_path", cls.__init__.__doc__),
            type=pathlib.Path,
        )
        parser.add_argument(
            "--base-image",
            required=True,
            help=_extract_help_from_docstring("base_image", cls.__init__.__doc__),
        )
        parser.add_argument(
            "--conda-env",
            help=_extract_help_from_docstring("conda_env", cls.__init__.__doc__),
            type=pathlib.Path,
        )

    def execute(self):
        """Execute the subcommand."""
        print(
            "Building container based on "
            f"{self.image_path=}, {self.base_image=}, {self.conda_env=}"
        )


class Info:
    """
    Obtain info about the state of all required dependencies for building a container.

    Implements the "info" subcommand.
    """

    @classmethod
    def add_arguments(cls, parser):
        """
        Add command line arguments to arguments parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The argument parser to add arguments to.
        """
        pass

    def execute(self):
        """Execute the subcommand."""
        print("Sorry, no information about your system is available at this time.")


class BuilderCLI:
    """
    Build Apptainer/Singularity containers for HPC systems in user space.

    The main command CLI.
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
            subcommand_cls.add_arguments(sub_parser)
            sub_parser.set_defaults(subcommand_cls=subcommand_cls)

        # Parse args
        self.args = parser.parse_args()
        subcommand_args = {
            key: val for key, val in vars(self.args).items() if key != "subcommand_cls"
        }
        self.subcommand = self.args.subcommand_cls(**subcommand_args)


def _extract_help_from_docstring(arg, docstring):
    """
    Extract the description of `arg` in `string`.

    Parameters
    ----------
    arg : str
        The name of the argument.
    docstring : str
        The numpydoc docstring in which `arg` is documented.
    """
    arg_found = False
    arg_desc = []
    for line in docstring.splitlines():
        if arg_found:
            if " : " in line or line.strip() == "":
                # No more description lines, return the description
                return "".join(arg_desc).lstrip().lower().rstrip(".")
            else:
                # Extract line as part of arg description
                arg_desc.extend([line, " "])
        elif f"{arg} : " in line:
            # We found the requested arg in the docstring
            arg_found = True
    else:
        # We didn't find the arg in the docstring
        raise KeyError(f"The docstring does not include {arg=}")


if __name__ == "__main__":
    # Create BuilderCLI to parse command line args and run the specified
    # subcommand
    cli = BuilderCLI()
    cli.subcommand.execute()
