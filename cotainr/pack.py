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
import re
import sys

from . import tracing, util

logger = logging.getLogger(__name__)

# class CondaRecipe:
#     """
#     Minimal library style conda install commands.
#     """

#     def __init__(self, log_settings=None):
#         if log_settings is None:
#             log_settings = tracing.LogSettings()

#         self.log_dispatcher = tracing.LogDispatcher(
#             name=__class__.__name__,
#             map_log_level_func=self._map_log_level,
#             filters=self._logging_filters,
#             log_settings=log_settings,
#         )

#         if log_settings.verbosity == 2:
#             _v = " -v"  # Conda INFO
#         elif log_settings.verbosity == 3 or log_settings.verbosity == 4:
#             _v = " -vv"  # Conda DEBUG
#         elif log_settings.verbosity >= 5:
#             _v = " -vvv"  # Conda TRACE
#         else:
#             _v = ""

#         # Reference = [function, string, verification]
#         download =       ['download', self.condaInstaller_sh, self.verify_license_accept]
#         install =        ['run', f"bash {install_path.name} -b -s -p {self.prefix}", self.verify_correct_conda_runtime and install_path.unlink()]
#         source_install = [f'write{source_file}', f"source {self.prefix + '/etc/profile.d/conda.sh'}", None]
#         update =         ['run', "conda update -y -n base -c conda-forge conda -q" + _v, None]
#         clean =          ['run', "conda clean -y -a -q" + _v, None]
#         create_env =     ['run', f"conda env create -f {path} -n {name} -q" + _v, None]
#         source_env =     [f'write{env_file}', f"conda activate {conda_env_name}", None]
#         clean =          ['run', "conda clean -y -a -q" + _v, None]

#         self.bootstrap = [install, source_install, update, (clean)]
#         self.environment = [create_env, source_env, (clean)]


#     def bootstrap_runtime(self):
#         for recipe_step in self.bootstrap:
#             dispatch(recipe_step)

#     def build_environment(self):
#         for recipe_step in self.environment:
#             dispatch(recipe_step)

# def dispatch(recipe_step, comm):
#     execute, command, post_process = recipe_step
#     getattr(comm, execute)(command)
#     post_process()


