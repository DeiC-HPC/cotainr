"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

This module implements packing of software into the container.

Classes
-------
CondaInstall
    A Conda installation in a container sandbox.
"""

import logging
from pathlib import Path
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

from . import tracing, util

logger = logging.getLogger(__name__)


class CondaInstall:
    """
    A Conda installation in a container sandbox.

    Bootstraps a Miniforge based Conda installation in a container sandbox. As
    part of the bootstrapping of Miniforge, the user must accept the `Miniforge
    license terms
    <https://github.com/conda-forge/miniforge/blob/main/LICENSE>`_.

    Parameters
    ----------
    sandbox : :class:`~cotainr.container.SingularitySandbox`
        The sandbox in which Conda should be installed.
    prefix : str
        The Conda prefix to use for the Conda install.
    license_accepted : bool, default=False
        The flag to indicate whether or not the user has already accepted the
        Miniforge license terms.
    log_settings : :class:`~cotainr.tracing.LogSettings`, optional
        The data used to setup the logging machinery (the default is None which
        implies that the logging machinery is not used).

    Attributes
    ----------
    sandbox : :class:`~cotainr.container.SingularitySandbox`
        The sandbox in which Conda is installed.
    prefix : str
        The Conda prefix used for the Conda install.
    license_accepted : bool
        Whether or not the Miniforge license terms have been accepted.
    log_dispatcher : :class:`~cotainr.tracing.LogDispatcher` or None.
        The log dispatcher used to process stdout/stderr message from
        Singularity commands that run in sandbox, if the logging machinery is
        used.

    Notes
    -----
    When adding a Conda environment, it is the responsibility of the user of
    cotainr to make sure they have the necessary rights to use the Conda
    channels/repositories and packages specified in the Conda environment, e.g.
    if `using the default Anaconda repositories
    <https://www.anaconda.com/blog/anaconda-commercial-edition-faq>`_.
    """

    def __init__(
        self,
        *,
        sandbox,
        prefix="/opt/conda",
        license_accepted=False,
        log_settings=None,
    ):
        """Bootstrap a conda installation."""
        self.sandbox = sandbox
        self.prefix = prefix
        self.license_accepted = license_accepted
        if log_settings is not None:
            self._verbosity = log_settings.verbosity
            self.log_dispatcher = tracing.LogDispatcher(
                name=__class__.__name__,
                map_log_level_func=self._map_log_level,
                filters=self._logging_filters,
                log_settings=log_settings,
            )
        else:
            self._verbosity = 0
            self.log_dispatcher = None

        # Download Miniforge installer
        conda_installer_path = (
            Path(self.sandbox.sandbox_dir).resolve() / "conda_installer.sh"
        )
        self._download_miniforge_installer(installer_path=conda_installer_path)

        # Make sure the user has accepted the Miniforge installer license
        if not license_accepted:
            self._display_miniforge_license_for_acceptance(
                installer_path=conda_installer_path
            )
        else:
            self._display_message(
                msg=(
                    "You have accepted the Miniforge installer license via the command "
                    "line option '--accept-licenses'."
                ),
                log_level=logging.WARNING,
            )

        # Bootstrap Conda environment in container
        self._bootstrap_conda(installer_path=conda_installer_path)

        # Remove unneeded files
        conda_installer_path.unlink()
        self.cleanup_unused_files()

    def add_environment(self, *, path, name):
        """
        Add an exported Conda environment to the Conda install.

        Equivalent to calling "conda env create -f `path` -n `name`".

        Parameters
        ----------
        path : :class:`os.PathLike`
            The path to the exported env.yml file describing the Conda
            environment to install.
        name : str
            The name to use for the installed Conda environment.
        """
        self._run_command_in_sandbox(
            cmd=f"conda env create -f {path} -n {name}" + self._conda_verbosity_arg
        )

    def cleanup_unused_files(self):
        """
        Remove all unused Conda files.

        Equivalent to calling "conda clean -a".
        """
        self._run_command_in_sandbox(
            cmd="conda clean -y -a" + self._conda_verbosity_arg
        )

    def _bootstrap_conda(self, *, installer_path):
        """
        Install Conda and at its source script to the sandbox env.

        Parameters
        ----------
        installer_path : pathlib.Path
            The path of the Conda installer to run to bootstrap Conda.
        """
        # Run Conda installer
        self._run_command_in_sandbox(
            cmd=f"bash {installer_path.name} -b -s -p {self.prefix}"
        )

        # Add Conda to container sandbox env
        self.sandbox.add_to_env(
            shell_script=f"source {self.prefix + '/etc/profile.d/conda.sh'}"
        )

        # Check that we correctly use the newly installed Conda from now on
        self._check_conda_bootstrap_integrity()

        # Update the installed Conda package manager to the latest version
        self._run_command_in_sandbox(
            cmd=(
                "conda update -y -n base -c conda-forge conda"
                + self._conda_verbosity_arg
            )
        )

    def _check_conda_bootstrap_integrity(self):
        """Raise RuntimeError if multiple interfering Conda installs are found."""
        source_check_process = self._run_command_in_sandbox(cmd="conda info --base")
        if source_check_process.stdout.strip() != f"{self.prefix}":
            raise RuntimeError(
                "Multiple Conda installs interfere. "
                "We risk destroying the Conda install in "
                f"{source_check_process.stdout.strip()}. Aborting!"
            )

    def _display_message(self, *, msg, log_level=None):
        """
        Display a message to the user.

        Displays the message using the `log_dispatcher` if `log_level` is not
        `None` and a `log_dispatcher` is defined for the `CondaInstall`.
        Otherwise prints the message on stdout. When the `log_dispatcher` is
        used, messages with `log_levels` of WARNING or above are sent to stderr
        whereas massages with with `log_level` below WARNING are sent to
        stdout.

        Parameters
        ----------
        msg : str
            The message to display to the user.
        log_level : int, optional
            The logging level to use for the message, e.g. `logging.INFO` or
            `logging.WARNING`.
        """
        if self.log_dispatcher is None or log_level is None:
            print(msg)
        else:
            if log_level >= logging.WARNING:
                self.log_dispatcher.logger_stderr.log(level=log_level, msg=msg)
            else:
                self.log_dispatcher.logger_stdout.log(level=log_level, msg=msg)

    def _display_miniforge_license_for_acceptance(self, *, installer_path):
        """
        Extract and display Miniforge installer license for acceptance.

        Runs the Miniforge bootstrap installer to extract the license, displays
        it to the user, and prompts for acceptance of the license terms. Exits
        if the license terms are not accepted.

        Parameters
        ----------
        installer_path : pathlib.Path
            The path of the Miniforge installer to run to bootstrap Conda.

        Raises
        ------
        RuntimeError
            If unable to extract a license from the Miniforge installer.

        Notes
        -----
        This assumes that the Miniforge installer, as it is run, prompts the
        user for pressing ENTER to display the license, then displays the
        license and prompts the user to answer "yes" to accept the license
        terms.

        We try to "forward" this flow to the user by extracting the text shown
        when running the installer and pressing ENTER. We then prompt for a
        "yes" to the license terms.
        """
        with subprocess.Popen(
            ["bash", f"{installer_path.name}"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        ) as process:
            license_text, _ = process.communicate(
                # "press" ENTER to display the license and capture it
                "\n"
            )
            process.kill()  # We only use this process to extract the license

        util._flush_stdin_buffer()
        if license_text:
            license_text = license_text.replace(
                # remove prompt for pressing enter (as we have already done this...)
                "Please, press ENTER to continue\n>>> ",
                "\n",
            )
            logger.debug(f"The Miniforge displayed license is: {license_text}")
            val = input(license_text)  # prompt user for acceptance of license terms
            if val != "yes":
                self._display_message(
                    msg="You have not accepted the Miniforge installer license. Aborting!",
                    log_level=logging.CRITICAL,
                )
                sys.exit(0)

            self.license_accepted = True
            self._display_message(
                msg="You have accepted the Miniforge installer license.",
                log_level=logging.INFO,
            )
        else:
            raise RuntimeError(
                "No license seems to be displayed by the Miniforge installer."
            )

    @staticmethod
    def _get_install_script(architecture):
        """
        Determine the Miniforge installer to be downloaded based on system architecture.

        Always downloads a Linux version as the container is expected to always be Linux.

        Parameters
        ----------
        architecture : str
            The container architecture as returned by "uname -m".

        Raises
        ------
        ValueError
            If the container sandbox architecture is not supported.
        """
        if architecture in ("arm64", "aarch64"):
            install_script = "Miniforge3-Linux-aarch64.sh"
        elif architecture == "x86_64":
            install_script = "Miniforge3-Linux-x86_64.sh"
        else:
            raise ValueError(
                "Cotainr's CondaInstall only supports x86_64 and arm64/aarch64. "
                f'Cotainr got "{architecture=}" for your container'
            )

        return install_script

    def _download_miniforge_installer(self, *, installer_path):
        """
        Download the Miniforge installer to `installer_path`.

        Parameters
        ----------
        installer_path : pathlib.Path
            The path to download the conda installer to.

        Raises
        ------
        RuntimeError
            If the container sandbox architecture is unknown.
        urllib.error.URLError
            If three attempts at downloading the installer all fail.
        """
        architecture = self.sandbox.architecture
        if architecture is None:
            raise RuntimeError(
                f"Cotainr's CondaInstall got '{architecture=}' "
                "which indicates that it is not running in a container sandbox context."
            )

        install_script = CondaInstall._get_install_script(architecture)
        miniforge_installer_url = (
            "https://github.com/conda-forge/miniforge/releases/latest/download/"
            + install_script
        )

        # Make up to 3 attempts at downloading the installer
        for retry in range(3):
            try:
                with urllib.request.urlopen(miniforge_installer_url) as url:  # nosec B310
                    installer_path.write_bytes(url.read())

                break

            except urllib.error.URLError as e:
                url_error = e

                # Exponential back-off
                time.sleep(2**retry + random.uniform(0.001, 1))  # nosec B311

        else:
            raise url_error

    def _run_command_in_sandbox(self, *, cmd):
        """
        Wrap the sandbox command runner to use class specific log_dispatcher.

        Wraps calls to `self.sandbox.run_command_in_container` to use
        self.log_dispatcher for log handling instead of the sandbox's log
        dispatcher.

        Parameters
        ----------
        cmd : str
            The command to run in the container sandbox.

        Returns
        -------
        process : :class:`subprocess.CompletedProcess`
            Information about the process that ran in the container sandbox.
        """
        return self.sandbox.run_command_in_container(
            cmd=cmd, custom_log_dispatcher=self.log_dispatcher
        )

    @property
    def _conda_verbosity_arg(self):
        """
        Get a verbosity level for Conda commands.

        A mapping of the internal cotainr verbosity level to `Conda verbosity
        flags
        <https://docs.conda.io/projects/conda/en/latest/commands/create.html#Output,%20Prompt,%20and%20Flow%20Control%20Options>`_.

        Returns
        -------
        verbosity_arg : str
            The verbosity arg ("-q", "-v", "-vv", etc.) to add to the Conda
            command.
        """
        if self._verbosity <= 0:
            return " -q"
        elif self._verbosity == 2:
            # Conda INFO
            return " -v"
        elif self._verbosity == 3:
            # Conda DEBUG
            return " -vv"
        elif self._verbosity >= 4:
            # Conda TRACE
            return " -vvv"
        else:
            return ""

    @property
    def _logging_filters(self):
        """
        Create logging filters for messages from conda commands.

        Returns
        -------
        logging_filters : list of :class:`logging.Filter`.
            The list of filters to use with the logging machinery when handling
            messages from conda commands.
        """

        class StripANSIEscapeCodes(logging.Filter):
            """
            In-place strip all ANSI escape codes.

            Regex from https://stackoverflow.com/a/14693789
            """

            ansi_escape_re = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

            def filter(self, record):
                record.msg = self.ansi_escape_re.sub("", record.msg)
                return True

        class NoEmptyLinesFilter(logging.Filter):
            """Remove any empty lines."""

            def filter(self, record):
                return record.msg.strip() != ""

        class OnlyFinalProgressbarFilter(logging.Filter):
            """
            Only include final 100% complete line when download progress bars are shown.

            Assume a progress bar line like
            [some text]|[some text]|[progress bar characters]| [percentage complete]% [ansi escape codes]
            """

            progress_bar_re = re.compile(
                r"^(.+?)\|(.+?)\|[ \#0-9]+?\|[ ]{1,3}[0-9]{1,2}\%"
            )

            def filter(self, record):
                return not self.progress_bar_re.match(record.msg)

        logging_filters = [
            # The order matters as filters are applied in order. ANSI escape
            # codes and partial progress bars must be removed before filtering
            # empty lines.
            StripANSIEscapeCodes(),
            OnlyFinalProgressbarFilter(),
            NoEmptyLinesFilter(),
        ]

        return logging_filters

    @staticmethod
    def _map_log_level(msg):
        """
        Attempt to infer log level for a message.

        Parameters
        ----------
        msg : str
            The message to infer log level for.

        Returns
        -------
        log_level : int
            One of the standard log levels (DEBUG, INFO, WARNING, ERROR, or
            CRITICAL).
        """
        if (
            msg.startswith("DEBUG")
            or msg.startswith("VERBOSE")
            or msg.startswith("TRACE")
        ):
            return logging.DEBUG
        elif msg.startswith("INFO"):
            return logging.INFO
        elif msg.startswith("WARNING"):
            return logging.WARNING
        elif msg.startswith("ERROR"):
            return logging.ERROR
        elif msg.startswith("CRITICAL"):
            return logging.CRITICAL
        else:
            # If no prefix on message, assume its INFO level
            return logging.INFO
