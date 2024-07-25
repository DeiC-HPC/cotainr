"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import logging
from pathlib import Path

import pytest

from cotainr.container import SingularitySandbox
from cotainr.tracing import LogDispatcher, LogSettings
from .data import data_cached_alpine_sif
from ..util.patches import patch_disable_stream_subprocess


class TestConstructor:
    def test_attributes(self):
        base_image = "my_base_image_6021"
        sandbox = SingularitySandbox(base_image=base_image)
        assert sandbox.base_image == base_image
        assert sandbox.sandbox_dir is None
        assert sandbox.log_dispatcher is None
        assert sandbox._verbosity == 0

    def test_setup_log_dispatcher(self):
        log_settings = LogSettings(verbosity=1)
        sandbox = SingularitySandbox(
            base_image="my_base_image_6021", log_settings=log_settings
        )
        assert sandbox._verbosity == 1
        assert sandbox.log_dispatcher.verbosity == log_settings.verbosity
        assert sandbox.log_dispatcher.log_file_path == log_settings.log_file_path
        assert sandbox.log_dispatcher.no_color == log_settings.no_color
        assert sandbox.log_dispatcher.map_log_level is SingularitySandbox._map_log_level
        assert sandbox.log_dispatcher.logger_stdout.name == "SingularitySandbox.out"
        assert sandbox.log_dispatcher.logger_stderr.name == "SingularitySandbox.err"


class TestContext:
    def test_add_verbosity_arg(self, capsys, patch_disable_stream_subprocess):
        with SingularitySandbox(base_image="my_base_image_6021"):
            pass
        stdout_lines = capsys.readouterr().out.rstrip("\n").split("\n")
        assert "args=['singularity', '-q', " in stdout_lines[0]

    @pytest.mark.singularity_integration
    def test_singularity_sandbox_creation(self, data_cached_alpine_sif):
        with SingularitySandbox(base_image=data_cached_alpine_sif) as sandbox:
            # Check that the sandbox contains the expected singularity files
            assert (sandbox.sandbox_dir / "environment").exists()
            assert (sandbox.sandbox_dir / "singularity").exists()
            assert (sandbox.sandbox_dir / ".singularity.d").exists()

    def test_tmp_dir_setup_and_teardown(self, patch_disable_stream_subprocess):
        test_dir = Path().resolve()
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            # Check that we are in the temporary sandbox directory
            sandbox_dir = sandbox.sandbox_dir
            assert sandbox_dir.stem == "singularity_sandbox"
            assert sandbox_dir != test_dir
            assert Path().resolve() == sandbox_dir

        # Check that we have exited and removed the temporary sandbox directory
        assert Path().resolve() == test_dir
        assert sandbox.sandbox_dir is None
        assert not sandbox_dir.exists()


class TestAddToEnv:
    def test_add_twice(self, patch_disable_stream_subprocess):
        lines = ["first script line", "second script line"]
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            env_file = sandbox.sandbox_dir / "environment"
            for line in lines:
                sandbox.add_to_env(shell_script=line)
            assert env_file.read_text() == lines[0] + "\n" + lines[1] + "\n"

    def test_newline_encapsulation(self, patch_disable_stream_subprocess):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            env_file = sandbox.sandbox_dir / "environment"
            shell_script = "fancy shell_script\nas a double line string"
            sandbox.add_to_env(shell_script=shell_script)
            assert env_file.read_text() == shell_script + "\n"

    def test_shell_script_append(self, patch_disable_stream_subprocess):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            env_file = sandbox.sandbox_dir / "environment"
            existing_shell_script = "some existing\nshell script"
            env_file.write_text(existing_shell_script)
            new_shell_script = "fancy_shell_script\nas_a_string"
            sandbox.add_to_env(shell_script=new_shell_script)
            assert (
                env_file.read_text().strip() == existing_shell_script + new_shell_script
            )