class Conda:
    """
    A Conda installation in a container sandbox.

    Bootstraps a Miniforge based Conda installation in a container sandbox. As
    part of the bootstrapping of Miniforge, the user must accept the `Miniforge
    license terms
    <https://github.com/conda-forge/miniforge/blob/main/LICENSE>`_.

    Parameters
    ----------
    comm : :class:`~cotainr.container.CommunicationInterface`
        The communicator interface to the sandbox.
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

    def __init__(self, *, comm, prefix="/opt/cotainr/conda", log_settings=None):
        """Bootstrap a conda installation."""
        self.comm = comm
        self.prefix = prefix

        if log_settings is None:
            log_settings = tracing.LogSettings()

        self.log_dispatcher = tracing.LogDispatcher(
            name=__class__.__name__,
            map_log_level_func=self._map_log_level,
            filters=self._logging_filters,
            log_settings=log_settings,
        )

        if log_settings.verbosity == 2:
            self._conda_verbosity_arg = " -v"  # Conda INFO
        elif log_settings.verbosity == 3 or log_settings.verbosity == 4:
            self._conda_verbosity_arg = " -vv"  # Conda DEBUG
        elif log_settings.verbosity >= 5:
            self._conda_verbosity_arg = " -vvv"  # Conda TRACE
        else:
            self._conda_verbosity_arg = ""

    def download_miniforge(self, location, architecture, license_accepted=False):
        """Download the Miniforge installer."""
        # Download Miniforge installer
        conda_installer_path = Path(location).resolve() / "conda_installer.sh"
        install_script = self._get_install_script(architecture)
        miniforge_url = (
            "https://github.com/conda-forge/miniforge/releases/latest/download/"
            + install_script
        )

        self.comm.download(
            src_url=miniforge_url,
            dst_path=conda_installer_path,
            log_dispatcher=self.log_dispatcher,
        )

        # Make sure the user has accepted the Miniforge installer license
        if not license_accepted:
            self._display_miniforge_license_for_acceptance(
                installer_path=conda_installer_path
            )
        else:
            self.log_dispatcher.logger_stderr.log(
                msg=(
                    "You have accepted the Miniforge installer license via the command "
                    "line option '--accept-licenses'."
                ),
                level=logging.WARNING,
            )
        return conda_installer_path

    def install(self, install_path, env_file):
        """Install the downloaded Miniforge conda."""
        # Run Conda installer
        self.comm.run_command_in_container(
            cmd=f"bash {install_path.name} -b -s -p {self.prefix}",
            log_dispatcher=self.log_dispatcher,
        )

        # Add Conda to container sandbox env
        self.comm.write_to_file(
            env_file,
            f"source {self.prefix + '/etc/profile.d/conda.sh'}",
            log_dispatcher=self.log_dispatcher,
        )

        # Check that we correctly use the newly installed Conda from now on
        """Raise RuntimeError if multiple interfering Conda installs are found."""
        source_check_process = self.comm.run_command_in_container(
            cmd="conda info --base", log_dispatcher=self.log_dispatcher
        )
        if source_check_process.stdout.strip() != f"{self.prefix}":
            raise RuntimeError(
                "Multiple Conda installs interfere. "
                "We risk destroying the Conda install in "
                f"{source_check_process.stdout.strip()}. Aborting!"
            )

        # Update the installed Conda package manager to the latest version
        self.comm.run_command_in_container(
            cmd="conda update -y -n base -c conda-forge conda -q"
            + self._conda_verbosity_arg,
            log_dispatcher=self.log_dispatcher,
        )

        # Remove unneeded files
        install_path.unlink()
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
        self.comm.run_command_in_container(
            cmd=f"conda env create -f {path} -n {name} -q" + self._conda_verbosity_arg,
            log_dispatcher=self.log_dispatcher,
        )

    def cleanup_unused_files(self):
        """
        Remove all unused Conda files.

        Equivalent to calling "conda clean -a".
        """
        self.comm.run_command_in_container(
            cmd="conda clean -y -a -q" + self._conda_verbosity_arg,
            log_dispatcher=self.log_dispatcher,
        )

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
        process = self.comm._subprocess_runner(
            ["bash", f"{installer_path.name}"], self.log_dispatcher, input="\n"
        )
        license_text = process.stdout
        util._flush_stdin_buffer()
        if license_text:
            license_text = license_text.replace(
                # remove prompt for pressing enter (as we have already done this...)
                "Please, press ENTER to continue\n>>> ",
                "\n",
            )
            # Remove "[yes|no]"" and ">>>" from license text as answer_is_yes
            # adds them as part of the input handling
            license_text = license_text.replace(" [yes|no]\n>>> ", "")
            self.log_dispatcher.logger_stdout.log(
                f"The Miniforge displayed license is: {license_text}",
                level=logging.DEBUG,
            )
            # prompt user for acceptance of license terms
            if not util.answer_is_yes(license_text):
                self.log_dispatcher.logger_stderr.log(
                    msg="You have not accepted the Miniforge installer license. Aborting!",
                    level=logging.CRITICAL,
                )
                sys.exit(0)

            self.license_accepted = True
            self.log_dispatcher.logger_stdout.log(
                msg="You have accepted the Miniforge installer license.",
                level=logging.INFO,
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

    def __getattr__(self, func):
        """
        Wrap all methods of CommunicationInterface.

        It is called as last resort after getattr(self, method) ie. self.method()
        is not found.
        """

        def method(*args, **kwargs):
            if func in dir(self.comm) and not func.startswith("_"):
                return getattr(self.comm, func)(
                    *args, **kwargs, log_dispatcher=self.log_dispatcher
                )
            else:
                raise AttributeError

        return method

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
