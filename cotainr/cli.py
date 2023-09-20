r"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements the command line main command and subcommands.

Classes
-------
CotainrSubcommand(ABC)
    Abstract base class for `CotainrCLI` subcommands.
Build
    Build a container. (The "build" subcommand.)
CotainrCLI
    Build Apptainer/Singularity containers for HPC systems in user space. (The
    main CLI command.)
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
import platform
import re
import shutil
import subprocess
import sys

from . import container
from . import pack
from . import util
from . import _minimum_dependency_version as _min_dep_ver


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
        container. When installing a Conda environment, you must accept the
        Miniforge license terms, as specified during the build process.
    system : str
        Which system/partition you will be running the container on. This sets
        base image and other parameters for a simpler container creation.
        Running the info command will tell you more about the system and what
        is available.
    accept_licenses : bool, default=False
        Accept all license terms (if any) needed for completing the container
        build process.
    """

    def __init__(
        self,
        *,
        image_path,
        base_image=None,
        conda_env=None,
        system=None,
        accept_licenses=False,
    ):
        """Construct the "build" subcommand."""
        self.image_path = Path(image_path).resolve()
        if self.image_path.exists():
            val = input(
                f"{self.image_path} already exists. "
                "Would you like to overwrite it? (y/N) "
            ).lower()
            if val != "y":
                sys.exit(0)

        self.accept_licenses = accept_licenses
        self.base_image = base_image
        systems = util.get_systems()
        if system is not None:
            if system in systems:
                self.system = systems[system]
                self.base_image = self.system["base-image"]
            else:
                raise KeyError("System does not exist")
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
        """Add arguments to the "build" subcommand subparser."""
        parser.add_argument(
            "image_path",
            help=_extract_help_from_docstring(arg="image_path", docstring=cls.__doc__),
            type=Path,
        )
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--base-image",
            help=_extract_help_from_docstring(arg="base_image", docstring=cls.__doc__),
        )
        group.add_argument(
            "--system",
            help=_extract_help_from_docstring(arg="system", docstring=cls.__doc__),
        )
        parser.add_argument(
            "--conda-env",
            help=_extract_help_from_docstring(arg="conda_env", docstring=cls.__doc__),
            type=Path,
        )
        parser.add_argument(
            "--accept-licenses",
            help=_extract_help_from_docstring(
                arg="accept_licenses", docstring=cls.__doc__
            ),
            action="store_true",
        )

    def execute(self):
        """Execute the "build" subcommand."""
        with container.SingularitySandbox(base_image=self.base_image) as sandbox:
            if self.conda_env is not None:
                # Install supplied conda env
                conda_env_name = "conda_container_env"
                conda_env_file = sandbox.sandbox_dir / self.conda_env.name
                shutil.copyfile(self.conda_env, conda_env_file)
                conda_install = pack.CondaInstall(
                    sandbox=sandbox, license_accepted=self.accept_licenses
                )
                conda_install.add_environment(path=conda_env_file, name=conda_env_name)
                sandbox.add_to_env(shell_script=f"conda activate {conda_env_name}")
                conda_install.cleanup_unused_files()

            sandbox.add_metadata()
            sandbox.build_image(path=self.image_path)


class Info(CotainrSubcommand):
    """
    Obtain info about the state of all required dependencies for building a container.

    The "info" subcommand.
    """

    def __init__(self):
        """Construct the "info" subcommand."""
        self._checkmark = "\033[92mOK\033[0m"  # green OK
        self._nocheckmark = "\033[91mERROR\033[0m"  # red ERROR
        self._tabs_width = 4

    def execute(self):
        """Execute the "info" subcommand."""
        print("Dependency report")
        print("-" * 79)
        print(f"\t- {self._check_python_dependency()}".expandtabs(self._tabs_width))
        print(
            f"\t- {self._check_singularity_dependency()}".expandtabs(self._tabs_width)
        )
        print("")
        print("System info")
        print("-" * 79)
        print(self._check_systems())

    def _check_python_dependency(self):
        """
        Check and report on the Python version used.

        Reports the Python version used and whether it meets the minimum
        required version.

        Returns
        -------
        python_check_result : str
            A description of the Python version used.
        """
        ver_tup = platform.python_version_tuple()
        ver_check = self._check_version(
            version=tuple(map(int, ver_tup)), min_version=_min_dep_ver["python"]
        )
        return f"Running python {'.'.join(ver_tup)} {ver_check}"

    def _check_singularity_dependency(self):
        """
        Check and report on any installed singularity provider.

        Reports the provider (apptainer/singularity/unknown), its version, and
        whether it meets the minimum required version if a singularity provider
        is found. Otherwise reports "apptainer/singularity not found".

        Returns
        -------
        singularity_check_result : str
            A description of the singularity provider.

        Notes
        -----
        Assumes that "singularity --version" returns a format like:
          - singularity version 3.7.4-1  (for singularity)
          - singularity-ce version 3.11.4-1 (for singularity community edition)
          - apptainer version 1.0.3      (for apptainer)
        """
        try:
            provider, _, version = subprocess.check_output(
                ["singularity", "--version"], text=True
            ).split()
            ver_tup = tuple(
                map(int, re.findall(r"\d+\.\d+\.\d+", version)[0].split("."))
            )
            if provider in _min_dep_ver:
                ver_check = self._check_version(
                    version=ver_tup, min_version=_min_dep_ver[provider]
                )
                singularity_check_result = f"Found {provider} {version} {ver_check}"
            else:
                singularity_check_result = (
                    f"Found unknown singularity provider: {provider} {version}"
                )
        except (subprocess.CalledProcessError, FileNotFoundError):
            singularity_check_result = (
                f"apptainer/singularity not found, {self._nocheckmark}"
            )

        return singularity_check_result

    def _check_systems(self):
        """
        Check and report on any available HPC systems.

        Reports the available systems from the `systems.json` file.

        Returns
        -------
        system_check_result : str
            A description of the available system configurations.
        """
        systems = util.get_systems()
        system_check_report = []
        if systems:
            system_check_report.append("Available system configurations:")
            for system in systems:
                system_check_report.append(f"\t- {system}".expandtabs(self._tabs_width))
        else:
            system_check_report.append("No system configurations available")

        return "\n".join(system_check_report)

    def _check_version(self, *, version, min_version):
        """
        Check and report a version against a minimum required version.

        Checks whether `version` is larger than or equal to `min_version` and
        returns a description of result. The version specifications must be
        (major, minor, patchlevel) tuples of integers.

        Parameters
        ----------
        version : tuple of int
            The version to check against a minimum version.
        min_version : tuple of int
            The minimum version to check against.

        Returns
        -------
        ver_check : str
            A description of the result of the version check.

        Raises
        ------
        TypeError
            If the provided `version` and `min_version` are not (major, minor,
            patchlevel) tuples of integers.
        """
        for name, ver_spec in {"version": version, "min_version": min_version}.items():
            if (
                not isinstance(ver_spec, tuple)
                or len(ver_spec) != 3
                or not all(isinstance(part, int) for part in ver_spec)
            ):
                raise TypeError(
                    f"The '{name}={ver_spec}' argument must be "
                    "a (major, minor, patchlevel) tuple of integers"
                )
        min_ver_str = f"{min_version[0]}.{min_version[1]}.{min_version[2]}"
        if version >= min_version:
            ver_check = f">= {min_ver_str}, {self._checkmark}"
        else:
            ver_check = f"< {min_ver_str}, {self._nocheckmark}"

        return ver_check


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
        """Construct a command line interface for the container builder."""
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
    """Construct the main CLI entrypoint."""
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

    Returns
    -------
    arg_description : str
        The argument description formatted in a similar way to the default
        arguments provided by an `argparse.ArgumentParser`, i.e. a single line,
        no leading white space, first letter lower case, and no trailing
        period.

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
                arg_description = "".join(arg_desc).strip().rstrip(".")
                arg_description = arg_description[0].lower() + arg_description[1:]
                return arg_description
            else:
                # Extract line as part of arg description
                arg_desc.extend([line.strip(), " "])
        elif f"{arg} : " in line:
            # We found the requested arg in the docstring
            arg_found = True
    else:
        # We didn't find the arg in the docstring
        raise KeyError(f"The docstring does not include {arg=}")
