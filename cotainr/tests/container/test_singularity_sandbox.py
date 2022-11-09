from pathlib import Path
import subprocess

import pytest

from cotainr.container import SingularitySandbox
from cotainr.tests.container.data import data_singularity_image
from cotainr.tests.util.patches import patch_stream_subprocess


class TestConstructor:
    def test_attributes(self):
        base_image = "my_base_image_6021"
        sandbox = SingularitySandbox(base_image=base_image)
        assert sandbox.base_image == base_image
        assert sandbox.sandbox_dir is None


class TestContext:
    @pytest.mark.singularity_integration
    def test_singularity_sandbox_creation(self, data_singularity_image):
        with SingularitySandbox(base_image=data_singularity_image) as sandbox:
            # Check that the sandbox contains the expected singularity files
            assert (sandbox.sandbox_dir / "environment").exists()
            assert (sandbox.sandbox_dir / "singularity").exists()
            assert (sandbox.sandbox_dir / ".singularity.d").exists()

    def test_tmp_dir_setup_and_teardown(self, patch_stream_subprocess):
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
    def test_newline_encapsulation(self, patch_stream_subprocess):
        with SingularitySandbox(base_image="my_base_image_6021") as sandbox:
            env_file = sandbox.sandbox_dir / "environment"
            shell_script = "fancy shell_script\nas a double line string"
            sandbox.add_to_env(shell_script=shell_script)
            assert env_file.read_text() == shell_script + "\n"

    def test_shell_script_append(self, patch_stream_subprocess):
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
    def test_overwrite_existing_image(self, data_singularity_image, tmp_path):
        existing_singularity_image_path = tmp_path / "existing_image_6021"
        existing_singularity_image_path.write_bytes(data_singularity_image.read_bytes())
        existing_singularity_image_stats = existing_singularity_image_path.stat()
        assert existing_singularity_image_path.exists()
        with SingularitySandbox(base_image=data_singularity_image) as sandbox:
            sandbox.build_image(path=existing_singularity_image_path)

        # Check that the image file has been overwritten
        assert (
            existing_singularity_image_path.stat() != existing_singularity_image_stats
        )

    def test_sandbox_image_equality(self, data_singularity_image, tmp_path):
        built_image_path = tmp_path / "built_image_6021"
        with SingularitySandbox(base_image=data_singularity_image) as sandbox:
            sandbox.build_image(path=built_image_path)

        def get_container_os_release(path):
            process = subprocess.run(
                ["singularity", "exec", f"{path}", "cat", "/etc/os-release"],
                capture_output=True,
                check=True,
                text=True,
            )
            return process.stdout

        # Simple test of equality based on OS release of base image and built container
        assert get_container_os_release(
            data_singularity_image
        ) == get_container_os_release(built_image_path)


@pytest.mark.singularity_integration
class TestRunCommandInContainer:
    def test_error_handling(self, data_singularity_image):
        cmd = "some6021 non-meaningful command"
        with SingularitySandbox(base_image=data_singularity_image) as sandbox:
            with pytest.raises(ValueError) as exc_info:
                sandbox.run_command_in_container(cmd=cmd)
            assert str(exc_info.value).startswith(
                f"Invalid command {cmd=} passed to Singularity"
            )

    def test_no_home(self, data_singularity_image):
        with SingularitySandbox(base_image=data_singularity_image) as sandbox:
            process = sandbox.run_command_in_container(cmd="ls -l /home")
        assert process.stdout.strip() == "total 0"

    def test_writeable(self, data_singularity_image):
        test_file = "test_file_6021"
        with SingularitySandbox(base_image=data_singularity_image) as sandbox:
            sandbox.run_command_in_container(cmd=f"touch /{test_file}")
            assert (sandbox.sandbox_dir / test_file).exists()


class TestAssertWithinSandboxContext:
    def test_pass_inside_sandbox(self):
        sandbox = SingularitySandbox(base_image="my_base_image_6021")
        sandbox.sandbox_dir = Path()
        sandbox._assert_within_sandbox_context()

    def test_fail_outside_sandbox(self):
        sandbox = SingularitySandbox(base_image="my_base_image_6021")
        with pytest.raises(ValueError) as exc_info:
            sandbox._assert_within_sandbox_context()
        assert (
            str(exc_info.value)
            == "The operation is only valid inside a sandbox context."
        )
