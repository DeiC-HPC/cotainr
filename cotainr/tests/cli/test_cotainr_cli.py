"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import itertools
import logging
import re

import pytest

from cotainr.cli import CotainrCLI
from cotainr.tracing import LogSettings

from .data import (
    data_cotainr_critical_color_log_messages,
    data_cotainr_debug_color_log_messages,
    data_cotainr_info_color_log_messages,
    data_cotainr_info_no_color_log_messages,
)
from .patches import (
    patch_disable_cotainrcli_init,
    patch_disables_cotainrcli_setup_cotainr_cli_logging,
)
from .stubs import StubInvalidSubcommand, StubLogSettingsSubcommand, StubValidSubcommand


class TestConstructor:
    def test_adding_subcommand(self, argparse_options_line, capsys, monkeypatch):
        monkeypatch.setattr(CotainrCLI, "_subcommands", [StubValidSubcommand])
        with pytest.raises(SystemExit):
            CotainrCLI(args=["stubvalidsubcommand", "-h"])
        stdout = capsys.readouterr().out
        assert stdout == (
            "usage: cotainr stubvalidsubcommand [-h] [--kw-arg KW_ARG] pos_arg\n\n"
            "positional arguments:\n"
            "  pos_arg\n\n"
            f"{argparse_options_line}"
            "  -h, --help       show this help message and exit\n"
            "  --kw-arg KW_ARG\n"
        )

    @pytest.mark.parametrize(
        "subcommands",
        (
            [StubInvalidSubcommand],
            [StubInvalidSubcommand] + CotainrCLI._subcommands,
            CotainrCLI._subcommands + [StubInvalidSubcommand],
        ),
    )
    def test_invalid_subcommands(self, subcommands, monkeypatch):
        monkeypatch.setattr(CotainrCLI, "_subcommands", subcommands)
        with pytest.raises(TypeError, match="must be a cotainr.cli.CotainrSubcommand"):
            CotainrCLI(args=[])

    def test_no_subcommands(self, capsys, monkeypatch):
        monkeypatch.setattr(CotainrCLI, "_subcommands", [])
        with pytest.raises(SystemExit):
            CotainrCLI(args=[]).subcommand.execute()
        stdout = capsys.readouterr().out
        assert stdout.startswith("usage: cotainr [-h] [--version]\n")
        assert "subcommands:" not in stdout

    def test_setup_custom_cli_log_settings_logger(
        self, patch_disables_cotainrcli_setup_cotainr_cli_logging, capsys, monkeypatch
    ):
        monkeypatch.setattr(CotainrCLI, "_subcommands", [StubLogSettingsSubcommand])
        CotainrCLI(
            args=[
                "stublogsettingssubcommand",
                "--verbosity=-1",
                "--log-file-path=/some/path_6021",
                "--no-color",
            ]
        )
        stdout = capsys.readouterr().out.rstrip("\n")
        assert stdout == (
            "LogSettings("
            "verbosity=-1, log_file_path=PosixPath('/some/path_6021'), no_color=True)"
        )

    def test_setup_default_cli_logger(
        self, patch_disables_cotainrcli_setup_cotainr_cli_logging, capsys, monkeypatch
    ):
        monkeypatch.setattr(CotainrCLI, "_subcommands", [StubValidSubcommand])
        CotainrCLI(args=["stubvalidsubcommand", "some_pos_arg_6021"])

        # Check that the default LogSettings are used if no one are specified
        stdout = capsys.readouterr().out.rstrip("\n")
        assert stdout == str(LogSettings())

    @pytest.mark.parametrize(
        "arg, kwarg",
        [
            ("", ""),
            ("another_pos_arg", ""),
            ("", "some_kwarg"),
            ("some_pos_arg", 6021),
        ],
    )
    def test_subcommand_arg_parsing(self, arg, kwarg, capsys, monkeypatch):
        monkeypatch.setattr(CotainrCLI, "_subcommands", [StubValidSubcommand])
        cli = CotainrCLI(args=["stubvalidsubcommand", f"{arg}", f"--kw-arg={kwarg}"])
        cli.subcommand.execute()
        stdout = capsys.readouterr().out
        assert stdout == f"Executed: 'stubvalidsubcommand {arg} --kw-arg={kwarg}'"


