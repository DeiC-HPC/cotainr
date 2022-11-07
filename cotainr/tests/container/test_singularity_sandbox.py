import pytest

from cotainr.container import SingularitySandbox


class TestConstructor:
    def test_attributes(self):
        raise NotImplementedError("Test not implemented'")


class TestContext:
    # mock stream_subprocess
    def test_singularity_sandbox_creation(self):
        raise NotImplementedError("Test not implemented'")

    def test_tmp_dir_location(self):
        raise NotImplementedError("Test not implemented'")

    def test_tmp_dir_teardown(self):
        raise NotImplementedError("Test not implemented'")


class TestAddToEnv:
    # mock stream_subprocess
    def test_newline_encapsulation(self):
        raise NotImplementedError("Test not implemented'")

    def test_shell_script_append(self):
        raise NotImplementedError("Test not implemented'")


@pytest.mark.singularity_integration
class TestBuildImage:
    def test_overwrite_existing_image(self):
        raise NotImplementedError("Test not implemented'")

    def test_sandbox_image_equality(self):
        raise NotImplementedError("Test not implemented'")


@pytest.mark.singularity_integration
class TestRunCommandInContainer:
    def test_error_handling(self):
        # test error in cmd
        raise NotImplementedError("Test not implemented'")

    def test_no_home(self):
        # test that no home is present
        raise NotImplementedError("Test not implemented'")

    def test_writeable(self):
        # test that sandbox is writable
        raise NotImplementedError("Test not implemented'")


class TestAssertWithinSandboxContext:
    def test_pass_inside_sandbox(self):
        raise NotImplementedError("Test not implemented'")

    def test_fail_outside_sandbox(self):
        raise NotImplementedError("Test not implemented'")
