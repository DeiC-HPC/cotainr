"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import logging
import platform
import re
import subprocess
import urllib.error

import pytest

from cotainr.container import SingularitySandbox
from cotainr.pack import CondaInstall
from cotainr.tracing import LogSettings

from ..container.data import data_cached_ubuntu_sif
from ..container.patches import patch_disable_singularity_sandbox_subprocess_runner
from .patches import (
    patch_disable_conda_install_bootstrap_conda,
    patch_disable_conda_install_download_miniforge_installer,
)
from .stubs import StubEmptyLicensePopen, StubShowLicensePopen


class TestConstructor:
    def test_attributes(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
        assert conda_install.sandbox == sandbox
        assert conda_install.prefix == "/opt/conda"
        assert conda_install.license_accepted
        assert conda_install.log_dispatcher is None
        assert conda_install._verbosity == 0

    def test_beforehand_license_acceptance(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            CondaInstall(sandbox=sandbox, license_accepted=True)

        # Check that the message about accepting Miniforge license on
        # beforehand is shown
        (
            _sandbox_create_cmd,
            _sandbox_uname_cmd,
            miniforge_license_accept_cmd,
            _conda_bootstrap_cmd,
            _conda_bootstrap_clean_cmd,
        ) = capsys.readouterr().out.strip().split("\n")
        assert miniforge_license_accept_cmd == (
            "You have accepted the Miniforge installer license via the command line option "
            "'--accept-licenses'."
        )

    def test_cleanup(
        self,
        capsys,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)

            # Check that installer was removed after use
            assert not (
                conda_install.sandbox.sandbox_dir / "conda_installer.sh"
            ).exists()

        (
            _sandbox_create_cmd,
            _sandbox_uname_cmd,
            _miniforge_license_accept_cmd,
            bootstrap_cmd,
            clean_cmd,
            _empty_string,
        ) = capsys.readouterr().out.split("\n")

        # Check that installer (mock) was created in the first place
        assert bootstrap_cmd.startswith("PATCH: Bootstrapped Conda using ")
        assert bootstrap_cmd.endswith("conda_installer.sh")

        # Check that the conda clean (mock) command ran
        assert clean_cmd.startswith("PATCH: Ran command in sandbox:")
        assert "'conda', 'clean', '-y', '-a'" in clean_cmd

    def test_setup_log_dispatcher(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        log_settings = LogSettings(verbosity=1)
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(
                sandbox=sandbox, license_accepted=True, log_settings=log_settings
            )
        assert conda_install._verbosity == 1
        assert conda_install.log_dispatcher.verbosity == log_settings.verbosity
        assert conda_install.log_dispatcher.log_file_path == log_settings.log_file_path
        assert conda_install.log_dispatcher.no_color == log_settings.no_color
        assert conda_install.log_dispatcher.map_log_level is CondaInstall._map_log_level
        assert conda_install.log_dispatcher.logger_stdout.name == "CondaInstall.out"
        assert conda_install.log_dispatcher.logger_stderr.name == "CondaInstall.err"


@pytest.mark.conda_integration
@pytest.mark.singularity_integration
class TestAddEnvironment:
    def test_env_creation(self, tmp_path, data_cached_ubuntu_sif):
        conda_env_path = tmp_path / "conda_env.yml"
        conda_env_path.write_text(
            "channels:\n  - conda-forge\ndependencies:\n  - python"
        )
        conda_env_name = "some_env_name_6021"
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            conda_install.add_environment(path=conda_env_path, name=conda_env_name)
            process = sandbox.run_command_in_container(cmd="conda info -e")
            assert re.search(
                # We expect to find a line in the list of environments similar to:
                # some_env_name_6021         /opt/conda/envs/some_env_name_6021
                rf"^{conda_env_name}(\s)+/opt/conda/envs/{conda_env_name}$",
                process.stdout,
                flags=re.MULTILINE,
            )

    def test_other_conda_channels_than_condaforge(
        self, tmp_path, data_cached_ubuntu_sif
    ):
        conda_env_path = tmp_path / "conda_env.yml"
        conda_env_path.write_text(
            "channels:\n  - bioconda\ndependencies:\n  - samtools"
        )
        conda_env_name = "some_bioconda_env_6021"
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            conda_install.add_environment(path=conda_env_path, name=conda_env_name)
            process = sandbox.run_command_in_container(cmd="conda info -e")
            assert re.search(
                # We expect to find a line in the list of environments similar to:
                # some_env_name_6021         /opt/conda/envs/some_env_name_6021
                rf"^{conda_env_name}(\s)+/opt/conda/envs/{conda_env_name}$",
                process.stdout,
                flags=re.MULTILINE,
            )


@pytest.mark.conda_integration
@pytest.mark.singularity_integration
class TestCleanupUnusedFiles:
    def test_all_unneeded_removed(self, data_cached_ubuntu_sif):
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            CondaInstall(sandbox=sandbox, license_accepted=True)
            process = sandbox.run_command_in_container(cmd="conda clean -d -a")
            clean_msg = (
                "There are no unused tarball(s) to remove.\n"
                "There are no index cache(s) to remove.\n"
                "There are no unused package(s) to remove.\n"
                "There are no tempfile(s) to remove.\n"
                "There are no logfile(s) to remove."
            )
            assert process.stdout.strip() == clean_msg


@pytest.mark.conda_integration
@pytest.mark.singularity_integration
class Test_BootstrapConda:
    def test_correct_conda_installer_bootstrap(self, data_cached_ubuntu_sif):
        with SingularitySandbox(base_image=data_cached_ubuntu_sif) as sandbox:
            conda_install_dir = sandbox.sandbox_dir / "opt/conda"
            assert not conda_install_dir.exists()
            CondaInstall(sandbox=sandbox, license_accepted=True)

            # Check that conda has been installed
            assert conda_install_dir.exists()

            # Check that we are using our installed conda
            process = sandbox.run_command_in_container(cmd="conda info --base")
            assert process.stdout.strip() == "/opt/conda"

            # Check that the installed conda is up-to-date
            process = sandbox.run_command_in_container(
                cmd="conda update -n base -d conda"
            )
            assert "# All requested packages already installed." in process.stdout


class Test_CheckCondaBootstrapIntegrity:
    def test_bail_on_interfering_conda_installs(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            with pytest.raises(RuntimeError) as exc_info:
                # Abuse that the output of the mocked subprocess runner in the
                # sandbox is a line about the command run
                # - not the actual output of "conda info --base"
                conda_install._check_conda_bootstrap_integrity()

        exc_msg = str(exc_info.value)
        assert exc_msg.startswith(
            "Multiple Conda installs interfere. "
            "We risk destroying the Conda install in "
            "PATCH: Ran command in sandbox: "
        )
        assert exc_msg.endswith("Aborting!")
        assert "'conda', 'info', '--base'" in exc_msg


class Test_DisplayMessage:
    @pytest.mark.parametrize("level", [logging.DEBUG, logging.INFO])
    def test_log_to_stdout(
        self,
        level,
        caplog,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        log_settings = LogSettings(verbosity=3)
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(
                sandbox=sandbox, license_accepted=True, log_settings=log_settings
            )
            conda_install._display_message(msg="test_6021", log_level=level)

        assert caplog.records[-1].levelno == level
        assert caplog.records[-1].name == "CondaInstall.out"
        assert caplog.records[-1].msg == "test_6021"

    @pytest.mark.parametrize(
        "level", [logging.WARNING, logging.ERROR, logging.CRITICAL]
    )
    def test_log_to_stderr(
        self,
        level,
        caplog,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        log_settings = LogSettings(verbosity=0)
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(
                sandbox=sandbox, license_accepted=True, log_settings=log_settings
            )
            conda_install._display_message(msg="test_6021", log_level=level)

        assert caplog.records[-1].levelno == level
        assert caplog.records[-1].name == "CondaInstall.err"
        assert caplog.records[-1].msg == "test_6021"

    def test_no_log_dispatcher(
        self,
        capsys,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            conda_install._display_message(msg="test_6021", log_level=logging.INFO)

        stdout_lines = capsys.readouterr().out.rstrip("\n").split("\n")
        assert stdout_lines[-1] == "test_6021"

    def test_no_log_level(
        self,
        capsys,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        log_settings = LogSettings(verbosity=1)
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(
                sandbox=sandbox, license_accepted=True, log_settings=log_settings
            )
            conda_install._display_message(msg="test_6021")

        stdout_lines = capsys.readouterr().out.rstrip("\n").split("\n")
        assert stdout_lines[-1] == "test_6021"


class Test_DisplayMiniforgeLicenseForAcceptance:
    def test_accepting_license(
        self,
        factory_mock_input,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr(subprocess, "Popen", StubShowLicensePopen)
        monkeypatch.setattr("builtins.input", factory_mock_input("yes"))
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox)

        stdout_lines = capsys.readouterr().out.strip().split("\n")
        assert "You have accepted the Miniforge installer license." in stdout_lines
        assert conda_install.license_accepted

    @pytest.mark.parametrize("answer", ["n", "N", "", "some_answer_6021"])
    def test_not_accepting_license(
        self,
        answer,
        factory_mock_input,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr(subprocess, "Popen", StubShowLicensePopen)
        monkeypatch.setattr("builtins.input", factory_mock_input(answer))
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            with pytest.raises(SystemExit):
                CondaInstall(sandbox=sandbox)

        stdout_lines = capsys.readouterr().out.strip().split("\n")
        assert (
            "You have not accepted the Miniforge installer license. Aborting!"
        ) in stdout_lines

    def test_installer_not_showing_license(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        monkeypatch,
    ):
        monkeypatch.setattr(subprocess, "Popen", StubEmptyLicensePopen)
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            with pytest.raises(
                RuntimeError,
                match="^No license seems to be displayed by the Miniforge installer.$",
            ):
                CondaInstall(sandbox=sandbox)

    def test_license_interaction_handling(
        self,
        factory_mock_input,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr(subprocess, "Popen", StubShowLicensePopen)
        monkeypatch.setattr("builtins.input", factory_mock_input("yes"))
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            CondaInstall(sandbox=sandbox)

        stdout = capsys.readouterr().out.strip()
        stdout_lines = stdout.split("\n")

        # Check that we send the "ENTER" and kill the process.
        assert "StubShowLicensePopen received: input='\\n'." in stdout_lines
        assert "StubShowLicensePopen killed." in stdout_lines

        # Check that the prompt for "ENTER" is not displayed to the user
        assert "Please, press ENTER to continue\n>>> " not in stdout

        # Check that the license is displayed to the user
        assert "STUB:\n\n\nThis is the license terms..." in stdout

    @pytest.mark.conda_integration
    def test_miniforge_still_showing_license(
        self,
        factory_mock_input,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_singularity_sandbox_subprocess_runner,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr("builtins.input", factory_mock_input("yes"))
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            sandbox.architecture = platform.machine()
            CondaInstall(sandbox=sandbox)

        stdout = capsys.readouterr().out.strip()

        # Check that various lines that we expect to always be part of
        # https://github.com/conda-forge/miniforge/blob/main/LICENSE are still
        # shown to the user when extracting and showing the Miniforge license
        # terms from the installer - just to have an idea that the license is
        # still being shown correctly to the user
        assert (
            "Miniforge installer code uses BSD-3-Clause license as stated below."
        ) in stdout
        assert (
            "Miniforge installer comes with a bootstrapping executable that is used\n"
            "when installing miniforge and is deleted after miniforge is installed."
        ) in stdout
        assert "conda-forge" in stdout
        assert "All rights reserved." in stdout


class Test_DownloadMiniforgeInstaller:
    def test_installer_download_success(
        self,
        patch_urllib_urlopen_as_bytes_stream,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            # Just needs some supported architecture
            sandbox.architecture = "x86_64"
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            conda_installer_path = (
                conda_install.sandbox.sandbox_dir / "conda_installer_download"
            )
            conda_install._download_miniforge_installer(
                installer_path=conda_installer_path
            )
            conda_installer_strings = [
                b"PATCH: Bytes returned by urlopen for url=",
                b"'https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-",
            ]
            conda_installer_bytes_string = conda_installer_path.read_bytes()
            for installer_string in conda_installer_strings:
                assert installer_string in conda_installer_bytes_string

    @pytest.mark.conda_integration  # technically not a test that depends on Conda - but a very slow one...
    def test_installer_download_fail(
        self,
        patch_urllib_urlopen_force_fail,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            # Just needs some supported architecture
            sandbox.architecture = "x86_64"
            with pytest.raises(
                urllib.error.URLError, match="PATCH: urlopen error forced for url="
            ):
                CondaInstall(sandbox=sandbox)

    def test_unknown_architecture(
        self, patch_disable_singularity_sandbox_subprocess_runner
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            sandbox.architecture = None
            with pytest.raises(
                RuntimeError,
                match=(
                    r".*"
                    r"Cotainr.*"
                    r"CondaInstall.*"
                    r"which indicates that it is not running in a container sandbox context"
                ),
            ):
                CondaInstall(sandbox=sandbox, license_accepted=True)


class Test_GetInstallScript:
    @pytest.mark.parametrize("arch", ["arm64", "aarch64"])
    def test_arm_success(self, arch):
        assert CondaInstall._get_install_script(arch) == "Miniforge3-Linux-aarch64.sh"

    def test_x86_success(self):
        assert (
            CondaInstall._get_install_script("x86_64") == "Miniforge3-Linux-x86_64.sh"
        )

    @pytest.mark.parametrize(
        "arch",
        [
            "test",
            "arms64",
            "aarchs64",
            "None",
            "Weird",
            "WINDOWS",
            "icecream",
            "86_64",
            "pc",
        ],
    )
    def test_unknown_arch_error(self, arch):
        with pytest.raises(
            ValueError,
            match=(
                r".*"
                r"Cotainr.*"
                r"CondaInstall.*"
                r"supports.*"
                r"x86_64.*"
                r"arm64.*"
                r"aarch64.*"
                rf"{arch}.*"
            ),
        ):
            CondaInstall._get_install_script(arch)


class Test_CondaVerbosityArg:
    @pytest.mark.parametrize(
        ["verbosity", "verbosity_arg"],
        [(-1, " -q"), (0, " -q"), (1, ""), (2, " -v"), (3, " -vv"), (4, " -vvv")],
    )
    def test_correct_mapping_of_verbosity(
        self,
        verbosity,
        verbosity_arg,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            conda_install._verbosity = verbosity
            assert conda_install._conda_verbosity_arg == verbosity_arg


class Test_LoggingFilters:
    def test_correctly_ordered_list_of_filters(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)

        filter_names = [
            filter_.__class__.__name__ for filter_ in conda_install._logging_filters
        ]
        assert filter_names == [
            "StripANSIEscapeCodes",
            "OnlyFinalProgressbarFilter",
            "NoEmptyLinesFilter",
        ]

    def test_strip_ANSI_codes_filter(
        self,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            filter_ = conda_install._logging_filters[0]
            assert filter_.__class__.__name__ == "StripANSIEscapeCodes"

        rec = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test_path",
            lineno=0,
            msg=(
                "\x1b[38;5;8msome_\x1b[38;5;3m\x1b[38;5;1m\033[38;5;160mlong\x1b[0m_message_"
                "\033[Awith\x1b[A_a_lot_of_AN\x1b[KSI_codes_\x1b[B6021"
            ),
            args=None,
            exc_info=None,
        )
        filter_.filter(rec)
        assert rec.msg == "some_long_message_with_a_lot_of_ANSI_codes_6021"

    @pytest.mark.parametrize(["msg", "keep"], [("", False), ("some_msg_6021", True)])
    def test_no_empty_lines_filter(
        self,
        msg,
        keep,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            filter_ = conda_install._logging_filters[2]
            assert filter_.__class__.__name__ == "NoEmptyLinesFilter"

        rec = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test_path",
            lineno=0,
            msg=msg,
            args=None,
            exc_info=None,
        )
        assert filter_.filter(rec) == keep

    @pytest.mark.parametrize(
        ["msg", "keep"],
        [
            (
                "CondaInstall.out:-: openssl-3.1.3        | 2.5 MB    |            |   0%",
                False,
            ),
            (
                "CondaInstall.out:-: jsonpatch-1.33       | 17 KB     | #########4 |  94%",
                False,
            ),
            (
                "CondaInstall.out:-: libnsl-2.0.0         | 32 KB     | ####9      |  49%",
                False,
            ),
            (
                "CondaInstall.out:-: zstandard-0.21.0     | 395 KB    | 4          |   4%",
                False,
            ),
            (
                "CondaInstall.out:-: python-3.11.5        | 29.4 MB   | ########## | 100%",
                True,
            ),
        ],
    )
    def test_only_final_progressbar_filter(
        self,
        msg,
        keep,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_singularity_sandbox_subprocess_runner,
    ):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            conda_install = CondaInstall(sandbox=sandbox, license_accepted=True)
            filter_ = conda_install._logging_filters[1]
            assert filter_.__class__.__name__ == "OnlyFinalProgressbarFilter"

        rec = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test_path",
            lineno=0,
            msg=msg,
            args=None,
            exc_info=None,
        )
        assert filter_.filter(rec) == keep


class Test_MapLogLevel:
    @pytest.mark.parametrize(
        ["msg", "log_level"],
        [
            ("DEBUG", logging.DEBUG),
            ("VERBOSE", logging.DEBUG),
            ("TRACE", logging.DEBUG),
            ("DEBUG:6021", logging.DEBUG),
            ("VERBOSE 6021", logging.DEBUG),
            ("TRACEING my day away", logging.DEBUG),
            ("INFO", logging.INFO),
            ("INFORMATION", logging.INFO),
            ("WARNING", logging.WARNING),
            ("WARNING-log", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("ERROR_MSG", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
            ("CRITICAL/mission", logging.CRITICAL),
            ("unknown", logging.INFO),
            ("debug something", logging.INFO),
            (
                "some messages containing DEBUG, VERBOSE, TRACE, WARNING, ERROR, and CRITICAL",
                logging.INFO,
            ),
        ],
    )
    def test_correct_log_level_mapping(self, msg, log_level):
        assert CondaInstall._map_log_level(msg=msg) == log_level