class TestHelpMessage:
    cotainr_main_help_msg = (
        # Capsys apparently assumes an 80 char terminal (?) - thus extra '\n'
        "usage: cotainr [-h] [--version] {{build,info}} ...\n\n"
        "Build Apptainer/Singularity containers for HPC systems in user space.\n\n"
        "{argparse_options_line}"
        "  -h, --help    show this help message and exit\n"
        "  --version     show program's version number and exit\n\n"
        "subcommands:\n  {{build,info}}\n"
        "    build       Build a container.\n"
        "    info        Obtain info about the state of all required dependencies for\n"
        "                building a container.\n"
    )

    def test_main_help(self, argparse_options_line, capsys):
        with pytest.raises(SystemExit):
            CotainrCLI(args=["--help"])
        stdout = capsys.readouterr().out
        assert stdout == self.cotainr_main_help_msg.format(
            argparse_options_line=argparse_options_line
        )

    def test_missing_subcommand(self, argparse_options_line, capsys):
        with pytest.raises(SystemExit):
            CotainrCLI(args=[]).subcommand.execute()
        stdout = capsys.readouterr().out
        assert stdout == self.cotainr_main_help_msg.format(
            argparse_options_line=argparse_options_line
        )


class TestVersionMessage:
    def test_main_version(self, capsys):
        from cotainr import __version__ as _cotainr_version

        with pytest.raises(SystemExit):
            CotainrCLI(args=["--version"])
        stdout = capsys.readouterr().out
        assert stdout == f"cotainr {_cotainr_version}\n"