@pytest.mark.singularity_integration
class TestBuildImage:
    def test_add_verbosity_arg(self, capsys, patch_disable_stream_subprocess):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            sandbox.build_image(path="some_path_6021")
        stdout_lines = capsys.readouterr().out.rstrip("\n").split("\n")
        assert "args=['singularity', '-q', " in stdout_lines[-1]

    def test_fix_perms_on_oci_docker_images(self, tmp_path):
        # Tests correct permission handling in relation to the error:
        #   FATAL:   While performing build: packer failed to pack: copy Failed:
        #   symlink GlobalSign_Root_R46.pem
        #   .../var/lib/ca-certificates/openssl/002c0b4f.0: permission denied
        # which seems to be a problem with all SUSE based docker images.
        # https://github.com/DeiC-HPC/cotainr/issues/48
        image_path = tmp_path / "image_6021"
        assert not image_path.exists()
        with SingularitySandbox(base_image="docker://opensuse/leap:15.4") as sandbox:
            sandbox.build_image(path=image_path)

        assert image_path.exists()

    def test_overwrite_existing_image(self, data_cached_alpine_sif, tmp_path):
        existing_singularity_image_path = tmp_path / "existing_image_6021"
        existing_singularity_image_path.write_bytes(data_cached_alpine_sif.read_bytes())
        existing_singularity_image_stats = existing_singularity_image_path.stat()
        assert existing_singularity_image_path.exists()
        with SingularitySandbox(base_image=data_cached_alpine_sif) as sandbox:
            sandbox.build_image(path=existing_singularity_image_path)

        # Check that the image file has been overwritten
        assert (
            existing_singularity_image_path.stat() != existing_singularity_image_stats
        )

    def test_sandbox_image_equality(
        self, data_cached_alpine_sif, singularity_exec, tmp_path
    ):
        built_image_path = tmp_path / "built_image_6021"
        with SingularitySandbox(base_image=data_cached_alpine_sif) as sandbox:
            sandbox.build_image(path=built_image_path)

        # Simple test of equality based on OS release of base image and built container
        base_image_os_release = singularity_exec(
            f"{data_cached_alpine_sif} cat /etc/os-release"
        ).stdout
        built_image_os_release = singularity_exec(
            f"{built_image_path} cat /etc/os-release"
        ).stdout
        assert base_image_os_release == built_image_os_release


@pytest.mark.singularity_integration
class TestRunCommandInContainer:
    def test_add_verbosity_arg(self, capsys, patch_disable_stream_subprocess):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            sandbox.run_command_in_container(cmd="ls")
        stdout_lines = capsys.readouterr().out.rstrip("\n").split("\n")
        assert "args=['singularity', '-q', " in stdout_lines[-1]

    def test_correct_umask(self, data_cached_alpine_sif, context_set_umask):
        test_file = "test_file_6021"
        with context_set_umask(0o007):  # default umask on LUMI
            with SingularitySandbox(base_image=data_cached_alpine_sif) as sandbox:
                sandbox.run_command_in_container(cmd=f"touch /{test_file}")
                test_file_path = sandbox.sandbox_dir / test_file
                assert test_file_path.exists()
                test_file_mode = test_file_path.stat().st_mode
                # file permissions extracted from the last 3 octal digits of st_mode
                test_file_permissions = test_file_mode & 0o777
                assert oct(test_file_permissions) == "0o644"

    def test_error_handling(self, data_cached_alpine_sif):
        cmd = "some6021 non-meaningful command"
        with SingularitySandbox(base_image=data_cached_alpine_sif) as sandbox:
            with pytest.raises(
                ValueError, match=f"^Invalid command {cmd=} passed to Singularity"
            ):
                sandbox.run_command_in_container(cmd=cmd)

    def test_no_home(self, data_cached_alpine_sif):
        with SingularitySandbox(base_image=data_cached_alpine_sif) as sandbox:
            process = sandbox.run_command_in_container(cmd="ls -l /home")
        assert process.stdout.strip() == "total 0"


