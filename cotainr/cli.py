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
Build(CotainrSubcommand)
    Build a container. (The "build" subcommand.)
CotainrCLI
    Build Apptainer/Singularity containers for HPC systems in user space. (The
    main CLI command.)
Info(CotainrSubcommand)
    Obtain info about the state of all required dependencies for building a
    container. (The "info" subcommand.)

Functions
---------
main(\*args, \*\*kwargs)
    Main CLI entrypoint.
"""

from abc import ABC, abstractmethod
import argparse
from datetime import datetime
import logging
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

from . import __version__ as _cotainr_version
from . import _minimum_dependency_version as _min_dep_ver
from . import container, pack, tracing, util

logger = logging.getLogger(__name__)


class CotainrSubcommand(ABC):
    """Abstract base class for `CotainrCLI` subcommands."""

    @classmethod  # noqa: B027
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
    verbosity : int, optional
        The verbosity of the output from cotainr: -1 for only CRITICAL, 0 (the
        default) for cotainr INFO and subprocess WARNING, 1 for subprocess
        output as well, 2 for subprocess INFO, 3 for DEBUG, and 4 for TRACE.
    log_to_file : bool
        Create files containing all logging information shown on stdout/stderr.
    no_color : bool
        Do not use colored console output.
    """

    def __init__(
        self,
        *,
        image_path,
        base_image=None,
        conda_env=None,
        system=None,
        accept_licenses=False,
        verbosity=0,
        log_to_file=False,
        no_color=False,
    ):
        """Construct the "build" subcommand."""
        self.log_settings = tracing.LogSettings(
            verbosity=verbosity,
            log_file_path=(
                Path(".").resolve()
                / f"cotainr_build_{datetime.now().isoformat().replace(':', '.')}"
                if log_to_file
                else None
            ),
            no_color=no_color,
        )
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
        system_group = parser.add_mutually_exclusive_group(required=True)
        system_group.add_argument(
            "--base-image",
            help=_extract_help_from_docstring(arg="base_image", docstring=cls.__doc__),
        )
        system_group.add_argument(
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
        verbose_quiet_group = parser.add_mutually_exclusive_group()
        verbose_quiet_group.add_argument(
            "--verbose",
            "-v",
            action="count",
            dest="verbosity",
            default=0,
            help=(
                "increase the verbosity of the output from cotainr. "
                "Can be used multiple times: Once for subprocess output, "
                "twice for subprocess INFO, three times for DEBUG, "
                "and four times for TRACE"
            ),
        )
        verbose_quiet_group.add_argument(
            "--quiet",
            "-q",
            action="store_const",
            const=-1,
            dest="verbosity",
            help="do not show any non-CRITICAL output from cotainr",
        )
        parser.add_argument(
            "--log-to-file",
            action="store_true",
            help=_extract_help_from_docstring(arg="log_to_file", docstring=cls.__doc__),
        )
        parser.add_argument(
            "--no-color",
            action="store_true",
            help=_extract_help_from_docstring(arg="no_color", docstring=cls.__doc__),
        )

    def execute(self):
        """Execute the "build" subcommand."""
        t_start_build = time.time()
        with tracing.ConsoleSpinner():
            logger.info("Creating Singularity Sandbox")
            with container.SingularitySandbox(
                base_image=self.base_image, log_settings=self.log_settings
            ) as sandbox:
                if self.conda_env is not None:
                    # Install supplied conda env
                    logger.info("Installing Conda environment: %s", self.conda_env)
                    conda_env_name = "conda_container_env"
                    conda_env_file = sandbox.sandbox_dir / self.conda_env.name
                    shutil.copyfile(self.conda_env, conda_env_file)
                    conda_install = pack.CondaInstall(
                        sandbox=sandbox,
                        license_accepted=self.accept_licenses,
                        log_settings=self.log_settings,
                    )
                    conda_install.add_environment(
                        path=conda_env_file, name=conda_env_name
                    )

                    sandbox.add_to_env(shell_script=f"conda activate {conda_env_name}")

                    # Clean-up unused files
                    logger.info("Cleaning up unused Conda files")
                    conda_install.cleanup_unused_files()
                    logger.info(
                        "Finished installing conda environment: %s", self.conda_env
                    )

                logger.info("Adding metadata to container")
                sandbox.add_metadata()
                logger.info("Building container image")
                sandbox.build_image(path=self.image_path)

            t_end_build = time.time()
            logger.info(
                "Finished building %s in %s",
                self.image_path,
                time.strftime("%H:%M:%S", time.gmtime(t_end_build - t_start_build)),
            )


class Info(CotainrSubcommand):
    """
    Obtain info about the state of all required dependencies for building a container.

    The "info" subcommand.
    """

    def __init__(self):
        """Construct the "info" subcommand."""
        self._checkmark = "\x1b[38;5;2mOK\x1b[0m"  # green OK
        self._nocheckmark = "\x1b[38;5;1mERROR\x1b[0m"  # red ERROR
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
        parser.add_argument(
            "--version", action="version", version=f"%(prog)s {_cotainr_version}"
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

        # Setup subcommand
        try:
            self.subcommand = self.args.subcommand_cls(**subcommand_args)
        except AttributeError:
            # Print help and exit if no subcommand was given
            self.subcommand = _NoSubcommand(parser=parser)

        # Setup CLI logging
        self._setup_cotainr_cli_logging(
            log_settings=getattr(
                self.subcommand,
                "log_settings",
                tracing.LogSettings(),
            )
        )

    def _setup_cotainr_cli_logging(self, *, log_settings):
        """
        Set up logging for the cotainr main CLI.

        Setting up the logging for the cotainr main CLI includes:
        - Defining log levels based on CLI verbosity arguments.
        - Defining log message formats based on CLI verbosity arguments.
        - Creating log handlers for console output.
        - Creating log handlers for log file output, if requested.
        - Setting up colored console output, if requested.
        - Defining the cotainr "root logger".

        Parameters
        ----------
        log_settings : :class:`~cotainr.tracing.LogSettings`
            The log settings to use for the cotainr main CLI logging.
        """

        class OnlyDebugInfoLevelFilter(logging.Filter):
            """A simple logging filter that removes records >=INFO."""

            def filter(self, record):
                return record.levelno <= logging.INFO

        # Setup cotainr CLI log level and format
        if log_settings.verbosity >= 2:
            cotainr_log_level = logging.DEBUG
            cotainr_stdout_fmt = (
                "%(asctime)s - %(name)s::%(funcName)s::%(lineno)d::"
                "Cotainr:-:%(levelname)s: %(message)s"
            )
            cotainr_stderr_fmt = cotainr_stdout_fmt
        else:
            if log_settings.verbosity <= -1:
                cotainr_log_level = logging.CRITICAL
            else:
                cotainr_log_level = logging.INFO
            cotainr_stdout_fmt = "Cotainr:-: %(message)s"
            cotainr_stderr_fmt = "Cotainr:-:%(levelname)s: %(message)s"

        # Setup cotainr log handlers
        cotainr_stdout_handlers = [logging.StreamHandler(stream=sys.stdout)]
        cotainr_stderr_handlers = [logging.StreamHandler(stream=sys.stderr)]
        if log_settings.log_file_path is not None:
            cotainr_stdout_handlers.append(
                logging.FileHandler(
                    log_settings.log_file_path.with_suffix(
                        log_settings.log_file_path.suffix + ".out"
                    )
                )
            )
            cotainr_stderr_handlers.append(
                logging.FileHandler(
                    log_settings.log_file_path.with_suffix(
                        log_settings.log_file_path.suffix + ".err"
                    )
                )
            )

        for stdout_handler in cotainr_stdout_handlers:
            stdout_handler.setLevel(cotainr_log_level)
            stdout_handler.setFormatter(logging.Formatter(cotainr_stdout_fmt))
            stdout_handler.addFilter(
                # Avoid also emitting WARNINGs and above on stdout
                OnlyDebugInfoLevelFilter()
            )

        for stderr_handler in cotainr_stderr_handlers:
            stderr_handler.setLevel(logging.WARNING)
            stderr_handler.setFormatter(logging.Formatter(cotainr_stderr_fmt))

        if not log_settings.no_color:
            # Replace console formatters with one that colors the output
            cotainr_stdout_handlers[0].setFormatter(
                tracing.ColoredOutputFormatter(cotainr_stdout_fmt)
            )
            cotainr_stderr_handlers[0].setFormatter(
                tracing.ColoredOutputFormatter(cotainr_stderr_fmt)
            )

        # Define cotainr root logger
        root_logger = logging.getLogger("cotainr")
        root_logger.setLevel(cotainr_log_level)
        for handler in cotainr_stdout_handlers + cotainr_stderr_handlers:
            root_logger.addHandler(handler)


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