class Test_SetupCotainrCLILogging:
    @pytest.mark.parametrize("verbosity", [-1, -2, -3, -5, -1000])
    def test_cotainr_critical_logging(
        self,
        verbosity,
        capsys,
        data_cotainr_critical_color_log_messages,
        patch_disable_cotainrcli_init,
    ):
        (
            log_level_msgs,
            stdout_msgs,
            stderr_msgs,
        ) = data_cotainr_critical_color_log_messages

        # Setup the CotainrCLI logger
        CotainrCLI()._setup_cotainr_cli_logging(
            log_settings=LogSettings(
                verbosity=verbosity, log_file_path=None, no_color=False
            )
        )
        assert "cotainr" in logging.Logger.manager.loggerDict

        # Log test messages to cotainr root logger
        cotainr_root_logger = logging.getLogger("cotainr")
        for level, msg in log_level_msgs.items():
            cotainr_root_logger.log(level=level, msg=msg)

        # Check correct log level
        assert cotainr_root_logger.getEffectiveLevel() == logging.CRITICAL

        # Check correct handles
        # Pytest manipulates the handler streams to capture the logging output
        assert len(cotainr_root_logger.handlers) == 2
        for handler in cotainr_root_logger.handlers:
            assert isinstance(handler, logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        assert stdout.rstrip("\n").split("\n") == stdout_msgs
        assert stderr.rstrip("\n").split("\n") == stderr_msgs

    @pytest.mark.parametrize("verbosity", [2, 3, 5, 1000])
    def test_cotainr_debug_logging(
        self,
        verbosity,
        capsys,
        data_cotainr_debug_color_log_messages,
        patch_disable_cotainrcli_init,
    ):
        (
            log_level_msgs,
            expected_stdout_msgs,
            expected_stderr_msgs,
        ) = data_cotainr_debug_color_log_messages

        # Setup the CotainrCLI logger
        CotainrCLI()._setup_cotainr_cli_logging(
            log_settings=LogSettings(
                verbosity=verbosity, log_file_path=None, no_color=False
            )
        )
        assert "cotainr" in logging.Logger.manager.loggerDict

        # Log test messages to cotainr root logger
        cotainr_root_logger = logging.getLogger("cotainr")
        for level, msg in log_level_msgs.items():
            cotainr_root_logger.log(level=level, msg=msg)

        # Check correct log level
        assert cotainr_root_logger.getEffectiveLevel() == logging.DEBUG

        # Check correct handles
        # Pytest manipulates the handler streams to capture the logging output
        assert len(cotainr_root_logger.handlers) == 2
        for handler in cotainr_root_logger.handlers:
            assert isinstance(handler, logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        actual_stdout_msgs = stdout.rstrip("\n").split("\n")
        actual_stderr_msgs = stderr.rstrip("\n").split("\n")
        assert len(actual_stdout_msgs) == len(expected_stdout_msgs)
        assert len(actual_stderr_msgs) == len(expected_stderr_msgs)
        debug_msg_start_re = re.compile(
            # Verbose debug msg prefix along lines of:
            # 2023-09-21 10:24:06,191 - cotainr::test_cotainr_debug_logging::163::
            r"^\d{4}(-\d{2}){2} (\d{2}:){2}\d{2},\d{3} - cotainr::test_cotainr_debug_logging::\d+::"
        )
        for actual_msg, expected_msg in itertools.chain(
            zip(actual_stdout_msgs, expected_stdout_msgs),
            zip(actual_stderr_msgs, expected_stderr_msgs),
        ):
            assert debug_msg_start_re.match(actual_msg)
            assert actual_msg.endswith(expected_msg)

    @pytest.mark.parametrize("verbosity", [0, 1])
    def test_cotainr_info_logging(
        self,
        verbosity,
        capsys,
        data_cotainr_info_color_log_messages,
        patch_disable_cotainrcli_init,
    ):
        log_level_msgs, stdout_msgs, stderr_msgs = data_cotainr_info_color_log_messages

        # Setup the CotainrCLI logger
        CotainrCLI()._setup_cotainr_cli_logging(
            log_settings=LogSettings(
                verbosity=verbosity, log_file_path=None, no_color=False
            )
        )
        assert "cotainr" in logging.Logger.manager.loggerDict

        # Log test messages to cotainr root logger
        cotainr_root_logger = logging.getLogger("cotainr")
        for level, msg in log_level_msgs.items():
            cotainr_root_logger.log(level=level, msg=msg)

        # Check correct log level
        assert cotainr_root_logger.getEffectiveLevel() == logging.INFO

        # Check correct handles
        # Pytest manipulates the handler streams to capture the logging output
        assert len(cotainr_root_logger.handlers) == 2
        for handler in cotainr_root_logger.handlers:
            assert isinstance(handler, logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        assert stdout.rstrip("\n").split("\n") == stdout_msgs
        assert stderr.rstrip("\n").split("\n") == stderr_msgs

    @pytest.mark.parametrize("no_color", [True, False])
    def test_log_to_file(
        self,
        no_color,
        tmp_path,
        data_cotainr_info_no_color_log_messages,
        patch_disable_cotainrcli_init,
    ):
        (
            log_level_msgs,
            stdout_msgs,
            stderr_msgs,
        ) = data_cotainr_info_no_color_log_messages

        # Setup the CotainrCLI logger
        log_file_path = tmp_path / "cotainr_log"
        CotainrCLI()._setup_cotainr_cli_logging(
            log_settings=LogSettings(
                verbosity=0, log_file_path=log_file_path, no_color=no_color
            )
        )
        assert "cotainr" in logging.Logger.manager.loggerDict

        # Log test messages to cotainr root logger
        cotainr_root_logger = logging.getLogger("cotainr")
        for level, msg in log_level_msgs.items():
            cotainr_root_logger.log(level=level, msg=msg)

        # Check correct log level
        assert cotainr_root_logger.getEffectiveLevel() == logging.INFO

        # Check correct handles
        # Pytest manipulates the handler streams to capture the logging output
        assert len(cotainr_root_logger.handlers) == 4
        for handler in cotainr_root_logger.handlers[::2]:
            assert isinstance(handler, logging.StreamHandler)
        for handler in cotainr_root_logger.handlers[1::2]:
            assert isinstance(handler, logging.FileHandler)

        # Check correct logging, incl. message format, coloring, log level to file
        assert (
            log_file_path.with_suffix(".out").read_text().rstrip("\n").split("\n")
            == stdout_msgs
        )
        assert (
            log_file_path.with_suffix(".err").read_text().rstrip("\n").split("\n")
            == stderr_msgs
        )

    def test_no_color_on_console(
        self,
        capsys,
        data_cotainr_info_no_color_log_messages,
        patch_disable_cotainrcli_init,
    ):
        (
            log_level_msgs,
            stdout_msgs,
            stderr_msgs,
        ) = data_cotainr_info_no_color_log_messages

        # Setup the CotainrCLI logger
        CotainrCLI()._setup_cotainr_cli_logging(
            log_settings=LogSettings(verbosity=0, log_file_path=None, no_color=True)
        )
        assert "cotainr" in logging.Logger.manager.loggerDict

        # Log test messages to cotainr root logger
        cotainr_root_logger = logging.getLogger("cotainr")
        for level, msg in log_level_msgs.items():
            cotainr_root_logger.log(level=level, msg=msg)

        # Check correct log level
        assert cotainr_root_logger.getEffectiveLevel() == logging.INFO

        # Check correct handles
        # Pytest manipulates the handler streams to capture the logging output
        assert len(cotainr_root_logger.handlers) == 2
        for handler in cotainr_root_logger.handlers:
            assert isinstance(handler, logging.StreamHandler)

        # Check correct logging, incl. message format, coloring, log level, and output stream
        # readouterr clears its content when returning
        stdout, stderr = capsys.readouterr()
        assert stdout.rstrip("\n").split("\n") == stdout_msgs
        assert stderr.rstrip("\n").split("\n") == stderr_msgs
