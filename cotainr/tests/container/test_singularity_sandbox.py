from cotainr.container import SingularitySandbox


class TestConstructor:
    def test_attributes(self):
        raise NotImplementedError("Test not implemented'")


class TestContext:
    def test_singularity_sandbox_creation(self):
        raise NotImplementedError("Test not implemented'")

    def test_tmp_dir_location(self):
        raise NotImplementedError("Test not implemented'")

    def test_tmp_dir_teardown(self):
        raise NotImplementedError("Test not implemented'")


class TestAddToEnv:
    def test_newline_encapsulation(self):
        raise NotImplementedError("Test not implemented'")

    def test_shell_script_append(self):
        raise NotImplementedError("Test not implemented'")


class TestBuildImage:
    def test_overwrite_existing_image(self):
        raise NotImplementedError("Test not implemented'")

    def test_sandbox_image_equality(self):
        raise NotImplementedError("Test not implemented'")


class TestRunCommandInContainer:
    def test_error_handling(self):
        raise NotImplementedError("Test not implemented'")

    def test_no_home(self):
        raise NotImplementedError("Test not implemented'")

    def test_stdout_passing(self):
        raise NotImplementedError("Test not implemented'")

    def test_stderr_passing(self):
        raise NotImplementedError("Test not implemented'")

    def test_writeable(self):
        raise NotImplementedError("Test not implemented'")


class TestAssertWithinSandboxContext:
    def test_pass_inside_sandbox(self):
        raise NotImplementedError("Test not implemented'")

    def test_fail_outside_sandbox(self):
        raise NotImplementedError("Test not implemented'")
