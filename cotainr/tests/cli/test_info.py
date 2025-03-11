"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import argparse
import re
import subprocess

import pytest

from cotainr.cli import CotainrCLI, Info

from ..util.patches import patch_empty_system, patch_system_with_actual_file


class TestExecute:
    def test_report_structure(self, capsys):
        Info().execute()
        stdout = capsys.readouterr().out

        # Dependency report section
        assert stdout.startswith(
            "Dependency report\n"
            "-------------------------------------------------------------------------------\n"
        )
        # One line with python version check
        assert (
            sum(line.startswith("    - Running python ") for line in stdout.split("\n"))
            == 1
        )
        # One line with singularity / apptainer version check
        assert (
            sum(
                any(
                    provider in line
                    for provider in ["singularity", "singularity-ce", "apptainer"]
                )
                for line in stdout.split("\n")
            )
            == 1
        )

        # Systems info section
        assert (
            "\n"
            "System info\n"
            "-------------------------------------------------------------------------------\n"
        ) in stdout

    def test_with_systems(self, capsys, patch_system_with_actual_file):
        Info().execute()
        stdout = capsys.readouterr().out
        assert stdout.endswith(
            "System info\n"
            "-------------------------------------------------------------------------------\n"
            "Available system configurations:\n"
            "    - some_system_6021\n"
            "    - another_system_6021\n"
        )

    def test_without_systems(self, capsys, patch_empty_system):
        Info().execute()
        stdout = capsys.readouterr().out
        assert stdout.endswith(
            "System info\n"
            "-------------------------------------------------------------------------------\n"
            "No system configurations available\n"
        )


class TestAddArguments:
    def test_no_arguments_added(self):
        parser = argparse.ArgumentParser()
        Info.add_arguments(parser=parser)
        args = parser.parse_args(args=[])
        assert not vars(args)


class TestHelpMessage:
    def test_CLI_subcommand_help_message(self, argparse_options_line, capsys):
        with pytest.raises(SystemExit):
            CotainrCLI(args=["info", "--help"])
        stdout = capsys.readouterr().out
        assert stdout == (
            # Capsys apparently assumes an 80 char terminal (?) - thus extra '\n'
            "usage: cotainr info [-h]\n\n"
            "Obtain info about the state of all required dependencies for building a\n"
            "container.\n\n"
            f"{argparse_options_line}"
            "  -h, --help  show this help message and exit\n"
        )


class Test_check_python_dependency:
    def test_formatting(self):
        # Check for formatting like "Running python 3.11.0 >= 3.9.0, OK"
        assert re.match(
            (
                r"^Running python \d+\.\d+\.\d+ (>=)|(<) \d+\.\d+\.\d+, "
                r"(\\x1b\[38;5;1mOK\\x1b\[0m)|(\\x1b\[38;5;1mERROR\\x1b\[0m)$"
            ),
            Info()._check_python_dependency(),
        )


class Test_check_singularity_dependency:
    def test_found_apptainer(self, monkeypatch):
        monkeypatch.setattr(
            subprocess,
            "check_output",
            lambda *args, **kwargs: "apptainer version 1.0.0",
        )
        assert (
            Info()._check_singularity_dependency()
            == "Found apptainer 1.0.0 >= 1.0.0, \x1b[38;5;2mOK\x1b[0m"
        )

    def test_found_singularity(self, monkeypatch):
        monkeypatch.setattr(
            subprocess,
            "check_output",
            lambda *args, **kwargs: "singularity version 3.7.4-1",
        )
        assert (
            Info()._check_singularity_dependency()
            == "Found singularity 3.7.4-1 >= 3.7.4, \x1b[38;5;2mOK\x1b[0m"
        )

    def test_found_singularity_ce(self, monkeypatch):
        monkeypatch.setattr(
            subprocess,
            "check_output",
            lambda *args, **kwargs: "singularity-ce version 3.11.4-1",
        )
        assert (
            Info()._check_singularity_dependency()
            == "Found singularity-ce 3.11.4-1 >= 3.9.2, \x1b[38;5;2mOK\x1b[0m"
        )

    def test_found_unknown(self, monkeypatch):
        monkeypatch.setattr(
            subprocess,
            "check_output",
            lambda *args, **kwargs: "container_tool_6021 version 60.2.1",
        )
        assert (
            Info()._check_singularity_dependency()
            == "Found unknown singularity provider: container_tool_6021 60.2.1"
        )

    def test_not_found(self, monkeypatch):
        def not_found(*args, **kwargs):
            raise FileNotFoundError()

        monkeypatch.setattr(
            subprocess,
            "check_output",
            not_found,
        )
        assert (
            Info()._check_singularity_dependency()
            == "apptainer/singularity not found, \x1b[38;5;1mERROR\x1b[0m"
        )


class Test_check_version:
    @pytest.mark.parametrize(
        "version,min_version,cmp_result",
        [
            ((3, 9, 0), (3, 9, 0), ">= 3.9.0, \x1b[38;5;2mOK\x1b[0m"),
            ((0, 1, 12), (0, 0, 1), ">= 0.0.1, \x1b[38;5;2mOK\x1b[0m"),
            ((3, 7, 14), (3, 9, 0), "< 3.9.0, \x1b[38;5;1mERROR\x1b[0m"),
            ((1, 0, 0), (3, 9, 0), "< 3.9.0, \x1b[38;5;1mERROR\x1b[0m"),
        ],
    )
    def test_version_comparison(self, version, min_version, cmp_result):
        assert (
            Info()._check_version(version=version, min_version=min_version)
            == cmp_result
        )

    def test_wrong_input_len(self):
        with pytest.raises(TypeError) as exc_info:
            Info()._check_version(version=(1, 0, 0, 0), min_version=(1, 0, 0))
        assert str(exc_info.value) == (
            "The 'version=(1, 0, 0, 0)' argument must be "
            "a (major, minor, patchlevel) tuple of integers"
        )

    def test_wrong_input_type(self):
        with pytest.raises(TypeError) as exc_info:
            Info()._check_version(version=(1, 0, 0), min_version="1.0.0")
        assert str(exc_info.value) == (
            "The 'min_version=1.0.0' argument must be "
            "a (major, minor, patchlevel) tuple of integers"
        )

    def test_wrong_part_type(self):
        with pytest.raises(TypeError) as exc_info:
            Info()._check_version(version=("1", "0", "0"), min_version=(1, 0, 0))
        assert str(exc_info.value) == (
            "The 'version=('1', '0', '0')' argument must be "
            "a (major, minor, patchlevel) tuple of integers"
        )