class Test_AssertWithinSandboxContext:
    def test_pass_inside_sandbox(self):
        sandbox = SingularitySandbox(base_image="my_base_image_6021")
        sandbox.sandbox_dir = Path()
        sandbox._assert_within_sandbox_context()

    def test_fail_outside_sandbox(self):
        sandbox = SingularitySandbox(base_image="my_base_image_6021")
        with pytest.raises(
            ValueError,
            match=r"^The operation is only valid inside a sandbox context\.$",
        ):
            sandbox._assert_within_sandbox_context()


class Test_SubprocessRunner:
    def test_logger_prefix_for_custom_log_dispatcher(
        self,
        capsys,
        patch_disable_stream_subprocess,
    ):
        log_dispatcher = LogDispatcher(
            name="test_dispatcher_6021",
            map_log_level_func=lambda msg: logging.WARNING,
            log_settings=LogSettings(),
        )
        sandbox = SingularitySandbox(base_image="my_base_image_6021")
        sandbox._subprocess_runner(
            custom_log_dispatcher=log_dispatcher, args=["some_arg_6021"]
        )
        stderr = capsys.readouterr().err
        assert stderr.startswith("SingularitySandbox/test_dispatcher_6021.err")

    def test_use_own_log_dispatcher(self, capsys, patch_disable_stream_subprocess):
        sandbox = SingularitySandbox(
            base_image="my_base_image_6021", log_settings=LogSettings(verbosity=1)
        )
        sandbox._subprocess_runner(args=["some_arg_6021"])
        stderr = capsys.readouterr().err
        assert stderr.startswith("SingularitySandbox.err")


class Test_AddVerbosityArg:
    @pytest.mark.parametrize(
        ["verbosity", "verbosity_arg"],
        [(-1, "-s"), (0, "-q"), (1, None), (2, None), (3, "-v"), (4, "-v")],
    )
    def test_correct_mapping_of_verbosity(self, verbosity, verbosity_arg):
        sandbox = SingularitySandbox(base_image="my_base_image_6021")
        sandbox._verbosity = verbosity
        args = ["first_arg", "last_arg"]
        sandbox._add_verbosity_arg(args=args)
        if verbosity_arg is not None:
            assert len(args) == 3
            assert args[0] == "first_arg"
            assert args[1] == verbosity_arg
            assert args[2] == "last_arg"
        else:
            assert len(args) == 2
            assert args[0] == "first_arg"
            assert args[1] == "last_arg"

    def test_return_args(self):
        sandbox = SingularitySandbox(base_image="my_base_image_6021")
        args = ["some_arg"]
        returned_args = sandbox._add_verbosity_arg(args=args)
        assert returned_args is args


class Test_MapLogLevel:
    @pytest.mark.parametrize(
        ["msg", "log_level"],
        [
            ("DEBUG", logging.DEBUG),
            ("VERBOSE", logging.DEBUG),
            ("DEBUG:6021", logging.DEBUG),
            ("VERBOSE 6021", logging.DEBUG),
            ("INFO", logging.INFO),
            ("LOG", logging.INFO),
            ("INFORMATION", logging.INFO),
            ("LOG some text", logging.INFO),
            ("WARNING", logging.WARNING),
            ("WARNING-log", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("ERROR_MSG", logging.ERROR),
            ("ABRT", logging.CRITICAL),
            ("FATAL", logging.CRITICAL),
            ("ABRT/mission", logging.CRITICAL),
            ("FATALities", logging.CRITICAL),
            ("unknown", logging.INFO),
            (
                "some messages containing DEBUG, VERBOSE, WARNING, ERROR, ABRT, and FATAL",
                logging.INFO,
            ),
        ],
    )
    def test_correct_log_level_mapping(self, msg, log_level):
        assert SingularitySandbox._map_log_level(msg=msg) == log_level
